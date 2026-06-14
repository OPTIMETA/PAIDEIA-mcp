"""OCR engine dispatch for paideia-mcp.

Exposes ``run_ocr(engine, png_paths, *, project_root=None) -> (list[str], str)``
which routes to the requested engine module and returns markdown per page plus
the engine that actually produced it.

Two in-process engines are supported, both of which OCR fully inside this MCP
process so the durable course folder is written without any external agent's
vision step:

* ``qwen3-vl`` — local Ollama Qwen3-VL 8B. High fidelity, fully offline. When
  Ollama is unreachable or the model is not pulled, this transparently falls
  back to ``tesseract`` so a default install still produces output; the return
  value's second element records which engine ran.
* ``tesseract`` — pytesseract (``eng`` and/or ``kor``). Lightest, lowest
  fidelity, no model download.
"""

from __future__ import annotations

from pathlib import Path

import httpx

_SUPPORTED = ("qwen3-vl", "tesseract")
_IN_PROCESS = _SUPPORTED

# Errors that mean "Ollama isn't available" rather than "the page is bad",
# and therefore justify the qwen3-vl -> tesseract fallback.
_OLLAMA_UNAVAILABLE = (httpx.HTTPError, ConnectionError, OSError)


def _resolve_course_name(project_root: str | None) -> str | None:
    """Read ``COURSE_NAME`` from ``.course-meta`` under ``project_root``."""

    if not project_root:
        return None
    from ..phase import parse_meta

    meta = parse_meta(Path(project_root))
    value = meta.get("COURSE_NAME", "").strip()
    return value or None


def run_ocr(
    engine: str,
    png_paths: list[Path] | list[str],
    *,
    project_root: str | None = None,
) -> tuple[list[str], str]:
    """Dispatch OCR for a list of PNG paths.

    Args:
        engine: One of ``qwen3-vl`` or ``tesseract``.
        png_paths: Absolute paths (or strings) pointing at rendered PNG pages.
        project_root: Optional project root hint. When set, ``.course-meta``
            ``COURSE_NAME`` is forwarded to engines that parameterize their
            prompt on the course (currently only ``qwen3-vl``).

    Returns:
        ``(pages_md, engine_used)`` — one markdown string per input page in the
        same order, and the engine that actually ran (``qwen3-vl`` requests can
        come back as ``tesseract`` when Ollama is unavailable).

    Raises:
        ValueError: when ``engine`` is unknown.
    """

    if engine not in _SUPPORTED:
        raise ValueError(
            f"unknown OCR engine '{engine}'. Supported: {', '.join(_SUPPORTED)}"
        )

    paths = [Path(p) for p in png_paths]

    if engine == "qwen3-vl":
        from . import qwen3vl

        try:
            pages = qwen3vl.transcribe_pages(
                paths,
                course_name=_resolve_course_name(project_root),
            )
            return pages, "qwen3-vl"
        except _OLLAMA_UNAVAILABLE:
            # Ollama down or model not pulled — degrade to tesseract so the
            # two-engine set stays self-sufficient instead of hard-failing.
            from . import tesseract

            return tesseract.transcribe_pages(paths), "tesseract"

    # tesseract
    from . import tesseract

    return tesseract.transcribe_pages(paths), "tesseract"


__all__ = ["run_ocr", "_SUPPORTED", "_IN_PROCESS"]
