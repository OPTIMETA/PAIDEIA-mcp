"""Small deterministic PAIDEIA study tools for MCP clients."""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .workspace import next_timestamped_path, resolve_root


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def _strip_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def pattern_lookup(
    project_root: str | None = None,
    query: str = "",
    max_chars: int = 16000,
) -> dict[str, Any]:
    """Filter course-index/patterns.md by Pk label or keyword."""

    root = resolve_root(project_root)
    path = root / "course-index" / "patterns.md"
    text = _read(path)
    if not text:
        return {"error": "course-index/patterns.md missing", "matches": []}
    blocks = re.split(r"(?m)^(?=##\s+|###\s+|\bP\d+\b)", text)
    q = query.strip().lower()
    if not q:
        hits = blocks[:10]
    else:
        hits = [b for b in blocks if q in b.lower()]
    body = "\n\n".join(h.strip() for h in hits if h.strip())
    return {
        "project_root": str(root),
        "path": "course-index/patterns.md",
        "query": query,
        "matches": len(hits),
        "text": body[:max_chars],
        "truncated": len(body) > max_chars,
    }


def hwmap(project_root: str | None = None, mode: str = "hot") -> dict[str, Any]:
    """Return HW-density tiers from course-index/coverage.md."""

    root = resolve_root(project_root)
    path = root / "course-index" / "coverage.md"
    text = _read(path)
    if not text:
        return {"error": "course-index/coverage.md missing", "items": []}
    rows: list[dict[str, str]] = []
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        if "---" in line or "Exam tier" in line or "시험" in line and "tier" in line.lower():
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        joined = " ".join(cells)
        tier = None
        if "🔥🔥" in joined or "Exam-primary" in joined:
            tier = "primary"
        elif "🔥" in joined or "Exam-likely" in joined:
            tier = "likely"
        elif "🟡" in joined or "possible" in joined.lower():
            tier = "possible"
        elif "⚪" in joined or "low-risk" in joined.lower():
            tier = "low"
        if tier:
            rows.append({"tier": tier, "cells": cells, "raw": line})
    if mode in {"hot", "primary", "exam"}:
        rows = [r for r in rows if r["tier"] in {"primary", "likely"}]
    elif mode in {"low", "drop"}:
        rows = [r for r in rows if r["tier"] == "low"]
    return {"project_root": str(root), "path": "course-index/coverage.md", "mode": mode, "items": rows}


def _parse_errors(text: str) -> list[dict[str, str]]:
    text = _strip_comments(text)
    chunks = re.split(r"(?m)^\s*-\s+problem_id:\s*", text)
    entries: list[dict[str, str]] = []
    for chunk in chunks[1:]:
        first, _, rest = chunk.partition("\n")
        entry = {"problem_id": first.strip()}
        for key in ["pattern", "error_type", "summary", "source", "date"]:
            match = re.search(rf"(?m)^\s*{key}:\s*(.+?)\s*$", rest)
            if match:
                entry[key] = match.group(1).strip().strip('"')
        if "pattern" in entry:
            entries.append(entry)
    return entries


def generate_weakmap(project_root: str | None = None, concept: str = "") -> dict[str, Any]:
    """Generate a compact weakmap from errors/log.md plus an optional concept."""

    root = resolve_root(project_root)
    entries = _parse_errors(_read(root / "errors" / "log.md"))
    by_pattern: dict[str, list[dict[str, str]]] = defaultdict(list)
    for entry in entries:
        by_pattern[entry["pattern"]].append(entry)
    counts = Counter({p: len(v) for p, v in by_pattern.items()})
    lines = ["# Weakmap", "", "## Highest-priority misses", ""]
    if counts:
        for pattern, count in counts.most_common():
            latest = by_pattern[pattern][-1]
            lines.append(f"- {pattern} ({count}x) - latest: {latest.get('summary', '(no summary)')}")
    else:
        lines.append("- No graded errors yet.")
    if concept.strip():
        lines.extend(["", "## User-declared weaknesses", "", f"- {concept.strip()}"])
    lines.extend(
        [
            "",
            "## Next drill",
            "",
            "- Use `prepare_paideia_action` for `quiz weakmap`, `blind <problem>`, or `twin <problem>`.",
            "- Keep new failed attempts in `errors/log.md` with `append_error`.",
        ]
    )
    target = next_timestamped_path(str(root), "weakmap", "weakmap")
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {
        "project_root": str(root),
        "path": str(target.relative_to(root)),
        "patterns": counts.most_common(),
        "concept": concept or None,
    }

