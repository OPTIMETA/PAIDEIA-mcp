"""Prompt/action composition for Alt local models using PAIDEIA via MCP."""

from __future__ import annotations

import glob
from pathlib import Path
from typing import Any

from .repo_parser import get_action, parse_paideia_repo
from .workspace import list_artifacts, read_artifact, resolve_root


DIRECT_READ_LIMIT = 12000
MAX_GLOB_ITEMS = 20


def list_paideia_actions(repo_root: str | None = None) -> dict[str, Any]:
    """Return the parsed PAIDEIA action catalog."""

    return parse_paideia_repo(repo_root)


def _artifact_status(root: Path, spec: str) -> dict[str, Any]:
    """Summarize one required artifact spec."""

    if "*" in spec:
        matches = sorted(glob.glob(str(root / spec), recursive=True))
        rels = [str(Path(m).resolve().relative_to(root)) for m in matches[:MAX_GLOB_ITEMS]]
        return {
            "spec": spec,
            "exists": bool(matches),
            "matches": rels,
            "truncated": len(matches) > MAX_GLOB_ITEMS,
            "count": len(matches),
        }
    path = root / spec
    return {"spec": spec, "exists": path.exists(), "path": spec}


def _read_direct_context(root: Path, specs: list[str]) -> list[dict[str, Any]]:
    """Read direct markdown/text specs, inventory wildcards."""

    out: list[dict[str, Any]] = []
    for spec in specs:
        if "*" in spec or " or " in spec or " " in spec and "/" not in spec:
            out.append(_artifact_status(root, spec))
            continue
        path = root / spec
        if path.exists() and path.is_file():
            try:
                out.append(read_artifact(str(root), spec, max_chars=DIRECT_READ_LIMIT))
            except Exception as exc:  # noqa: BLE001 - context should be best-effort
                out.append({"spec": spec, "exists": True, "error": str(exc)})
        else:
            out.append(_artifact_status(root, spec))
    return out


def prepare_paideia_action(
    action: str,
    project_root: str | None = None,
    args: str = "",
    repo_root: str | None = None,
    include_instruction: bool = True,
) -> dict[str, Any]:
    """Compose the instruction/context Alt should give its local model.

    The result is deliberately not an opaque command runner. It gives the model
    the original PAIDEIA action recipe, the local artifact contract, current
    workspace evidence, and the exact MCP file-writing tools it should call
    after drafting markdown.
    """

    root = resolve_root(project_root)
    spec = get_action(action, repo_root)
    required_context = _read_direct_context(root, spec.required_artifacts)
    inventory = list_artifacts(str(root), "**/*.md")
    prompt = f"""You are running PAIDEIA inside Alt via a local MCP server.

Action: {spec.name}
User args: {args or "(none)"}
Course root: {root}

Follow the PAIDEIA philosophy:
- Build durable, editable markdown artifacts in the local course folder.
- HW density remains the primary exam-probability signal.
- Alt/Exam Radar lecture emphasis is a second signal; annotate divergences,
  never silently overwrite HW tiering.
- Preserve append-only learning history for errors/log.md and weakmap/.
- For attempt-first drills, ask for the learner's strategy before revealing or
  using a solution.

When you need to write a standard PAIDEIA action output, prefer
`save_action_artifact` so paired answer/solution files land in the canonical
folder. Use `write_artifact` for explicit target paths such as
`course-index/summary.md`.
For analyze, prefer `save_course_index` after drafting summary/patterns/coverage
together. For grade, prefer `save_grade_report` when you have both the written
feedback and the mistake entries to append.
When a failed/revised attempt should affect future study, call `append_error`.
Do not invent files outside the listed output hints.
"""
    if include_instruction:
        prompt += "\n\n# Original PAIDEIA action instruction\n\n" + spec.instruction

    return {
        "action": spec.to_dict(include_instruction=include_instruction),
        "project_root": str(root),
        "args": args,
        "model_prompt": prompt,
        "required_context": required_context,
        "artifact_inventory": inventory["files"],
        "write_tools": [
            "save_action_artifact",
            "save_course_index",
            "save_grade_report",
            "write_artifact",
            "append_error",
        ],
    }
