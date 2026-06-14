"""Readiness diagnostics for PAIDEIA MCP and local course folders."""

from __future__ import annotations

import glob
import importlib.metadata
import shutil
from pathlib import Path
from typing import Any

from .alt_manifest import MCP_TOOLS
from .bootstrap import missing_imports
from .prompts import list_prompt_specs
from .repo_parser import ACTION_REQUIRED_ARTIFACTS, CANONICAL_ACTIONS, parse_paideia_repo
from .workspace import DIRS, list_artifacts, resolve_root


def _package_version() -> str:
    try:
        return importlib.metadata.version("paideia-mcp")
    except importlib.metadata.PackageNotFoundError:
        return "source-tree"


def _exists_for_spec(root: Path, spec: str) -> dict[str, Any]:
    """Return best-effort existence info for an action prerequisite spec."""

    if " or " in spec:
        parts = [part.strip() for part in spec.split(" or ") if part.strip()]
        choices = [_exists_for_spec(root, part) for part in parts]
        return {
            "spec": spec,
            "exists": any(choice["exists"] for choice in choices),
            "choices": choices,
        }

    if "*" in spec:
        matches = sorted(glob.glob(str(root / spec), recursive=True))
        file_matches = [Path(path) for path in matches if Path(path).is_file()]
        rels = [str(path.resolve().relative_to(root)) for path in file_matches[:10]]
        return {
            "spec": spec,
            "exists": bool(file_matches),
            "matches": rels,
            "count": len(file_matches),
            "truncated": len(file_matches) > 10,
        }

    path = root / spec
    return {
        "spec": spec,
        "exists": path.exists(),
        "path": spec,
    }


def _artifact_counts(root: Path) -> dict[str, int]:
    tops = [
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
    counts: dict[str, int] = {}
    for top in tops:
        base = root / top
        counts[top] = len([path for path in base.rglob("*") if path.is_file()]) if base.exists() else 0
    return counts


def _recommendations(root: Path, initialized: bool, counts: dict[str, int]) -> list[str]:
    recs: list[str] = []
    if not initialized:
        recs.append("Call bootstrap_alt_course for a new Alt course, or init_course for an empty PAIDEIA folder.")
        return recs
    if counts.get("converted", 0) == 0:
        recs.append("Import Alt transcripts with import_alt_notes, or add PDFs under materials/ and call ingest_pdfs.")
    if not (root / "course-index" / "patterns.md").exists():
        recs.append("Build the course graph with build_course_index or prepare_paideia_action('analyze') plus save_course_index.")
    if (root / "course-index" / "patterns.md").exists() and counts.get("quizzes", 0) == 0:
        recs.append("Generate first practice with prepare_paideia_action('quiz') plus save_action_artifact.")
    if (root / "errors" / "log.md").exists() and counts.get("weakmap", 0) == 0:
        recs.append("Generate a weakness snapshot with generate_weakmap.")
    return recs


def paideia_doctor(
    project_root: str | None = None,
    repo_root: str | None = None,
) -> dict[str, Any]:
    """Return installation, MCP, and course-folder readiness diagnostics."""

    root = resolve_root(project_root)
    missing = missing_imports()
    dirs = {rel: (root / rel).is_dir() for rel in DIRS}
    initialized = (root / ".course-meta").is_file() and (root / "errors" / "log.md").is_file()
    counts = _artifact_counts(root)
    artifacts = list_artifacts(str(root), "**/*.md")["files"] if root.exists() else []

    action_readiness = []
    for name in CANONICAL_ACTIONS:
        checks = [_exists_for_spec(root, spec) for spec in ACTION_REQUIRED_ARTIFACTS.get(name, [])]
        ready = initialized and all(check["exists"] for check in checks)
        if name == "init-course":
            ready = True
        action_readiness.append(
            {
                "action": name,
                "ready": ready,
                "missing": [check["spec"] for check in checks if not check["exists"]],
                "checks": checks,
            }
        )

    catalog = parse_paideia_repo(repo_root)
    external = {
        "python": shutil.which("python3") or shutil.which("python"),
        "git": shutil.which("git"),
        "pdftoppm": shutil.which("pdftoppm"),
        "tesseract": shutil.which("tesseract"),
        "ollama": shutil.which("ollama"),
    }
    status = "ready"
    if missing:
        status = "missing-python-deps"
    elif not initialized:
        status = "course-not-initialized"
    elif not (root / "course-index" / "patterns.md").exists():
        status = "needs-analysis"

    return {
        "schema": "paideia-doctor:v1",
        "status": status,
        "package_version": _package_version(),
        "project_root": str(root),
        "repo_root": catalog["repo_root"],
        "python_missing_imports": missing,
        "external_dependencies": external,
        "mcp": {
            "tools": MCP_TOOLS,
            "tool_count": len(MCP_TOOLS),
            "prompts": [spec["name"] for spec in list_prompt_specs()],
            "resources": ["paideia://alt/manifest", "paideia://alt/system-prompt"],
        },
        "course": {
            "exists": root.exists(),
            "initialized": initialized,
            "dirs": dirs,
            "artifact_counts": counts,
            "markdown_artifacts": len(artifacts),
        },
        "actions": action_readiness,
        "recommendations": _recommendations(root, initialized, counts),
    }
