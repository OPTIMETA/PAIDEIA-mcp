from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from paideia_mcp.action import prepare_paideia_action
from paideia_mcp.alt_manifest import ACTION_RECIPES, build_alt_manifest
from paideia_mcp.alt_setup import alt_setup_instructions
from paideia_mcp.doctor import paideia_doctor
from paideia_mcp.exam_radar import import_exam_radar, parse_exam_radar_export
from paideia_mcp.prompts import workflow_guide
from paideia_mcp.repo_parser import CANONICAL_ACTIONS, get_action, parse_paideia_repo
from paideia_mcp.server import _get_prompt, _list_prompts, _list_resources, _list_tools, _read_resource
from paideia_mcp.study_tools import generate_weakmap, hwmap, pattern_lookup
from paideia_mcp.workspace import (
    append_error,
    bootstrap_alt_course,
    import_alt_note,
    import_alt_notes,
    init_course,
    read_artifact,
    save_action_artifact,
    save_course_index,
    save_grade_report,
    write_artifact,
)


def test_parse_nearby_paideia_repo_exposes_canonical_actions() -> None:
    catalog = parse_paideia_repo()

    names = {a["name"] for a in catalog["actions"]}
    assert {"init-course", "ingest", "analyze", "quiz", "grade", "alt"} <= names
    assert catalog["count"] >= 16


def test_repo_parser_handles_claude_command_repos_and_extras(tmp_path: Path) -> None:
    root = tmp_path / "PAIDEIA"
    commands = root / "plugins" / "paideia" / "commands"
    commands.mkdir(parents=True)
    (commands / "quiz.md").write_text(
        "---\n"
        "description: Generate practice problems from command markdown.\n"
        "---\n\n"
        "Quiz command body.\n",
        encoding="utf-8",
    )
    (commands / "doctor.md").write_text(
        "---\n"
        "description: Diagnose the command install.\n"
        "---\n\n"
        "Doctor command body.\n",
        encoding="utf-8",
    )

    catalog = parse_paideia_repo(str(root))
    quiz = next(action for action in catalog["actions"] if action["name"] == "quiz")
    extras = {action["name"]: action for action in catalog["extra_actions"]}

    assert quiz["source"] == "claude-command"
    assert "Generate practice" in quiz["description"]
    assert "doctor" in extras
    assert extras["doctor"]["source"] == "claude-command"
    assert get_action("doctor", str(root)).instruction.strip() == "Doctor command body."


def test_repo_parser_handles_hermes_command_repos(tmp_path: Path) -> None:
    root = tmp_path / "PAIDEIA-Hermes"
    commands = root / "commands"
    commands.mkdir(parents=True)
    (commands / "quiz.md").write_text(
        "---\n"
        "description: Hermes quiz command.\n"
        "---\n\n"
        "Hermes quiz body.\n",
        encoding="utf-8",
    )

    catalog = parse_paideia_repo(str(root))
    quiz = next(action for action in catalog["actions"] if action["name"] == "quiz")

    assert quiz["source"] == "hermes-command"
    assert "Hermes quiz command" in quiz["description"]
    assert get_action("quiz", str(root)).instruction.strip() == "Hermes quiz body."


def test_workspace_can_init_write_read_and_append_error(tmp_path: Path) -> None:
    root = tmp_path / "course"
    created = init_course(
        str(root),
        course_name="Signals",
        exam_date="2026-12-01",
        exam_type="final",
    )

    assert (root / ".course-meta").exists()
    assert "materials/lectures" in created["created_dirs"]

    written = write_artifact(
        str(root),
        "course-index/patterns.md",
        "# Patterns\n\n## P1 Transform\n",
    )
    assert written["path"] == "course-index/patterns.md"
    read = read_artifact(str(root), "course-index/patterns.md")
    assert "P1 Transform" in read["text"]

    appended = append_error(
        str(root),
        problem_id="q1",
        pattern="P1",
        error_type="pattern-missed",
        summary="Picked the wrong transform",
        source="blind/q1",
    )
    assert "pattern:    P1" in appended["entry"]


def test_exam_radar_import_writes_radar_and_weakmap(tmp_path: Path) -> None:
    root = tmp_path / "course"
    init_course(str(root), "EM", "2026-12-01")
    export = """# Exam Radar 작전 — EM
<!-- exam-radar:v1 source=alt -->

- 코스: EM
- 시험까지: D-10

## 지금 할 것 — 골드존 (시험확률 높음 · 아직 약함)
1. Boundary conditions · 시험확률 88% · 🎙

## 이미 다진 것 (잘 알거나 시험에 덜 나옴)
- Green theorem · 시험확률 55%

## 버려도 안전 (안 해도 되는 것)
- History notes · 시험확률 12%
"""

    parsed = parse_exam_radar_export(export)
    assert parsed["gold_count"] == 1

    result = import_exam_radar(str(root), export)
    assert result["gold"] == 1
    assert (root / "course-index" / "radar.md").exists()
    assert (root / result["weakmap_path"]).exists()


def test_prepare_action_contains_instruction_and_context(tmp_path: Path) -> None:
    root = tmp_path / "course"
    init_course(str(root), "Calc", "2026-12-01")
    write_artifact(str(root), "course-index/patterns.md", "## P1 Residue\n")

    result = prepare_paideia_action("quiz", str(root), args="weakmap 3")

    assert result["action"]["name"] == "quiz"
    assert "Original PAIDEIA action instruction" in result["model_prompt"]
    assert "save_action_artifact" in result["write_tools"]
    assert "save_course_index" in result["write_tools"]
    assert "save_grade_report" in result["write_tools"]
    assert "write_artifact" in result["write_tools"]


def test_small_study_tools(tmp_path: Path) -> None:
    root = tmp_path / "course"
    init_course(str(root), "Calc", "2026-12-01")
    write_artifact(str(root), "course-index/patterns.md", "## P1 Residue\nUse poles.\n")
    write_artifact(
        str(root),
        "course-index/coverage.md",
        "| § | Title | HW coverage | Exam tier |\n"
        "|---|---|---|---|\n"
        "| §1 | Residues | 3 | 🔥🔥 Exam-primary |\n",
    )
    append_error(str(root), "q1", "P1", "pattern-missed", "Missed pole", "grade/q1")

    assert pattern_lookup(str(root), "P1")["matches"] >= 1
    assert hwmap(str(root))["items"]
    weakmap = generate_weakmap(str(root))
    assert (root / weakmap["path"]).exists()


def test_import_alt_note_writes_materials_and_converted(tmp_path: Path) -> None:
    root = tmp_path / "course"
    init_course(str(root), "EM", "2026-12-01")

    imported = import_alt_note(
        str(root),
        title="Lecture 3 Boundary Conditions",
        transcript="Professor: this boundary condition is on the exam.",
        note_id=42,
        memo="Check examples.",
        summary="Boundary conditions.",
    )

    assert imported["material_path"].startswith("materials/lectures/")
    assert imported["converted_path"].startswith("converted/lectures/")
    assert "this boundary condition" in (root / imported["converted_path"]).read_text(
        encoding="utf-8"
    )


def test_import_alt_notes_and_bootstrap_alt_course_handle_batches(tmp_path: Path) -> None:
    root = tmp_path / "course"
    init_course(str(root), "Batch", "2026-12-01")

    batch = import_alt_notes(
        str(root),
        [
            {
                "noteId": 1,
                "title": "Lecture 1 Eigenvalues",
                "transcript": "Eigenvalues are exam-critical.",
                "memo": "Do examples.",
            },
            {
                "id": 2,
                "title": "Lecture 2 Orthogonality",
                "transcript": "Projection and orthogonality repeat.",
                "summary": "Projection lecture.",
            },
        ],
    )

    assert batch["imported_count"] == 2
    assert batch["error_count"] == 0
    assert len(list((root / "converted" / "lectures").glob("*.md"))) == 2

    boot_root = tmp_path / "boot"
    boot = bootstrap_alt_course(
        str(boot_root),
        course_name="Linear Algebra",
        exam_date="2026-12-01",
        notes=[
            {
                "note_id": "alt-3",
                "title": "Lecture 3 SVD",
                "transcript": "SVD is emphasized.",
            }
        ],
        git_init=False,
    )
    assert (boot_root / ".course-meta").exists()
    assert boot["notes"]["imported_count"] == 1
    assert len(list((boot_root / "materials" / "lectures").glob("*.md"))) == 1


def test_save_action_artifact_uses_paideia_paths(tmp_path: Path) -> None:
    root = tmp_path / "course"
    init_course(str(root), "Calc", "2026-12-01")

    quiz = save_action_artifact(
        str(root),
        action="quiz",
        slug="residue drill",
        content="# Quiz\n",
        answer_content="# Answers\n",
    )
    assert quiz["path"].startswith("quizzes/residue-drill_")
    assert quiz["sibling_path"].endswith("_answers.md")
    assert (root / quiz["path"]).exists()
    assert (root / quiz["sibling_path"]).exists()

    cheat = save_action_artifact(str(root), action="cheatsheet", content="# Final\n")
    assert cheat["path"] == "cheatsheet/final.md"


def test_save_course_index_and_grade_report_are_typed_writers(tmp_path: Path) -> None:
    root = tmp_path / "course"
    init_course(str(root), "Signals", "2026-12-01")

    index = save_course_index(
        str(root),
        summary_md="# Summary\n",
        patterns_md="# Patterns\n\n## P2 Convolution\n",
        coverage_md="| § | Title | HW coverage | Exam tier |\n",
    )
    assert index["paths"] == [
        "course-index/summary.md",
        "course-index/patterns.md",
        "course-index/coverage.md",
    ]

    report = save_grade_report(
        str(root),
        slug="quiz-1",
        report_md="# Grade\n\nPattern ok, end form wrong.\n",
        errors=[
            {
                "problem_id": "quiz-1-q1",
                "pattern": "P2",
                "error_type": "wrong-end-form",
                "summary": "Dropped the convolution bound.",
            }
        ],
    )
    assert report["path"] == "answers/converted/quiz-1.md"
    assert report["errors_appended"] == 1
    assert "Dropped the convolution bound" in (root / "errors" / "log.md").read_text(
        encoding="utf-8"
    )


def test_alt_workflow_guides_are_available_as_tool_and_prompts() -> None:
    guide = workflow_guide("lecture-to-quiz", project_root="/tmp/course")
    assert "import_alt_note" in guide["prompt"]
    assert "save_action_artifact" in guide["prompt"]
    assert "save_course_index" in guide["prompt"]

    prompts = asyncio.run(_list_prompts())
    names = {p.name for p in prompts}
    assert "paideia-lecture-to-quiz" in names
    got = asyncio.run(_get_prompt("paideia-lecture-to-quiz", {"project_root": "/tmp/course"}))
    assert "Lecture-to-quiz flow" in got.messages[0].content.text

    tools = asyncio.run(_list_tools())
    tool_names = {t.name for t in tools}
    assert "alt_workflow_guide" in tool_names
    assert "alt_capability_manifest" in tool_names
    assert "alt_setup_instructions" in tool_names
    assert "paideia_doctor" in tool_names
    assert "PAIDEIA__init_course" in tool_names
    assert "PAIDEIA__write_artifact" in tool_names


def test_alt_manifest_covers_every_canonical_action() -> None:
    manifest = build_alt_manifest(project_root="/tmp/course")
    action_names = {action["name"] for action in manifest["actions"]}

    assert action_names == set(CANONICAL_ACTIONS)
    assert set(ACTION_RECIPES) == set(CANONICAL_ACTIONS)
    assert manifest["action_count"] == 16
    assert "alt_capability_manifest" in manifest["tools"]
    assert "import_alt_notes" in manifest["tools"]
    assert "bootstrap_alt_course" in manifest["tools"]
    assert "alt_setup_instructions" in manifest["tools"]
    assert "paideia_doctor" in manifest["tools"]
    assert "PAIDEIA__init_course" in manifest["tools"]
    assert "PAIDEIA__write_artifact" in manifest["tools"]
    for action in manifest["actions"]:
        steps = action["recipe"]["steps"]
        assert steps, action["name"]
        for step in steps:
            tool = step.get("tool")
            if tool is not None:
                assert tool in manifest["tools"], (action["name"], tool)


def test_alt_manifest_is_available_as_resource() -> None:
    resources = asyncio.run(_list_resources())
    resource_names = {resource.name for resource in resources}
    assert "paideia-alt-manifest" in resource_names
    assert "paideia-alt-system-prompt" in resource_names

    manifest_resource = asyncio.run(_read_resource("paideia://alt/manifest"))
    manifest = json.loads(manifest_resource[0].content)
    assert manifest["schema"] == "paideia-alt-mcp-manifest:v1"
    assert manifest["action_count"] == 16

    prompt_resource = asyncio.run(_read_resource("paideia://alt/system-prompt"))
    assert "You are Alt's local model" in prompt_resource[0].content


def test_paideia_doctor_reports_readiness_and_next_steps(tmp_path: Path) -> None:
    root = tmp_path / "course"

    empty = paideia_doctor(str(root))
    assert empty["status"] == "course-not-initialized"
    assert empty["mcp"]["tool_count"] >= 26
    assert "bootstrap_alt_course" in " ".join(empty["recommendations"])

    bootstrap_alt_course(
        str(root),
        course_name="Doctor",
        exam_date="2026-12-01",
        notes=[
            {
                "note_id": "d1",
                "title": "Lecture",
                "transcript": "Repeated exam signal.",
            }
        ],
        git_init=False,
    )
    initialized = paideia_doctor(str(root))
    assert initialized["status"] == "needs-analysis"
    assert initialized["course"]["initialized"] is True
    assert initialized["course"]["artifact_counts"]["converted"] >= 1
    analyze = next(action for action in initialized["actions"] if action["action"] == "analyze")
    assert analyze["ready"] is True


def test_alt_setup_instructions_match_local_stdio_form(tmp_path: Path) -> None:
    root = tmp_path / "PAIDEIA-mcp"
    root.mkdir()
    setup = alt_setup_instructions(str(root), prefer_venv=True)

    assert setup["schema"] == "paideia-alt-setup:v1"
    assert setup["command"].endswith(".venv/bin/python")
    assert setup["args"] == ["-m", "paideia_mcp.bootstrap"]
    assert setup["args_multiline"] == "-m\npaideia_mcp.bootstrap"
    assert setup["working_directory"] == str(root)
    assert setup["env"]["PAIDEIA_MCP_AUTO_INSTALL"] == "0"
    assert "명령어" in setup["text"]
    assert "한 줄에 하나" in setup["text"]

    no_venv = alt_setup_instructions(str(root), prefer_venv=False)
    assert no_venv["command"] == "python3"
    assert no_venv["env"]["PAIDEIA_MCP_AUTO_INSTALL"] == "1"


def test_end_to_end_alt_local_model_workflow(tmp_path: Path) -> None:
    root = tmp_path / "course"
    init_course(str(root), "Electromagnetics", "2026-12-01")

    imported = import_alt_note(
        str(root),
        title="Lecture 1 Gauss Law",
        transcript="Gauss law is important. This flux calculation will be on the exam.",
        note_id="alt-1",
    )
    assert (root / imported["converted_path"]).exists()

    # Simulate the local model producing the analyze outputs after
    # prepare_paideia_action("analyze") gives it the PAIDEIA recipe.
    analyze = prepare_paideia_action("analyze", str(root))
    assert analyze["action"]["name"] == "analyze"
    save_course_index(
        str(root),
        summary_md="# Summary\n\n## §1 Gauss law\n",
        patterns_md="# Patterns\n\n## P1 Flux theorem\nRecognition: closed surface flux.\n",
        coverage_md=(
            "| § | Title | HW coverage | Exam tier |\n"
            "|---|---|---|---|\n"
            "| §1 | Gauss law | 3 | 🔥🔥 Exam-primary |\n"
        ),
    )

    quiz_prep = prepare_paideia_action("quiz", str(root), args="§1 2")
    assert "course-index/patterns.md" in str(quiz_prep["required_context"])
    quiz = save_action_artifact(
        str(root),
        action="quiz",
        slug="gauss-law",
        content="# Quiz\n\n1. Compute the flux.\n",
        answer_content="# Answers\n\nUse P1.\n",
    )
    assert (root / quiz["path"]).exists()
    assert (root / quiz["sibling_path"]).exists()

    append_error(
        str(root),
        problem_id="gauss-law-q1",
        pattern="P1",
        error_type="wrong-end-form",
        summary="Forgot outward normal sign",
        source=quiz["path"],
    )
    weakmap = generate_weakmap(str(root))
    assert (root / weakmap["path"]).exists()
    assert "P1" in (root / weakmap["path"]).read_text(encoding="utf-8")


def test_stdio_mcp_smoke_exposes_tools_prompts_and_writes(tmp_path: Path) -> None:
    package_root = Path(__file__).resolve().parents[1]
    course_root = tmp_path / "course"

    async def run_smoke() -> None:
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "paideia_mcp.bootstrap"],
            cwd=str(package_root),
            env={"PAIDEIA_MCP_AUTO_INSTALL": "0"},
        )
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                tools = await session.list_tools()
                tool_names = {tool.name for tool in tools.tools}
                assert "prepare_paideia_action" in tool_names
                assert "save_course_index" in tool_names
                assert "save_grade_report" in tool_names
                assert "alt_capability_manifest" in tool_names
                assert "alt_setup_instructions" in tool_names
                assert "import_alt_notes" in tool_names
                assert "bootstrap_alt_course" in tool_names
                assert "paideia_doctor" in tool_names
                assert "PAIDEIA__init_course" in tool_names
                assert "PAIDEIA__write_artifact" in tool_names

                prompts = await session.list_prompts()
                assert "paideia-operating-guide" in {
                    prompt.name for prompt in prompts.prompts
                }
                prompt = await session.get_prompt(
                    "paideia-lecture-to-quiz",
                    {"project_root": str(course_root)},
                )
                assert "Lecture-to-quiz flow" in prompt.messages[0].content.text

                resources = await session.list_resources()
                assert "paideia-alt-manifest" in {
                    resource.name for resource in resources.resources
                }
                manifest_read = await session.read_resource("paideia://alt/manifest")
                manifest = json.loads(manifest_read.contents[0].text)
                assert manifest["action_count"] == 16

                doctor = await session.call_tool(
                    "paideia_doctor",
                    {"project_root": str(course_root)},
                )
                doctor_json = json.loads(doctor.content[0].text)
                assert doctor_json["status"] == "course-not-initialized"

                created = await session.call_tool(
                    "init_course",
                    {
                        "project_root": str(course_root),
                        "course_name": "MCP Smoke",
                        "exam_date": "2026-12-01",
                        "git_init": False,
                    },
                )
                created_json = json.loads(created.content[0].text)
                assert created_json["project_root"] == str(course_root)

                saved = await session.call_tool(
                    "save_course_index",
                    {
                        "project_root": str(course_root),
                        "summary_md": "# Summary\n",
                        "patterns_md": "# Patterns\n\n## P1 Flux\n",
                        "coverage_md": "| § | Title | HW coverage | Exam tier |\n",
                    },
                )
                saved_json = json.loads(saved.content[0].text)
                assert "course-index/patterns.md" in saved_json["paths"]

                manifest_tool = await session.call_tool(
                    "alt_capability_manifest",
                    {"project_root": str(course_root)},
                )
                manifest_tool_json = json.loads(manifest_tool.content[0].text)
                assert manifest_tool_json["project_root"] == str(course_root)

                setup_tool = await session.call_tool(
                    "alt_setup_instructions",
                    {"package_root": str(package_root)},
                )
                setup_tool_json = json.loads(setup_tool.content[0].text)
                assert setup_tool_json["args"] == ["-m", "paideia_mcp.bootstrap"]
                assert setup_tool_json["working_directory"] == str(package_root)

                alias_write = await session.call_tool(
                    "PAIDEIA__write_artifact",
                    {
                        "project_root": str(course_root),
                        "path": "course-index/alias-smoke.md",
                        "content": "# Alias Smoke\n",
                    },
                )
                alias_write_json = json.loads(alias_write.content[0].text)
                assert alias_write_json["path"] == "course-index/alias-smoke.md"
                assert (course_root / "course-index" / "alias-smoke.md").exists()

                batch = await session.call_tool(
                    "import_alt_notes",
                    {
                        "project_root": str(course_root),
                        "notes": [
                            {
                                "note_id": 11,
                                "title": "Lecture 11",
                                "transcript": "This topic is repeated.",
                            }
                        ],
                    },
                )
                batch_json = json.loads(batch.content[0].text)
                assert batch_json["imported_count"] == 1

    asyncio.run(run_smoke())
