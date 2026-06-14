"""``grade_pdf`` MCP tool.

Renders the answer PDF to page PNGs, OCRs them in-process via
:mod:`paideia_mcp.ocr` (``qwen3-vl`` with automatic ``tesseract`` fallback, or
``tesseract`` directly), writes ``answers/converted/<stem>.md`` with a
provenance + confidence-tier header, and returns the destination path.

Strategy-grading against the reference solution stays the skill's job; this
tool is strictly the OCR-prep step.
"""

from __future__ import annotations

import datetime
import os
import shutil
import tempfile
from pathlib import Path

from PIL import Image
from pdf2image import convert_from_path

from .ocr import run_ocr
from .phase import parse_meta

_DPI = 200
_MAX_LONG_EDGE = 1800
_DEFAULT_ENGINE = "qwen3-vl"
_ARCHIVE_DIRNAME = "_archive"

_TIER_BY_ENGINE = {
    "qwen3-vl": "medium",
    "tesseract": "low",
}


def _read_course_meta_engine(root: Path) -> str | None:
    """Return the ``OCR_ENGINE`` key from ``.course-meta``, if any."""

    meta = parse_meta(root)
    value = meta.get("OCR_ENGINE")
    if not value:
        return None
    normalized = value.strip().lower()
    # Accept legacy aliases from the Claude/Codex editions. Host-vision engines
    # (claude/openai/codex) don't OCR inside this MCP, so map them onto the
    # in-process default — qwen3-vl, which falls back to tesseract on its own.
    if normalized == "ollama":
        return "qwen3-vl"
    if normalized in {"openai-vision", "claude", "codex-native", "codex"}:
        return "qwen3-vl"
    if normalized in _TIER_BY_ENGINE:
        return normalized
    return None


def _resize_in_place(png_path: Path) -> None:
    """Downscale ``png_path`` if its long edge exceeds the ceiling."""

    with Image.open(png_path) as img:
        width, height = img.size
        if max(width, height) <= _MAX_LONG_EDGE:
            return
        scale = _MAX_LONG_EDGE / max(width, height)
        new_size = (int(width * scale), int(height * scale))
        resized = img.resize(new_size, Image.LANCZOS)
    resized.save(png_path, "PNG", optimize=True)


def _render_pdf(pdf_path: Path, scratch_dir: Path) -> list[Path]:
    """Render the PDF to page PNGs, resized to the long-edge ceiling."""

    scratch_dir.mkdir(parents=True, exist_ok=True)
    images = convert_from_path(str(pdf_path), dpi=_DPI)
    paths: list[Path] = []
    for i, img in enumerate(images, 1):
        out = scratch_dir / f"p{i:02d}.png"
        img.save(out, "PNG", optimize=True)
        _resize_in_place(out)
        paths.append(out)
    return paths


def _resolve_pdf(raw_path: str, root: Path) -> Path:
    """Resolve ``raw_path`` to an absolute PDF under ``root`` or absolute."""

    candidate = Path(raw_path)
    if candidate.is_absolute():
        return candidate.resolve()
    return (root / candidate).resolve()


def _archive_if_under_answers(pdf: Path, root: Path) -> str | None:
    """Move ``pdf`` into ``answers/_archive/<stem>_<ts>.pdf`` when applicable.

    The move only fires when the PDF lives directly under ``<root>/answers/``
    (the common case for `$paideia-grade answers/<stem>.pdf`). Answer PDFs
    dropped from an arbitrary absolute path are left alone — the caller
    chose that path, so it's not our business to relocate it.

    Returns the archived path (relative to ``root`` when possible) on a
    successful move, or ``None`` when no archive happened.
    """

    try:
        rel = pdf.relative_to(root)
    except ValueError:
        return None
    parts = rel.parts
    # Must be answers/<name>.pdf at depth 2 (not inside a subfolder like _archive/).
    if len(parts) != 2 or parts[0] != "answers":
        return None
    archive_dir = root / "answers" / _ARCHIVE_DIRNAME
    archive_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d-%H%M%SZ")
    dest = archive_dir / f"{pdf.stem}_{ts}.pdf"
    if not pdf.exists():
        # Already moved (idempotent re-run) — nothing to do.
        return None
    try:
        shutil.move(str(pdf), str(dest))
    except OSError:
        return None
    try:
        return str(dest.relative_to(root))
    except ValueError:
        return str(dest)


def grade_pdf(
    path: str,
    engine: str | None = None,
    project_root: str | None = None,
) -> dict:
    """OCR-prep an answer PDF.

    Args:
        path: Answer PDF path (absolute or relative to ``project_root``).
        engine: Override the OCR engine; defaults to ``.course-meta``
            ``OCR_ENGINE`` or ``qwen3-vl`` when absent.
        project_root: Project root; defaults to ``os.getcwd()``.

    Returns::

            {
              "mode": "ocr-complete",
              "markdown_path": ".../answers/converted/<stem>.md",
              "tier": "medium|low",
              "engine": "qwen3-vl|tesseract",
              "pages_processed": <int>,
              "source": "...",
            }

        ``engine`` reflects the engine that actually ran — a ``qwen3-vl``
        request comes back as ``tesseract`` (tier ``low``) when Ollama is
        unavailable.
    """

    root = Path(project_root or os.getcwd()).resolve()
    pdf = _resolve_pdf(path, root)
    if not pdf.exists():
        raise FileNotFoundError(f"answer PDF not found: {pdf}")

    selected_engine = engine or _read_course_meta_engine(root) or _DEFAULT_ENGINE
    if selected_engine not in _TIER_BY_ENGINE:
        raise ValueError(
            f"unknown OCR engine '{selected_engine}'. "
            f"Supported: {', '.join(_TIER_BY_ENGINE)}"
        )

    destination = root / "answers" / "converted" / f"{pdf.stem}.md"
    destination.parent.mkdir(parents=True, exist_ok=True)

    try:
        source_rel = str(pdf.relative_to(root))
    except ValueError:
        source_rel = str(pdf)
    ingested_at = datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    scratch = Path(tempfile.mkdtemp(prefix="paideia-grade-"))
    try:
        png_paths = _render_pdf(pdf, scratch)
        pages_md, engine_used = run_ocr(
            selected_engine,
            png_paths,
            project_root=str(root),
        )
    finally:
        for child in scratch.glob("*"):
            try:
                child.unlink()
            except OSError:
                pass
        try:
            scratch.rmdir()
        except OSError:
            pass

    tier = _TIER_BY_ENGINE[engine_used]
    header = (
        "# Vision-OCR transcription\n\n"
        f"<!-- source: {source_rel} -->\n"
        f"<!-- engine: {engine_used} -->\n"
        f"<!-- tier: {tier} -->\n"
        f"<!-- pages: {len(png_paths)} -->\n"
        f"<!-- ingested: {ingested_at} -->\n\n"
    )
    body_parts: list[str] = []
    for i, page_md in enumerate(pages_md, 1):
        body_parts.append(f"## Page {i}\n\n{(page_md or '').strip()}\n")
    destination.write_text(header + "\n".join(body_parts), encoding="utf-8")

    archived_to = _archive_if_under_answers(pdf, root)
    return {
        "mode": "ocr-complete",
        "markdown_path": str(destination),
        "tier": tier,
        "engine": engine_used,
        "pages_processed": len(png_paths),
        "source": source_rel,
        "archived_to": archived_to,
    }


__all__ = ["grade_pdf"]
