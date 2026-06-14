from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from paideia_mcp.action import prepare_paideia_action
from paideia_mcp.exam_radar import import_exam_radar, parse_exam_radar_export
from paideia_mcp.prompts import workflow_guide
from paideia_mcp.repo_parser import parse_paideia_repo
from paideia_mcp.server import _get_prompt, _list_prompts, _list_tools
from paideia_mcp.study_tools import generate_weakmap, hwmap, pattern_lookup
from paideia_mcp.workspace import (
    append_error,
    import_alt_note,
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

                prompts = await session.list_prompts()
                assert "paideia-operating-guide" in {
                    prompt.name for prompt in prompts.prompts
                }
                prompt = await session.get_prompt(
                    "paideia-lecture-to-quiz",
                    {"project_root": str(course_root)},
                )
                assert "Lecture-to-quiz flow" in prompt.messages[0].content.text

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

    asyncio.run(run_smoke())
