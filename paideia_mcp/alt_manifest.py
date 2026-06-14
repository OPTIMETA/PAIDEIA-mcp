"""Machine-readable Alt local-model manifest for PAIDEIA MCP."""

from __future__ import annotations

from typing import Any

from .prompts import list_prompt_specs, workflow_guide
from .repo_parser import CANONICAL_ACTIONS, parse_paideia_repo


MCP_TOOLS = [
    "ingest_pdfs",
    "grade_pdf",
    "build_course_index",
    "course_phase",
    "init_course",
    "parse_paideia_repo",
    "list_paideia_actions",
    "prepare_paideia_action",
    "list_artifacts",
    "read_artifact",
    "write_artifact",
    "import_alt_note",
    "import_alt_notes",
    "bootstrap_alt_course",
    "save_action_artifact",
    "save_course_index",
    "save_grade_report",
    "append_error",
    "parse_exam_radar_export",
    "import_exam_radar",
    "pattern_lookup",
    "hwmap",
    "generate_weakmap",
    "alt_workflow_guide",
    "alt_capability_manifest",
    "paideia_doctor",
]


ACTION_RECIPES: dict[str, dict[str, Any]] = {
    "init-course": {
        "mode": "deterministic",
        "steps": [
            {"tool": "init_course", "purpose": "Create the local PAIDEIA folder contract."},
            {
                "tool": "bootstrap_alt_course",
                "purpose": "Use instead when Alt is creating a new course and already has initial note transcripts.",
            },
            {"tool": "alt_workflow_guide", "purpose": "Return next-step operating guidance if needed."},
        ],
    },
    "ingest": {
        "mode": "deterministic-or-alt-note-assisted",
        "steps": [
            {
                "tool": "import_alt_notes",
                "purpose": "Preferred when Alt hands over multiple selected notes from alt.notes.getContent.",
            },
            {
                "tool": "import_alt_note",
                "purpose": "Use for one active Alt note/transcript.",
            },
            {
                "tool": "ingest_pdfs",
                "purpose": "When the source is PDFs under materials/**, OCR/render them into converted/**.",
            },
        ],
    },
    "analyze": {
        "mode": "local-model-assisted",
        "steps": [
            {"tool": "prepare_paideia_action", "args": {"action": "analyze"}},
            {"model": "Draft summary_md, patterns_md, and coverage_md from returned context."},
            {"tool": "save_course_index", "purpose": "Write the three course-index files together."},
        ],
    },
    "phase": {
        "mode": "deterministic",
        "steps": [{"tool": "course_phase"}],
    },
    "hwmap": {
        "mode": "deterministic",
        "steps": [{"tool": "hwmap"}],
    },
    "pattern": {
        "mode": "deterministic",
        "steps": [{"tool": "pattern_lookup"}],
    },
    "quiz": {
        "mode": "local-model-assisted",
        "steps": [
            {"tool": "prepare_paideia_action", "args": {"action": "quiz"}},
            {"model": "Draft practice problems plus hidden answers."},
            {"tool": "save_action_artifact", "args": {"action": "quiz"}},
        ],
    },
    "twin": {
        "mode": "local-model-assisted",
        "steps": [
            {"tool": "prepare_paideia_action", "args": {"action": "twin"}},
            {"model": "Draft a same-pattern variant plus hidden answer."},
            {"tool": "save_action_artifact", "args": {"action": "twin"}},
        ],
    },
    "blind": {
        "mode": "attempt-first-local-model-assisted",
        "steps": [
            {"tool": "prepare_paideia_action", "args": {"action": "blind"}},
            {"model": "Ask for the learner strategy before revealing any reference solution."},
            {
                "tool": "append_error",
                "purpose": "Append an error only after a failed or revised strategy.",
            },
        ],
    },
    "chain": {
        "mode": "local-model-assisted",
        "steps": [
            {"tool": "prepare_paideia_action", "args": {"action": "chain"}},
            {"model": "Draft one integration problem plus hidden answer."},
            {"tool": "save_action_artifact", "args": {"action": "chain"}},
        ],
    },
    "mock": {
        "mode": "local-model-assisted",
        "steps": [
            {"tool": "prepare_paideia_action", "args": {"action": "mock"}},
            {"model": "Draft a full mock exam and hidden solution set."},
            {"tool": "save_action_artifact", "args": {"action": "mock"}},
        ],
    },
    "grade": {
        "mode": "ocr-plus-local-model-assisted",
        "steps": [
            {"tool": "grade_pdf", "purpose": "OCR or rasterize the answer PDF."},
            {"tool": "prepare_paideia_action", "args": {"action": "grade"}},
            {"model": "Compare attempt, reference context, and PAIDEIA strategy rubric."},
            {"tool": "save_grade_report", "purpose": "Persist feedback and append canonical errors."},
        ],
    },
    "weakmap": {
        "mode": "deterministic-or-local-model-assisted",
        "steps": [
            {"tool": "generate_weakmap", "purpose": "Produce the standard current weakmap."},
            {
                "tool": "prepare_paideia_action",
                "args": {"action": "weakmap"},
                "purpose": "Use when a richer model-written weakmap is requested.",
            },
            {"tool": "save_action_artifact", "args": {"action": "weakmap"}},
        ],
    },
    "cheatsheet": {
        "mode": "local-model-assisted",
        "steps": [
            {"tool": "prepare_paideia_action", "args": {"action": "cheatsheet"}},
            {"model": "Draft a one-page, error-driven markdown cheatsheet."},
            {"tool": "save_action_artifact", "args": {"action": "cheatsheet"}},
        ],
    },
    "derive": {
        "mode": "local-model-assisted",
        "steps": [
            {"tool": "prepare_paideia_action", "args": {"action": "derive"}},
            {"model": "Draft the clean reference derivation from course materials."},
            {"tool": "save_action_artifact", "args": {"action": "derive"}},
        ],
    },
    "alt": {
        "mode": "deterministic",
        "steps": [
            {"tool": "import_exam_radar", "purpose": "Fold Exam Radar export into the PAIDEIA course graph."},
            {"tool": "hwmap", "purpose": "Compare lecture emphasis with HW-density tiers."},
        ],
    },
}


def build_alt_manifest(
    project_root: str | None = None,
    repo_root: str | None = None,
) -> dict[str, Any]:
    """Return the manifest Alt's local model can use to orchestrate PAIDEIA."""

    catalog = parse_paideia_repo(repo_root)
    actions = []
    for action in catalog["actions"]:
        name = action["name"]
        actions.append(
            {
                **action,
                "recipe": ACTION_RECIPES.get(name, {"mode": "unknown", "steps": []}),
            }
        )

    return {
        "schema": "paideia-alt-mcp-manifest:v1",
        "server": {
            "name": "paideia-mcp",
            "transport": "stdio",
            "command": "python3",
            "args": ["-m", "paideia_mcp.bootstrap"],
            "working_directory": "<path-to-PAIDEIA-mcp>",
        },
        "project_root": project_root or "<course-root>",
        "alt_sdk_boundary": {
            "sdk_import": "import { alt } from 'alt-plugin-sdk'",
            "notes_source": "Alt can read notes with alt.notes.*; this MCP server cannot read Alt's private database directly.",
            "bridge": "Pass selected note title/transcript/memo/summary payloads into bootstrap_alt_course, import_alt_notes, or import_alt_note.",
            "filesystem": "Durable local markdown writes happen through this MCP server, not through the Alt plugin sandbox.",
        },
        "paideia_rules": [
            "Durable study graph lives on disk as markdown/YAML.",
            "HW density is the primary exam-probability signal.",
            "Alt/Exam Radar lecture emphasis is a second signal and must not silently overwrite HW tiers.",
            "Attempt-first drills ask for strategy before revealing solutions.",
            "errors/log.md and weakmap/ preserve append-only learning history.",
        ],
        "tools": MCP_TOOLS,
        "prompts": [spec["name"] for spec in list_prompt_specs()],
        "actions": actions,
        "extra_actions": catalog.get("extra_actions", []),
        "action_count": len(actions),
        "canonical_action_count": len(CANONICAL_ACTIONS),
        "extra_action_count": catalog.get("extra_count", 0),
    }


def alt_system_prompt(project_root: str | None = None) -> str:
    """Return the default system prompt text for Alt clients that read resources."""

    return workflow_guide("operating-guide", project_root=project_root)["prompt"]
