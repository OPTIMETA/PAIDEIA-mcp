"""Parse PAIDEIA plugin repositories into an MCP-usable action catalog."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CANONICAL_ACTIONS: dict[str, str] = {
    "init-course": "Bootstrap a PAIDEIA course folder.",
    "ingest": "Convert materials/** PDFs/markdown into converted/** markdown.",
    "analyze": "Build course-index/summary.md, patterns.md, and coverage.md.",
    "phase": "Show setup/diag/drill/mock/cram/cool phase and top miss.",
    "hwmap": "Surface HW-density exam tiers from course-index/coverage.md.",
    "pattern": "Show pattern cards from course-index/patterns.md.",
    "quiz": "Generate practice problems on a topic, section, weakmap, or all.",
    "twin": "Generate a variant of a known HW/example problem.",
    "blind": "Run attempt-first strategy checking on a known problem.",
    "chain": "Generate an integration problem chaining multiple patterns.",
    "mock": "Generate a full mock exam weighted by HW density.",
    "grade": "OCR and strategy-grade a hand-written answer PDF.",
    "weakmap": "Produce a priority-ranked weakness report.",
    "cheatsheet": "Compile an error-driven one-page cheatsheet.",
    "derive": "Write a clean derivation/reference note for a target.",
    "alt": "Import an OPTIMETA Exam Radar export into the course graph.",
}


ACTION_OUTPUT_HINTS: dict[str, list[str]] = {
    "init-course": [".course-meta", "AGENTS.md", "errors/log.md"],
    "ingest": ["converted/{lectures,textbook,homework,solutions}/*.md"],
    "analyze": ["course-index/summary.md", "course-index/patterns.md", "course-index/coverage.md"],
    "phase": [],
    "hwmap": [],
    "pattern": [],
    "quiz": ["quizzes/<topic>_<ts>.md", "quizzes/<topic>_<ts>_answers.md"],
    "twin": ["twins/<source>_<ts>.md", "twins/<source>_<ts>_answers.md"],
    "blind": ["errors/log.md on failed/revised strategy"],
    "chain": ["chain/chain_<ts>.md", "chain/chain_<ts>_answers.md"],
    "mock": ["mock/mock_<ts>.md", "mock/mock_<ts>_sol.md"],
    "grade": ["answers/converted/<stem>.md", "errors/log.md"],
    "weakmap": ["weakmap/weakmap_<ts>.md"],
    "cheatsheet": ["cheatsheet/final.md", "cheatsheet/final.pdf optionally"],
    "derive": ["derivations/<slug>.md"],
    "alt": ["course-index/radar.md", "course-index/coverage.md", "weakmap/weakmap_<ts>.md"],
}


ACTION_REQUIRED_ARTIFACTS: dict[str, list[str]] = {
    "init-course": [],
    "ingest": ["materials/**"],
    "analyze": ["converted/**"],
    "phase": [".course-meta", "errors/log.md", "weakmap/**", "course-index/patterns.md"],
    "hwmap": ["course-index/coverage.md"],
    "pattern": ["course-index/patterns.md"],
    "quiz": ["course-index/summary.md", "course-index/patterns.md", "course-index/coverage.md"],
    "twin": ["converted/homework/**", "converted/solutions/**", "course-index/patterns.md"],
    "blind": ["converted/homework/** or converted/textbook/**", "course-index/patterns.md"],
    "chain": ["course-index/patterns.md", "course-index/coverage.md"],
    "mock": ["course-index/summary.md", "course-index/patterns.md", "course-index/coverage.md"],
    "grade": ["answers/*.pdf", "course-index/patterns.md"],
    "weakmap": [
        "errors/log.md",
        "course-index/coverage.md",
        "course-index/patterns.md",
        "course-index/summary.md",
    ],
    "cheatsheet": [
        "errors/log.md",
        "course-index/patterns.md",
        "course-index/coverage.md",
        "course-index/summary.md",
    ],
    "derive": ["course-index/summary.md", "converted/textbook/**", "converted/lectures/**"],
    "alt": ["Exam Radar export or materials/radar.md"],
}


@dataclass(frozen=True)
class PaideiaAction:
    """One PAIDEIA action parsed from a repo or built-in fallback."""

    name: str
    description: str
    source: str
    instruction_path: str | None
    instruction: str
    required_artifacts: list[str]
    output_hints: list[str]

    def to_dict(self, include_instruction: bool = False) -> dict[str, Any]:
        data: dict[str, Any] = {
            "name": self.name,
            "description": self.description,
            "source": self.source,
            "instruction_path": self.instruction_path,
            "required_artifacts": self.required_artifacts,
            "output_hints": self.output_hints,
        }
        if include_instruction:
            data["instruction"] = self.instruction
        return data


def _strip_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Parse the tiny YAML frontmatter used by SKILL.md files."""

    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 4)
    if end < 0:
        return {}, text
    raw = text[4:end].strip()
    meta: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip('"').strip("'")
    return meta, text[end + 4 :].lstrip()


def _action_from_skill_dir(path: Path, source: str) -> PaideiaAction | None:
    skill = path / "SKILL.md"
    if not skill.exists():
        return None
    text = skill.read_text(encoding="utf-8", errors="replace")
    meta, body = _strip_frontmatter(text)
    raw_name = meta.get("name") or path.name
    name = raw_name.removeprefix("paideia-")
    description = meta.get("description") or CANONICAL_ACTIONS.get(name, "")
    return PaideiaAction(
        name=name,
        description=description,
        source=source,
        instruction_path=str(skill),
        instruction=body,
        required_artifacts=ACTION_REQUIRED_ARTIFACTS.get(name, []),
        output_hints=ACTION_OUTPUT_HINTS.get(name, []),
    )


def _parse_codex_repo(root: Path) -> list[PaideiaAction]:
    base = root / "plugins" / "paideia" / "skills"
    if not base.exists():
        return []
    actions = []
    for path in sorted(base.iterdir()):
        if not path.is_dir() or not path.name.startswith("paideia-"):
            continue
        action = _action_from_skill_dir(path, "codex-skill")
        if action:
            actions.append(action)
    return actions


def _parse_claude_repo(root: Path) -> list[PaideiaAction]:
    base = root / "plugins" / "paideia" / "skills"
    if not base.exists():
        return []
    mapped = {
        "alt-import": "alt",
        "answer-processing": "grade",
        "course-builder": "analyze",
        "exam-drill": "quiz",
        "pdf": "ingest",
        "vision-ocr": "ingest",
    }
    actions: list[PaideiaAction] = []
    for path in sorted(base.iterdir()):
        if not path.is_dir():
            continue
        action = _action_from_skill_dir(path, "claude-skill")
        if action:
            name = mapped.get(action.name, action.name)
            actions.append(
                PaideiaAction(
                    name=name,
                    description=action.description or CANONICAL_ACTIONS.get(name, ""),
                    source=action.source,
                    instruction_path=action.instruction_path,
                    instruction=action.instruction,
                    required_artifacts=ACTION_REQUIRED_ARTIFACTS.get(name, []),
                    output_hints=ACTION_OUTPUT_HINTS.get(name, []),
                )
            )
    return actions


def _parse_opencode_repo(root: Path) -> list[PaideiaAction]:
    prompts = root / "assets" / "prompts"
    if not prompts.exists():
        return []
    actions: list[PaideiaAction] = []
    for path in sorted(prompts.glob("*.md")):
        name = path.stem
        if name.startswith("_") or name.endswith("_check"):
            continue
        body = path.read_text(encoding="utf-8", errors="replace")
        title = re.search(r"^#\s+Task:\s*(.+)$", body, re.MULTILINE)
        description = title.group(1).strip() if title else CANONICAL_ACTIONS.get(name, "")
        actions.append(
            PaideiaAction(
                name=name,
                description=description,
                source="opencode-prompt",
                instruction_path=str(path),
                instruction=body,
                required_artifacts=ACTION_REQUIRED_ARTIFACTS.get(name, []),
                output_hints=ACTION_OUTPUT_HINTS.get(name, []),
            )
        )
    return actions


def _default_repo_candidates() -> list[Path]:
    env = os.environ.get("PAIDEIA_REPO_ROOT")
    candidates: list[Path] = []
    if env:
        candidates.append(Path(env).expanduser())
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidates.extend(
            [
                parent / "PAIDEIA-codex",
                parent / "PAIDEIA",
                parent / "PAIDEIA-opencode",
                parent / "optimeta" / "PAIDEIA-codex",
                parent / "optimeta" / "PAIDEIA",
                parent / "optimeta" / "PAIDEIA-opencode",
            ]
        )
    return candidates


def _fallback_actions() -> list[PaideiaAction]:
    return [
        PaideiaAction(
            name=name,
            description=desc,
            source="built-in",
            instruction_path=None,
            instruction=(
                f"# PAIDEIA {name}\n\n"
                f"{desc}\n\n"
                "Use the PAIDEIA local artifact contract. Read the required "
                "artifacts first, write only the output hints, and preserve "
                "append-only logs/history."
            ),
            required_artifacts=ACTION_REQUIRED_ARTIFACTS.get(name, []),
            output_hints=ACTION_OUTPUT_HINTS.get(name, []),
        )
        for name, desc in CANONICAL_ACTIONS.items()
    ]


def parse_paideia_repo(repo_root: str | None = None) -> dict[str, Any]:
    """Parse one PAIDEIA repo, or auto-discover a nearby canonical repo."""

    roots = [Path(repo_root).expanduser()] if repo_root else _default_repo_candidates()
    seen: set[str] = set()
    actions: list[PaideiaAction] = []
    used_root: Path | None = None
    for root in roots:
        root = root.resolve()
        if not root.exists() or str(root) in seen:
            continue
        seen.add(str(root))
        parsed = _parse_codex_repo(root) or _parse_claude_repo(root) or _parse_opencode_repo(root)
        if parsed:
            used_root = root
            actions = parsed
            break

    if not actions:
        actions = _fallback_actions()

    by_name: dict[str, PaideiaAction] = {}
    for action in actions:
        by_name[action.name] = action
    # Ensure every canonical action exists even when the source repo is sparse.
    for fallback in _fallback_actions():
        by_name.setdefault(fallback.name, fallback)

    ordered = [by_name[name] for name in CANONICAL_ACTIONS if name in by_name]
    return {
        "repo_root": str(used_root) if used_root else None,
        "actions": [a.to_dict(include_instruction=False) for a in ordered],
        "count": len(ordered),
    }


def get_action(name: str, repo_root: str | None = None) -> PaideiaAction:
    """Return one parsed action with instructions."""

    catalog = parse_paideia_repo(repo_root)
    wanted = name.removeprefix("paideia-")
    for item in catalog["actions"]:
        if item["name"] == wanted:
            if item["instruction_path"]:
                path = Path(item["instruction_path"])
                text = path.read_text(encoding="utf-8", errors="replace")
                _, body = _strip_frontmatter(text)
                return PaideiaAction(
                    name=item["name"],
                    description=item["description"],
                    source=item["source"],
                    instruction_path=item["instruction_path"],
                    instruction=body,
                    required_artifacts=item["required_artifacts"],
                    output_hints=item["output_hints"],
                )
            fallback = next(a for a in _fallback_actions() if a.name == wanted)
            return fallback
    raise KeyError(f"unknown PAIDEIA action: {name}")

