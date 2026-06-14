"""Alt-facing PAIDEIA MCP prompt templates."""

from __future__ import annotations

from typing import Any


SCENARIOS = {
    "operating-guide": "General operating policy for using PAIDEIA from Alt.",
    "course-bootstrap": "Create or attach to a local PAIDEIA course folder.",
    "lecture-to-quiz": "Import an Alt transcript, update the graph, and produce a quiz.",
    "attempt-first-drill": "Run PAIDEIA's attempt-first blind/twin workflow.",
    "exam-radar-import": "Import Exam Radar output and fold it into the course graph.",
}


def list_prompt_specs() -> list[dict[str, Any]]:
    """Return MCP prompt metadata without importing mcp.types."""

    return [
        {
            "name": f"paideia-{name}",
            "description": description,
            "arguments": [
                {
                    "name": "project_root",
                    "description": "Absolute path to the local PAIDEIA course folder.",
                    "required": False,
                }
            ],
        }
        for name, description in SCENARIOS.items()
    ]


def workflow_guide(
    scenario: str = "operating-guide",
    project_root: str | None = None,
) -> dict[str, Any]:
    """Return an Alt-local-model workflow guide for one PAIDEIA scenario."""

    key = scenario.removeprefix("paideia-")
    if key not in SCENARIOS:
        raise KeyError(f"unknown scenario: {scenario}")
    root = project_root or "<course-root>"
    common = f"""You are Alt's local model using the PAIDEIA MCP server.

Course root: {root}

Core PAIDEIA rules:
- The durable study graph lives on disk as markdown/YAML.
- Use `init_course` before writing into a new course folder.
- Use `import_alt_note` when Alt provides an active note transcript.
- Use `prepare_paideia_action` before generating any non-trivial PAIDEIA artifact.
- Use `save_action_artifact` for generated quiz/twin/chain/mock/derive/cheatsheet/weakmap/grade outputs.
- Use `save_course_index` for analyze outputs after drafting summary/patterns/coverage together.
- Use `save_grade_report` when grading produces both feedback markdown and error-log entries.
- Use `write_artifact` only for explicit paths such as `course-index/summary.md`.
- Use `append_error` for every failed or revised attempt that should shape future weakmaps.
- Preserve append-only history in `errors/log.md` and `weakmap/`.
- HW density is the primary exam-probability signal; Alt lecture emphasis is a second signal.
- For blind/twin drills, ask for the learner's strategy first. Do not reveal the solution before the attempt.
"""
    if key == "operating-guide":
        guide = common + """
Default action loop:
1. Call `course_phase` to understand the current PAIDEIA phase.
2. If the course is missing, call `init_course`.
3. If the user is looking at an Alt lecture, call `import_alt_note`.
4. Call `prepare_paideia_action` for the requested PAIDEIA action.
5. Draft the artifact using the returned instruction and context.
6. Save with `save_action_artifact` or `write_artifact`.
7. Report only the saved paths and the next recommended PAIDEIA action.
"""
    elif key == "course-bootstrap":
        guide = common + """
Bootstrap flow:
1. Ask for course name and exam date if missing.
2. Call `init_course(project_root, course_name, exam_date, exam_type, weak_zones)`.
3. Tell the user where the folder was created.
4. Next, invite them to import Alt lectures with `import_alt_note` or add PDFs under `materials/`.
"""
    elif key == "lecture-to-quiz":
        guide = common + """
Lecture-to-quiz flow:
1. Call `import_alt_note` with the active Alt note title/transcript.
2. If `course-index/patterns.md` is missing, call `prepare_paideia_action("analyze")`.
3. Draft summary/patterns/coverage and save them with `save_course_index` when analysis is needed.
4. If the user wants practice, call `prepare_paideia_action("quiz", args)`.
5. Draft problems and hidden answers.
6. Save with `save_action_artifact(action="quiz", content=..., answer_content=...)`.
"""
    elif key == "attempt-first-drill":
        guide = common + """
Attempt-first drill flow:
1. Call `prepare_paideia_action("blind" or "twin", args=<problem/topic>)`.
2. Present only the problem or strategy prompt first.
3. Ask the user for 3-5 lines: pattern, variables, end form.
4. Grade the strategy after the user answers.
5. If revised or wrong, call `append_error` with the canonical schema.
"""
    else:
        guide = common + """
Exam Radar import flow:
1. If the user has copied Exam Radar output, call `import_exam_radar(export_md=...)`.
2. If Alt only provides topics/triage as text, ask it to emit the fixed `exam-radar:v1` markdown form first.
3. After import, call `hwmap` and `generate_weakmap` if the user asks what to study now.
4. Keep lecture emphasis separate from HW-derived exam tiers.
"""
    return {"scenario": key, "description": SCENARIOS[key], "prompt": guide.strip()}
