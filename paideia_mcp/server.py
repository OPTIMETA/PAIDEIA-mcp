"""paideia-mcp stdio entrypoint.

Registers the local PAIDEIA tools used by Codex, Alt, and other MCP clients,
then dispatches JSON-encoded results over the stdio MCP channel. The bootstrap
entrypoint launches this module after dependency preflight.
"""

from __future__ import annotations

import sys

from .bootstrap import missing_imports, missing_message

_missing = missing_imports()
if _missing:
    sys.stderr.write(missing_message(_missing))
    sys.exit(1)

import asyncio
import json
from typing import Any

from mcp.server import Server
from mcp.server.lowlevel.helper_types import ReadResourceContents
from mcp.server.stdio import stdio_server
from mcp.types import GetPromptResult, Prompt, PromptArgument, PromptMessage, Resource, TextContent, Tool

from .action import list_paideia_actions, prepare_paideia_action
from .alt_manifest import ALT_TOOL_NAMESPACE, alt_system_prompt, build_alt_manifest
from .alt_setup import alt_setup_instructions
from .analyze import build_course_index
from .doctor import paideia_doctor
from .exam_radar import import_exam_radar, parse_exam_radar_export
from .grade import grade_pdf
from .ingest import ingest_pdfs
from .phase import course_phase
from .prompts import list_prompt_specs, workflow_guide
from .repo_parser import parse_paideia_repo
from .study_tools import generate_weakmap, hwmap, pattern_lookup
from .workspace import (
    append_error,
    bootstrap_alt_course,
    import_alt_note,
    import_alt_notes,
    init_course,
    list_artifacts,
    read_artifact,
    save_action_artifact,
    save_course_index,
    save_grade_report,
    write_artifact,
)

app: Server = Server("paideia-mcp")


_PROJECT_ROOT_PROP = {
    "type": "string",
    "description": (
        "Absolute path to the course project root. Defaults to the server's "
        "CWD when omitted; set this explicitly if the user has cd'd between "
        "courses within the same Codex session."
    ),
}


_INGEST_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "engine": {
            "type": "string",
            "enum": ["codex-native", "qwen3-vl", "tesseract"],
            "default": "codex-native",
            "description": (
                "OCR engine. codex-native (default) renders PDFs to PNGs "
                "under .paideia-cache/ and returns a manifest so the calling "
                "skill can read pages with Codex CLI's bundled vision (no "
                "extra API billing for ChatGPT subscribers). qwen3-vl needs a "
                "local Ollama with qwen3-vl:8b. tesseract needs pytesseract "
                "with eng and/or kor traineddata."
            ),
        },
        "force": {
            "type": "boolean",
            "default": False,
            "description": "Reconvert even if converted/<cat>/<stem>.md exists.",
        },
        "categories": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": ["lectures", "textbook", "homework", "solutions"],
            },
            "description": "Restrict to a subset of the materials subfolders.",
        },
        "project_root": _PROJECT_ROOT_PROP,
    },
    "additionalProperties": False,
}


_GRADE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "path": {
            "type": "string",
            "description": (
                "Answer PDF path. Absolute, or relative to project_root "
                "(typically answers/<stem>.pdf)."
            ),
        },
        "engine": {
            "type": "string",
            "enum": ["codex-native", "qwen3-vl", "tesseract"],
            "description": (
                "Override the OCR engine. When omitted, falls back to "
                ".course-meta OCR_ENGINE, then to codex-native."
            ),
        },
        "project_root": _PROJECT_ROOT_PROP,
    },
    "required": ["path"],
    "additionalProperties": False,
}


_ANALYZE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "weak_zones": {
            "type": "string",
            "description": "Free-form hints about weak areas; passed through.",
        },
        "force": {
            "type": "boolean",
            "default": False,
            "description": (
                "Regenerate course-index/{summary,patterns,coverage}.md even if "
                "those files already exist."
            ),
        },
        "project_root": _PROJECT_ROOT_PROP,
    },
    "additionalProperties": False,
}


_PHASE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "project_root": _PROJECT_ROOT_PROP,
    },
    "additionalProperties": False,
}


_INIT_COURSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "project_root": _PROJECT_ROOT_PROP,
        "course_name": {"type": "string"},
        "exam_date": {"type": "string", "description": "YYYY-MM-DD."},
        "exam_type": {"type": "string", "default": "exam"},
        "weak_zones": {"type": "string", "default": "unknown"},
        "ocr_engine": {
            "type": "string",
            "enum": ["codex-native", "qwen3-vl", "tesseract"],
            "default": "codex-native",
        },
        "git_init": {"type": "boolean", "default": True},
    },
    "required": ["project_root", "course_name", "exam_date"],
    "additionalProperties": False,
}


_REPO_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "repo_root": {
            "type": "string",
            "description": (
                "Optional path to PAIDEIA / PAIDEIA-codex / PAIDEIA-opencode. "
                "When omitted, the server auto-discovers nearby repos or uses "
                "the built-in canonical action catalog."
            ),
        },
    },
    "additionalProperties": False,
}


_PREPARE_ACTION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "action": {
            "type": "string",
            "description": "PAIDEIA action name, e.g. quiz, grade, weakmap, alt.",
        },
        "project_root": _PROJECT_ROOT_PROP,
        "args": {"type": "string", "default": ""},
        "repo_root": _REPO_SCHEMA["properties"]["repo_root"],
        "include_instruction": {"type": "boolean", "default": True},
    },
    "required": ["action"],
    "additionalProperties": False,
}


_LIST_ARTIFACTS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "project_root": _PROJECT_ROOT_PROP,
        "glob_pattern": {"type": "string", "default": "**/*.md"},
    },
    "additionalProperties": False,
}


_READ_ARTIFACT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "project_root": _PROJECT_ROOT_PROP,
        "path": {"type": "string"},
        "max_chars": {"type": "integer", "default": 20000},
    },
    "required": ["path"],
    "additionalProperties": False,
}


_WRITE_ARTIFACT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "project_root": _PROJECT_ROOT_PROP,
        "path": {"type": "string"},
        "content": {"type": "string"},
        "mode": {
            "type": "string",
            "enum": ["overwrite", "append", "create"],
            "default": "overwrite",
        },
        "create_parent": {"type": "boolean", "default": True},
    },
    "required": ["path", "content"],
    "additionalProperties": False,
}


_IMPORT_ALT_NOTE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "project_root": _PROJECT_ROOT_PROP,
        "title": {"type": "string"},
        "transcript": {"type": "string"},
        "note_id": {
            "type": ["string", "integer", "null"],
            "description": "Alt note id if available.",
        },
        "memo": {"type": "string", "default": ""},
        "summary": {"type": "string", "default": ""},
        "category": {
            "type": "string",
            "enum": ["lectures", "textbook", "homework", "solutions"],
            "default": "lectures",
        },
        "write_converted": {"type": "boolean", "default": True},
        "overwrite": {"type": "boolean", "default": False},
    },
    "required": ["title", "transcript"],
    "additionalProperties": False,
}


_ALT_NOTE_PAYLOAD_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "note_id": {
            "type": ["string", "integer", "null"],
            "description": "Alt note id. noteId/id aliases are also accepted by the tool.",
        },
        "noteId": {"type": ["string", "integer", "null"]},
        "id": {"type": ["string", "integer", "null"]},
        "title": {"type": "string"},
        "transcript": {"type": "string"},
        "memo": {"type": "string", "default": ""},
        "summary": {"type": "string", "default": ""},
        "category": {
            "type": "string",
            "enum": ["lectures", "textbook", "homework", "solutions"],
        },
    },
    "required": ["title", "transcript"],
    "additionalProperties": False,
}


_IMPORT_ALT_NOTES_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "project_root": _PROJECT_ROOT_PROP,
        "notes": {"type": "array", "items": _ALT_NOTE_PAYLOAD_SCHEMA},
        "category": {
            "type": "string",
            "enum": ["lectures", "textbook", "homework", "solutions"],
            "default": "lectures",
        },
        "write_converted": {"type": "boolean", "default": True},
        "overwrite": {"type": "boolean", "default": False},
        "continue_on_error": {"type": "boolean", "default": True},
    },
    "required": ["notes"],
    "additionalProperties": False,
}


_BOOTSTRAP_ALT_COURSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "project_root": _PROJECT_ROOT_PROP,
        "course_name": {"type": "string"},
        "exam_date": {"type": "string", "description": "YYYY-MM-DD."},
        "notes": {"type": "array", "items": _ALT_NOTE_PAYLOAD_SCHEMA, "default": []},
        "exam_type": {"type": "string", "default": "exam"},
        "weak_zones": {"type": "string", "default": "unknown"},
        "ocr_engine": {
            "type": "string",
            "enum": ["codex-native", "qwen3-vl", "tesseract"],
            "default": "codex-native",
        },
        "git_init": {"type": "boolean", "default": True},
        "category": {
            "type": "string",
            "enum": ["lectures", "textbook", "homework", "solutions"],
            "default": "lectures",
        },
        "write_converted": {"type": "boolean", "default": True},
        "overwrite_notes": {"type": "boolean", "default": False},
        "continue_on_error": {"type": "boolean", "default": True},
    },
    "required": ["project_root", "course_name", "exam_date"],
    "additionalProperties": False,
}


_SAVE_ACTION_ARTIFACT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "project_root": _PROJECT_ROOT_PROP,
        "action": {
            "type": "string",
            "description": "PAIDEIA action name, e.g. quiz, twin, mock, derive.",
        },
        "content": {"type": "string"},
        "answer_content": {
            "type": ["string", "null"],
            "description": "Optional paired answer/solution markdown.",
        },
        "slug": {"type": "string"},
        "target_path": {
            "type": "string",
            "description": "Explicit relative path for multi-file actions like analyze.",
        },
        "overwrite": {"type": "boolean", "default": False},
    },
    "required": ["action", "content"],
    "additionalProperties": False,
}


_SAVE_COURSE_INDEX_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "project_root": _PROJECT_ROOT_PROP,
        "summary_md": {"type": "string"},
        "patterns_md": {"type": "string"},
        "coverage_md": {"type": "string"},
        "overwrite": {"type": "boolean", "default": False},
    },
    "required": ["summary_md", "patterns_md", "coverage_md"],
    "additionalProperties": False,
}


_SAVE_GRADE_REPORT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "project_root": _PROJECT_ROOT_PROP,
        "slug": {
            "type": "string",
            "description": "Filename stem for answers/converted/<slug>.md.",
        },
        "report_md": {"type": "string"},
        "errors": {
            "type": "array",
            "default": [],
            "items": {
                "type": "object",
                "properties": {
                    "problem_id": {"type": "string"},
                    "pattern": {"type": "string", "description": "Pk label, e.g. P3."},
                    "error_type": {
                        "type": "string",
                        "enum": [
                            "pattern-missed",
                            "wrong-variable",
                            "wrong-end-form",
                            "algebraic",
                            "sign",
                            "definition",
                        ],
                    },
                    "summary": {"type": "string"},
                    "source": {"type": "string"},
                    "date": {"type": "string"},
                },
                "required": ["pattern", "error_type", "summary"],
                "additionalProperties": False,
            },
        },
        "source": {
            "type": "string",
            "description": "Default source to record for appended errors.",
        },
        "overwrite": {"type": "boolean", "default": False},
    },
    "required": ["slug", "report_md"],
    "additionalProperties": False,
}


_APPEND_ERROR_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "project_root": _PROJECT_ROOT_PROP,
        "problem_id": {"type": "string"},
        "pattern": {"type": "string", "description": "Pk label, e.g. P3."},
        "error_type": {
            "type": "string",
            "enum": [
                "pattern-missed",
                "wrong-variable",
                "wrong-end-form",
                "algebraic",
                "sign",
                "definition",
            ],
        },
        "summary": {"type": "string"},
        "source": {"type": "string"},
        "date": {"type": "string"},
    },
    "required": ["problem_id", "pattern", "error_type", "summary", "source"],
    "additionalProperties": False,
}


_EXAM_RADAR_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "project_root": _PROJECT_ROOT_PROP,
        "export_md": {"type": "string"},
        "course_name": {"type": "string"},
    },
    "required": ["export_md"],
    "additionalProperties": False,
}


_PATTERN_LOOKUP_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "project_root": _PROJECT_ROOT_PROP,
        "query": {"type": "string", "default": ""},
        "max_chars": {"type": "integer", "default": 16000},
    },
    "additionalProperties": False,
}


_HWMAP_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "project_root": _PROJECT_ROOT_PROP,
        "mode": {
            "type": "string",
            "default": "hot",
            "description": "hot/primary/exam, all, or low/drop.",
        },
    },
    "additionalProperties": False,
}


_GENERATE_WEAKMAP_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "project_root": _PROJECT_ROOT_PROP,
        "concept": {"type": "string", "default": ""},
    },
    "additionalProperties": False,
}


_ALT_WORKFLOW_GUIDE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "scenario": {
            "type": "string",
            "enum": [
                "operating-guide",
                "course-bootstrap",
                "lecture-to-quiz",
                "attempt-first-drill",
                "exam-radar-import",
                "paideia-operating-guide",
                "paideia-course-bootstrap",
                "paideia-lecture-to-quiz",
                "paideia-attempt-first-drill",
                "paideia-exam-radar-import",
            ],
            "default": "operating-guide",
        },
        "project_root": _PROJECT_ROOT_PROP,
    },
    "additionalProperties": False,
}


_ALT_CAPABILITY_MANIFEST_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "project_root": _PROJECT_ROOT_PROP,
        "repo_root": _REPO_SCHEMA["properties"]["repo_root"],
    },
    "additionalProperties": False,
}


_PAIDEIA_DOCTOR_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "project_root": _PROJECT_ROOT_PROP,
        "repo_root": _REPO_SCHEMA["properties"]["repo_root"],
    },
    "additionalProperties": False,
}


_ALT_SETUP_INSTRUCTIONS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "package_root": {
            "type": "string",
            "description": "PAIDEIA-mcp package root. Defaults to this server's source root.",
        },
        "prefer_venv": {"type": "boolean", "default": True},
        "auto_install": {
            "type": ["boolean", "null"],
            "description": "Override PAIDEIA_MCP_AUTO_INSTALL. Defaults to false for venv, true for python3.",
        },
        "server_name": {"type": "string", "default": "PAIDEIA"},
    },
    "additionalProperties": False,
}


def _alt_alias(name: str) -> str:
    return f"{ALT_TOOL_NAMESPACE}{name}"


def _canonical_tool_name(name: str) -> str:
    if name.startswith(ALT_TOOL_NAMESPACE):
        return name[len(ALT_TOOL_NAMESPACE) :]
    return name


def _with_alt_aliases(tools: list[Tool]) -> list[Tool]:
    aliases = [
        Tool(
            name=_alt_alias(tool.name),
            description=(
                f"PAIDEIA namespace alias for {tool.name}. Use this exact name when "
                f"Alt searches for {_alt_alias(tool.name)}. {tool.description or ''}"
            ).strip(),
            inputSchema=tool.inputSchema,
        )
        for tool in tools
    ]
    return tools + aliases


@app.list_prompts()
async def _list_prompts() -> list[Prompt]:
    """Publish Alt-facing prompt templates when the MCP client supports prompts."""

    prompts: list[Prompt] = []
    for spec in list_prompt_specs():
        prompts.append(
            Prompt(
                name=spec["name"],
                description=spec["description"],
                arguments=[
                    PromptArgument(
                        name=arg["name"],
                        description=arg.get("description"),
                        required=arg.get("required", False),
                    )
                    for arg in spec["arguments"]
                ],
            )
        )
    return prompts


@app.get_prompt()
async def _get_prompt(name: str, arguments: dict[str, str] | None) -> GetPromptResult:
    """Return one PAIDEIA prompt template."""

    args = arguments or {}
    guide = workflow_guide(name, project_root=args.get("project_root"))
    return GetPromptResult(
        description=guide["description"],
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(type="text", text=guide["prompt"]),
            )
        ],
    )


@app.list_resources()
async def _list_resources() -> list[Resource]:
    """Expose machine-readable Alt onboarding resources."""

    return [
        Resource(
            name="paideia-alt-manifest",
            uri="paideia://alt/manifest",
            description=(
                "JSON manifest mapping every PAIDEIA action to the MCP tools "
                "Alt's local model should call."
            ),
            mimeType="application/json",
        ),
        Resource(
            name="paideia-alt-system-prompt",
            uri="paideia://alt/system-prompt",
            description="Default operating prompt for Alt local models using PAIDEIA MCP.",
            mimeType="text/plain",
        ),
    ]


@app.read_resource()
async def _read_resource(uri: Any) -> list[ReadResourceContents]:
    """Return one Alt onboarding resource."""

    value = str(uri).rstrip("/")
    if value == "paideia://alt/manifest":
        return [
            ReadResourceContents(
                content=json.dumps(build_alt_manifest(), ensure_ascii=False, indent=2),
                mime_type="application/json",
            )
        ]
    if value == "paideia://alt/system-prompt":
        return [
            ReadResourceContents(
                content=alt_system_prompt(),
                mime_type="text/plain",
            )
        ]
    raise FileNotFoundError(f"unknown resource: {uri}")


@app.list_tools()
async def _list_tools() -> list[Tool]:
    """Publish PAIDEIA tools plus Alt namespace aliases."""

    tools = [
        Tool(
            name="ingest_pdfs",
            description=(
                "Render every materials/**/*.pdf to markdown via the selected "
                "OCR engine. Idempotent unless force=True."
            ),
            inputSchema=_INGEST_SCHEMA,
        ),
        Tool(
            name="grade_pdf",
            description=(
                "OCR a single hand-written answer PDF into "
                "answers/converted/<stem>.md with a confidence tier."
            ),
            inputSchema=_GRADE_SCHEMA,
        ),
        Tool(
            name="build_course_index",
            description=(
                "Inventory converted/ markdown files and write a draft "
                "course-index/{summary,patterns,coverage}.md baseline."
            ),
            inputSchema=_ANALYZE_SCHEMA,
        ),
        Tool(
            name="course_phase",
            description=(
                "Return the artifact-derived course phase (setup/diag/drill/"
                "mock/cram/cool), days_until_exam, and top_miss_pattern."
            ),
            inputSchema=_PHASE_SCHEMA,
        ),
        Tool(
            name="init_course",
            description="Create a PAIDEIA local course folder skeleton for Alt or any MCP client.",
            inputSchema=_INIT_COURSE_SCHEMA,
        ),
        Tool(
            name="parse_paideia_repo",
            description="Parse a PAIDEIA repo into the canonical action catalog.",
            inputSchema=_REPO_SCHEMA,
        ),
        Tool(
            name="list_paideia_actions",
            description="List PAIDEIA actions available to Alt's local model.",
            inputSchema=_REPO_SCHEMA,
        ),
        Tool(
            name="prepare_paideia_action",
            description=(
                "Compose the original PAIDEIA instruction, current workspace "
                "context, and output contract for an Alt local model to execute."
            ),
            inputSchema=_PREPARE_ACTION_SCHEMA,
        ),
        Tool(
            name="list_artifacts",
            description="List markdown artifacts in a PAIDEIA course folder.",
            inputSchema=_LIST_ARTIFACTS_SCHEMA,
        ),
        Tool(
            name="read_artifact",
            description="Read a PAIDEIA course artifact by relative path.",
            inputSchema=_READ_ARTIFACT_SCHEMA,
        ),
        Tool(
            name="write_artifact",
            description="Write/append/create a PAIDEIA markdown artifact under the course root.",
            inputSchema=_WRITE_ARTIFACT_SCHEMA,
        ),
        Tool(
            name="import_alt_note",
            description=(
                "Import an Alt active note/transcript into materials/<category> "
                "and optionally converted/<category> for PAIDEIA analysis."
            ),
            inputSchema=_IMPORT_ALT_NOTE_SCHEMA,
        ),
        Tool(
            name="import_alt_notes",
            description=(
                "Batch-import Alt note payloads from alt.notes.getContent into "
                "materials/<category> and converted/<category>."
            ),
            inputSchema=_IMPORT_ALT_NOTES_SCHEMA,
        ),
        Tool(
            name="bootstrap_alt_course",
            description=(
                "Create a PAIDEIA course folder and import an initial batch of "
                "Alt note transcripts in one call."
            ),
            inputSchema=_BOOTSTRAP_ALT_COURSE_SCHEMA,
        ),
        Tool(
            name="save_action_artifact",
            description=(
                "Save a local-model-generated PAIDEIA action output to canonical "
                "paths such as quizzes/*, twins/*, mock/*, derivations/*, or cheatsheet/final.md."
            ),
            inputSchema=_SAVE_ACTION_ARTIFACT_SCHEMA,
        ),
        Tool(
            name="save_course_index",
            description=(
                "Save model-generated analyze outputs to course-index/summary.md, "
                "course-index/patterns.md, and course-index/coverage.md in one call."
            ),
            inputSchema=_SAVE_COURSE_INDEX_SCHEMA,
        ),
        Tool(
            name="save_grade_report",
            description=(
                "Save a model-generated grading report under answers/converted/ "
                "and append any canonical error-log entries."
            ),
            inputSchema=_SAVE_GRADE_REPORT_SCHEMA,
        ),
        Tool(
            name="append_error",
            description="Append one canonical YAML error entry to errors/log.md.",
            inputSchema=_APPEND_ERROR_SCHEMA,
        ),
        Tool(
            name="parse_exam_radar_export",
            description="Parse an OPTIMETA Exam Radar exam-radar:v1 markdown export.",
            inputSchema={"type": "object", "properties": {"export_md": {"type": "string"}}, "required": ["export_md"], "additionalProperties": False},
        ),
        Tool(
            name="import_exam_radar",
            description="Import Exam Radar into radar.md, coverage.md annotation, and a gold-zone weakmap.",
            inputSchema=_EXAM_RADAR_SCHEMA,
        ),
        Tool(
            name="pattern_lookup",
            description="Filter course-index/patterns.md by Pk label or keyword.",
            inputSchema=_PATTERN_LOOKUP_SCHEMA,
        ),
        Tool(
            name="hwmap",
            description="Read course-index/coverage.md and return HW-density exam-priority rows.",
            inputSchema=_HWMAP_SCHEMA,
        ),
        Tool(
            name="generate_weakmap",
            description="Generate a compact timestamped weakmap from errors/log.md.",
            inputSchema=_GENERATE_WEAKMAP_SCHEMA,
        ),
        Tool(
            name="alt_workflow_guide",
            description=(
                "Return an Alt-local-model PAIDEIA operating guide. This mirrors "
                "the MCP prompts for clients that only expose tools."
            ),
            inputSchema=_ALT_WORKFLOW_GUIDE_SCHEMA,
        ),
        Tool(
            name="alt_capability_manifest",
            description=(
                "Return the machine-readable Alt manifest: setup, SDK boundary, "
                "PAIDEIA rules, and action-to-tool recipes for all 16 actions."
            ),
            inputSchema=_ALT_CAPABILITY_MANIFEST_SCHEMA,
        ),
        Tool(
            name="paideia_doctor",
            description=(
                "Diagnose PAIDEIA MCP install health, external dependencies, "
                "course-folder readiness, action prerequisites, and next steps."
            ),
            inputSchema=_PAIDEIA_DOCTOR_SCHEMA,
        ),
        Tool(
            name="alt_setup_instructions",
            description=(
                "Return exact field-by-field values for Alt's local (stdio) MCP "
                "server form: command, one-argument-per-line args, name, cwd, and env."
            ),
            inputSchema=_ALT_SETUP_INSTRUCTIONS_SCHEMA,
        ),
    ]
    return _with_alt_aliases(tools)


_DISPATCH = {
    "ingest_pdfs": ingest_pdfs,
    "grade_pdf": grade_pdf,
    "build_course_index": build_course_index,
    "course_phase": course_phase,
    "init_course": init_course,
    "parse_paideia_repo": parse_paideia_repo,
    "list_paideia_actions": list_paideia_actions,
    "prepare_paideia_action": prepare_paideia_action,
    "list_artifacts": list_artifacts,
    "read_artifact": read_artifact,
    "write_artifact": write_artifact,
    "import_alt_note": import_alt_note,
    "import_alt_notes": import_alt_notes,
    "bootstrap_alt_course": bootstrap_alt_course,
    "save_action_artifact": save_action_artifact,
    "save_course_index": save_course_index,
    "save_grade_report": save_grade_report,
    "append_error": append_error,
    "parse_exam_radar_export": parse_exam_radar_export,
    "import_exam_radar": import_exam_radar,
    "pattern_lookup": pattern_lookup,
    "hwmap": hwmap,
    "generate_weakmap": generate_weakmap,
    "alt_workflow_guide": workflow_guide,
    "alt_capability_manifest": build_alt_manifest,
    "paideia_doctor": paideia_doctor,
    "alt_setup_instructions": alt_setup_instructions,
}


@app.call_tool()
async def _call_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[TextContent]:
    """Dispatch a tool call and return its JSON-encoded result."""

    canonical_name = _canonical_tool_name(name)
    handler = _DISPATCH.get(canonical_name)
    if handler is None:
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {"error": f"unknown tool '{name}'"},
                    ensure_ascii=False,
                ),
            )
        ]
    kwargs = dict(arguments or {})
    try:
        result = handler(**kwargs)
    except TypeError as exc:
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "error": f"bad arguments for '{name}': {exc}",
                        "arguments": kwargs,
                    },
                    ensure_ascii=False,
                ),
            )
        ]
    except Exception as exc:  # noqa: BLE001 — surface as structured error
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "error": f"{type(exc).__name__}: {exc}",
                        "tool": name,
                        "canonical_tool": canonical_name,
                    },
                    ensure_ascii=False,
                ),
            )
        ]
    return [
        TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False, indent=2),
        )
    ]


async def _run() -> None:
    """Start the stdio server and run until the client disconnects."""

    async with stdio_server() as (reader, writer):
        await app.run(reader, writer, app.create_initialization_options())


def main() -> None:
    """Console-script entrypoint."""

    asyncio.run(_run())


if __name__ == "__main__":
    main()
