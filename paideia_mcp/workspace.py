"""Local PAIDEIA course workspace operations.

This module is intentionally model-agnostic. Alt's local model can decide what
to write, while these helpers enforce the PAIDEIA folder contract and make file
edits safe, auditable, and reusable from MCP tools.
"""

from __future__ import annotations

import datetime as _dt
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any


DIRS = [
    "materials/lectures",
    "materials/textbook",
    "materials/homework",
    "materials/solutions",
    "converted/lectures",
    "converted/textbook",
    "converted/homework",
    "converted/solutions",
    "course-index",
    "quizzes",
    "mock",
    "twins",
    "chain",
    "derivations",
    "cheatsheet",
    "weakmap",
    "answers/converted",
    "errors",
]


ERRORS_LOG_SEED = """# Error log

<!-- Append-only YAML entries. Canonical schema:

- problem_id: <id>
  pattern:    <Pk>
  error_type: pattern-missed | wrong-variable | wrong-end-form | algebraic | sign | definition
  summary:    "<1 line>"
  source:     answers/converted/<stem>.md | blind/<id> | mock/<ts>.md
  date:       <ISO8601>

The `source:` field drives phase detection. Any source containing `mock`
advances the course to the `mock` phase.
-->
"""


GITIGNORE = """.codex/cache/
.paideia-cache/
answers/.paideia-cache/
answers/*.pdf
answers/**/*.pdf
cheatsheet/final.pdf
.DS_Store
*.pyc
__pycache__/
"""


AGENTS_TEMPLATE = """# PAIDEIA course workspace

Course: $COURSE_NAME
Exam date: $EXAM_DATE
Exam type: $EXAM_TYPE
Weak zones: $WEAK_ZONES
OCR engine: $OCR_ENGINE

This folder is a PAIDEIA study graph. Keep durable learning artifacts as plain
markdown, and preserve append-only history for `errors/log.md` and `weakmap/`.

Core rule: HW density is the primary exam-probability signal. Lecture emphasis
from Alt/Exam Radar is a second signal that annotates and flags divergences; it
does not silently overwrite the HW-derived tier.
"""


VALID_ENGINES = {"codex-native", "qwen3-vl", "tesseract"}
ALLOWED_TOP_LEVEL = {
    ".course-meta",
    "AGENTS.md",
    ".gitignore",
    "materials",
    "converted",
    "course-index",
    "quizzes",
    "mock",
    "twins",
    "chain",
    "derivations",
    "cheatsheet",
    "weakmap",
    "answers",
    "errors",
}


def resolve_root(project_root: str | None = None) -> Path:
    """Return an absolute course root."""

    return Path(project_root or os.getcwd()).expanduser().resolve()


def _safe_join(root: Path, rel_path: str) -> Path:
    """Join ``rel_path`` under ``root`` and reject traversal/unknown tops."""

    if not rel_path or rel_path.strip() in {".", ""}:
        raise ValueError("path must be a non-empty relative path")
    candidate = Path(rel_path)
    if candidate.is_absolute():
        raise ValueError("path must be relative to project_root")
    parts = candidate.parts
    if parts[0] not in ALLOWED_TOP_LEVEL:
        raise ValueError(
            f"path must start with one of {sorted(ALLOWED_TOP_LEVEL)}, got {parts[0]!r}"
        )
    target = (root / candidate).resolve()
    if root != target and root not in target.parents:
        raise ValueError("path escapes project_root")
    return target


def _now() -> str:
    return _dt.datetime.now().replace(microsecond=0).isoformat()


def _timestamp() -> str:
    return _dt.datetime.now().strftime("%Y-%m-%d_%H%M")


def _slug(value: str, fallback: str = "artifact") -> str:
    """ASCII filesystem slug with a stable fallback."""

    text = value.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:80] or fallback


def _top_up_gitignore(root: Path) -> str:
    path = root / ".gitignore"
    if not path.exists():
        path.write_text(GITIGNORE, encoding="utf-8")
        return "write"
    existing = path.read_text(encoding="utf-8", errors="replace")
    lines = existing.splitlines()
    changed = False
    for line in GITIGNORE.splitlines():
        if line and line not in lines:
            lines.append(line)
            changed = True
    if changed:
        path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
        return "merge"
    return "skip"


def init_course(
    project_root: str,
    course_name: str,
    exam_date: str,
    exam_type: str = "exam",
    weak_zones: str = "unknown",
    ocr_engine: str = "codex-native",
    git_init: bool = True,
) -> dict[str, Any]:
    """Create the PAIDEIA folder skeleton and seed core files."""

    if ocr_engine not in VALID_ENGINES:
        raise ValueError(f"ocr_engine must be one of {sorted(VALID_ENGINES)}")
    root = resolve_root(project_root)
    root.mkdir(parents=True, exist_ok=True)
    made_dirs: list[str] = []
    for rel in DIRS:
        path = root / rel
        before = path.exists()
        path.mkdir(parents=True, exist_ok=True)
        if not before:
            made_dirs.append(rel)

    log_path = root / "errors" / "log.md"
    wrote_log = False
    if not log_path.exists():
        log_path.write_text(ERRORS_LOG_SEED, encoding="utf-8")
        wrote_log = True

    meta = (
        f"COURSE_NAME: {course_name}\n"
        f"EXAM_DATE: {exam_date}\n"
        f"EXAM_TYPE: {exam_type}\n"
        f"USER_WEAK_ZONES: {weak_zones}\n"
        f"OCR_ENGINE: {ocr_engine}\n"
    )
    (root / ".course-meta").write_text(meta, encoding="utf-8")

    agents = (
        AGENTS_TEMPLATE.replace("$COURSE_NAME", course_name)
        .replace("$EXAM_DATE", exam_date)
        .replace("$EXAM_TYPE", exam_type)
        .replace("$WEAK_ZONES", weak_zones)
        .replace("$OCR_ENGINE", ocr_engine)
    )
    agents_path = root / "AGENTS.md"
    wrote_agents = False
    if not agents_path.exists():
        agents_path.write_text(agents, encoding="utf-8")
        wrote_agents = True

    gitignore_action = _top_up_gitignore(root)
    git_action = "skip"
    if git_init and not (root / ".git").exists() and shutil.which("git"):
        subprocess.run(["git", "init", "-q"], cwd=root, check=False)
        git_action = "init" if (root / ".git").exists() else "failed"

    return {
        "project_root": str(root),
        "created_dirs": made_dirs,
        "wrote_errors_log": wrote_log,
        "wrote_agents_md": wrote_agents,
        "gitignore": gitignore_action,
        "git": git_action,
    }


def list_artifacts(project_root: str | None = None, glob_pattern: str = "**/*.md") -> dict[str, Any]:
    """List markdown-ish artifacts under the PAIDEIA-managed directories."""

    root = resolve_root(project_root)
    allowed_dirs = [
        "materials",
        "converted",
        "course-index",
        "quizzes",
        "mock",
        "twins",
        "chain",
        "derivations",
        "cheatsheet",
        "weakmap",
        "answers",
        "errors",
    ]
    files: list[dict[str, Any]] = []
    for top in allowed_dirs:
        base = root / top
        if not base.exists():
            continue
        for path in sorted(base.glob(glob_pattern)):
            if path.is_file():
                stat = path.stat()
                files.append(
                    {
                        "path": str(path.relative_to(root)),
                        "size": stat.st_size,
                        "mtime": int(stat.st_mtime),
                    }
                )
    return {"project_root": str(root), "files": files}


def read_artifact(
    project_root: str | None,
    path: str,
    max_chars: int = 20000,
) -> dict[str, Any]:
    """Read one course artifact with a size cap."""

    root = resolve_root(project_root)
    target = _safe_join(root, path)
    text = target.read_text(encoding="utf-8", errors="replace")
    truncated = len(text) > max_chars
    return {
        "project_root": str(root),
        "path": str(target.relative_to(root)),
        "text": text[:max_chars],
        "truncated": truncated,
        "size": len(text),
    }


def write_artifact(
    project_root: str | None,
    path: str,
    content: str,
    mode: str = "overwrite",
    create_parent: bool = True,
) -> dict[str, Any]:
    """Write or append a text artifact under the PAIDEIA course root."""

    if mode not in {"overwrite", "append", "create"}:
        raise ValueError("mode must be overwrite, append, or create")
    root = resolve_root(project_root)
    target = _safe_join(root, path)
    if create_parent:
        target.parent.mkdir(parents=True, exist_ok=True)
    if mode == "create" and target.exists():
        raise FileExistsError(f"{path} already exists")
    if mode == "append":
        with target.open("a", encoding="utf-8") as f:
            f.write(content)
    else:
        target.write_text(content, encoding="utf-8")
    return {
        "project_root": str(root),
        "path": str(target.relative_to(root)),
        "mode": mode,
        "bytes": target.stat().st_size,
    }


def import_alt_note(
    project_root: str | None,
    title: str,
    transcript: str,
    note_id: str | int | None = None,
    memo: str = "",
    summary: str = "",
    category: str = "lectures",
    write_converted: bool = True,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Import one Alt note/transcript into the PAIDEIA course folder.

    Alt's plugin SDK can read note content inside Alt, but this standalone MCP
    server cannot see Alt's private database by itself. The Alt host/model
    passes the active note title/transcript into this tool, and the tool makes
    it a durable PAIDEIA source artifact.
    """

    if category not in {"lectures", "textbook", "homework", "solutions"}:
        raise ValueError("category must be lectures, textbook, homework, or solutions")
    root = resolve_root(project_root)
    root.joinpath("materials", category).mkdir(parents=True, exist_ok=True)
    root.joinpath("converted", category).mkdir(parents=True, exist_ok=True)
    suffix = f"-{note_id}" if note_id not in {None, ""} else ""
    slug = _slug(f"{title}{suffix}", "alt-note")
    body = (
        f"<!-- SOURCE: Alt note, note_id={note_id or 'unknown'}, imported {_now()} -->\n"
        f"# {title}\n\n"
    )
    if summary.strip():
        body += f"## Alt summary\n\n{summary.strip()}\n\n"
    if memo.strip():
        body += f"## Alt memo\n\n{memo.strip()}\n\n"
    body += f"## Transcript\n\n{transcript.strip()}\n"

    material_path = root / "materials" / category / f"{slug}.md"
    if material_path.exists() and not overwrite:
        raise FileExistsError(f"{material_path.relative_to(root)} already exists")
    material_path.write_text(body, encoding="utf-8")

    converted_rel = None
    if write_converted:
        converted_body = (
            f"<!-- GENERATED FROM: materials/{category}/{slug}.md; Alt transcript already text -->\n\n"
            + body
        )
        converted_path = root / "converted" / category / f"{slug}.md"
        if converted_path.exists() and not overwrite:
            raise FileExistsError(f"{converted_path.relative_to(root)} already exists")
        converted_path.write_text(converted_body, encoding="utf-8")
        converted_rel = str(converted_path.relative_to(root))

    return {
        "project_root": str(root),
        "material_path": str(material_path.relative_to(root)),
        "converted_path": converted_rel,
        "title": title,
        "note_id": note_id,
        "category": category,
    }


def import_alt_notes(
    project_root: str | None,
    notes: list[dict[str, Any]],
    category: str = "lectures",
    write_converted: bool = True,
    overwrite: bool = False,
    continue_on_error: bool = True,
) -> dict[str, Any]:
    """Import multiple Alt note payloads into a PAIDEIA course folder.

    This is the natural handoff shape for Alt SDK clients:
    ``alt.notes.list`` selects note ids, ``alt.notes.getContent`` returns
    title/transcript/memo/summary, and the host/local model forwards that array
    to MCP in one call.
    """

    imported: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for i, note in enumerate(notes):
        title = str(note.get("title") or f"Alt note {note.get('note_id') or i + 1}")
        transcript = str(note.get("transcript") or "")
        note_id = note.get("note_id", note.get("noteId", note.get("id")))
        try:
            imported.append(
                import_alt_note(
                    project_root=project_root,
                    title=title,
                    transcript=transcript,
                    note_id=note_id,
                    memo=str(note.get("memo") or ""),
                    summary=str(note.get("summary") or ""),
                    category=str(note.get("category") or category),
                    write_converted=write_converted,
                    overwrite=overwrite,
                )
            )
        except Exception as exc:  # noqa: BLE001 - batch import should report per-note failures
            errors.append(
                {
                    "index": i,
                    "note_id": note_id,
                    "title": title,
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
            if not continue_on_error:
                break

    root = resolve_root(project_root)
    return {
        "project_root": str(root),
        "imported_count": len(imported),
        "error_count": len(errors),
        "imported": imported,
        "errors": errors,
    }


def bootstrap_alt_course(
    project_root: str,
    course_name: str,
    exam_date: str,
    notes: list[dict[str, Any]] | None = None,
    exam_type: str = "exam",
    weak_zones: str = "unknown",
    ocr_engine: str = "codex-native",
    git_init: bool = True,
    category: str = "lectures",
    write_converted: bool = True,
    overwrite_notes: bool = False,
    continue_on_error: bool = True,
) -> dict[str, Any]:
    """Initialize a course folder and import an initial batch of Alt notes."""

    init = init_course(
        project_root=project_root,
        course_name=course_name,
        exam_date=exam_date,
        exam_type=exam_type,
        weak_zones=weak_zones,
        ocr_engine=ocr_engine,
        git_init=git_init,
    )
    imported = import_alt_notes(
        project_root=project_root,
        notes=notes or [],
        category=category,
        write_converted=write_converted,
        overwrite=overwrite_notes,
        continue_on_error=continue_on_error,
    )
    return {
        "project_root": init["project_root"],
        "init": init,
        "notes": imported,
    }


def save_action_artifact(
    project_root: str | None,
    action: str,
    content: str,
    answer_content: str | None = None,
    slug: str | None = None,
    target_path: str | None = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Save a generated PAIDEIA action result to its standard location.

    Use this after ``prepare_paideia_action`` when Alt's local model has drafted
    the markdown. It handles standard paired answer/solution filenames so the
    course folder remains compatible with the Claude/Codex/opencode editions.
    """

    root = resolve_root(project_root)
    action_name = action.removeprefix("paideia-")
    ts = _timestamp()
    base = _slug(slug or action_name, action_name)
    primary_rel: str
    sibling_rel: str | None = None

    if target_path:
        primary_rel = target_path
    elif action_name == "quiz":
        primary_rel = f"quizzes/{base}_{ts}.md"
        sibling_rel = f"quizzes/{base}_{ts}_answers.md"
    elif action_name == "twin":
        primary_rel = f"twins/{base}_{ts}.md"
        sibling_rel = f"twins/{base}_{ts}_answers.md"
    elif action_name == "chain":
        primary_rel = f"chain/chain_{ts}.md"
        sibling_rel = f"chain/chain_{ts}_answers.md"
    elif action_name == "mock":
        primary_rel = f"mock/mock_{ts}.md"
        sibling_rel = f"mock/mock_{ts}_sol.md"
    elif action_name == "derive":
        primary_rel = f"derivations/{base}.md"
    elif action_name == "cheatsheet":
        primary_rel = "cheatsheet/final.md"
    elif action_name == "weakmap":
        primary_rel = f"weakmap/weakmap_{ts}.md"
    elif action_name == "grade":
        primary_rel = f"answers/converted/{base}.md"
    elif action_name == "analyze":
        raise ValueError(
            "analyze writes multiple files; use target_path for summary.md, patterns.md, or coverage.md"
        )
    else:
        primary_rel = f"{action_name}/{base}_{ts}.md"

    primary = _safe_join(root, primary_rel)
    primary.parent.mkdir(parents=True, exist_ok=True)
    if primary.exists() and not overwrite:
        raise FileExistsError(f"{primary_rel} already exists")
    primary.write_text(content, encoding="utf-8")

    sibling_written = None
    if answer_content is not None and sibling_rel is not None:
        sibling = _safe_join(root, sibling_rel)
        sibling.parent.mkdir(parents=True, exist_ok=True)
        if sibling.exists() and not overwrite:
            raise FileExistsError(f"{sibling_rel} already exists")
        sibling.write_text(answer_content, encoding="utf-8")
        sibling_written = str(sibling.relative_to(root))

    return {
        "project_root": str(root),
        "action": action_name,
        "path": str(primary.relative_to(root)),
        "sibling_path": sibling_written,
    }


def save_course_index(
    project_root: str | None,
    summary_md: str,
    patterns_md: str,
    coverage_md: str,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Save the three canonical ``analyze`` outputs in one atomic-feeling call.

    Alt's local model often generates ``summary.md``, ``patterns.md``, and
    ``coverage.md`` together after reading converted materials. A typed writer
    keeps those files in the expected PAIDEIA locations without asking the
    model to remember three separate relative paths.
    """

    root = resolve_root(project_root)
    outputs = {
        "course-index/summary.md": summary_md,
        "course-index/patterns.md": patterns_md,
        "course-index/coverage.md": coverage_md,
    }
    existing = [path for path in outputs if (root / path).exists()]
    if existing and not overwrite:
        raise FileExistsError(
            "course-index files already exist; pass overwrite=True to replace: "
            + ", ".join(existing)
        )

    written: list[dict[str, Any]] = []
    for rel, content in outputs.items():
        target = _safe_join(root, rel)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        written.append({"path": rel, "bytes": target.stat().st_size})

    return {
        "project_root": str(root),
        "paths": [item["path"] for item in written],
        "files": written,
    }


def save_grade_report(
    project_root: str | None,
    slug: str,
    report_md: str,
    errors: list[dict[str, str]] | None = None,
    source: str | None = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Save a model-generated grading report and append canonical errors.

    ``grade_pdf`` handles OCR/rasterization. This helper covers the second half
    of PAIDEIA grading for Alt-local flows: the model compares the attempt with
    reference material, writes a durable report, and records mistakes that will
    feed weakmaps and cheatsheets.
    """

    root = resolve_root(project_root)
    base = _slug(slug, "grade-report")
    rel = f"answers/converted/{base}.md"
    target = _safe_join(root, rel)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and not overwrite:
        raise FileExistsError(f"{rel} already exists")
    target.write_text(report_md, encoding="utf-8")

    appended: list[dict[str, Any]] = []
    for i, error in enumerate(errors or [], 1):
        problem_id = error.get("problem_id") or f"{base}-e{i}"
        entry_source = error.get("source") or source or rel
        appended.append(
            append_error(
                str(root),
                problem_id=problem_id,
                pattern=error["pattern"],
                error_type=error["error_type"],
                summary=error["summary"],
                source=entry_source,
                date=error.get("date"),
            )
        )

    return {
        "project_root": str(root),
        "path": rel,
        "errors_appended": len(appended),
        "error_log_path": "errors/log.md" if appended else None,
    }


def append_error(
    project_root: str | None,
    problem_id: str,
    pattern: str,
    error_type: str,
    summary: str,
    source: str,
    date: str | None = None,
) -> dict[str, Any]:
    """Append one canonical PAIDEIA error-log entry."""

    if not re.fullmatch(r"P\d+", pattern):
        raise ValueError("pattern must look like P<number>")
    if error_type not in {
        "pattern-missed",
        "wrong-variable",
        "wrong-end-form",
        "algebraic",
        "sign",
        "definition",
    }:
        raise ValueError("invalid error_type")
    root = resolve_root(project_root)
    log = root / "errors" / "log.md"
    log.parent.mkdir(parents=True, exist_ok=True)
    if not log.exists():
        log.write_text(ERRORS_LOG_SEED, encoding="utf-8")
    entry = (
        f"\n- problem_id: {problem_id}\n"
        f"  pattern:    {pattern}\n"
        f"  error_type: {error_type}\n"
        f"  summary:    \"{summary.replace(chr(34), chr(39))}\"\n"
        f"  source:     {source}\n"
        f"  date:       {date or _now()}\n"
    )
    with log.open("a", encoding="utf-8") as f:
        f.write(entry)
    return {"project_root": str(root), "path": "errors/log.md", "entry": entry}


def newest_weakmap_path(project_root: str | None = None) -> Path | None:
    root = resolve_root(project_root)
    weakmaps = sorted(
        (root / "weakmap").glob("weakmap_*.md"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return weakmaps[0] if weakmaps else None


def next_timestamped_path(project_root: str | None, folder: str, stem: str) -> Path:
    root = resolve_root(project_root)
    target = _safe_join(root, f"{folder}/{stem}_{_timestamp()}.md")
    target.parent.mkdir(parents=True, exist_ok=True)
    return target
