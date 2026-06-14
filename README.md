# PAIDEIA MCP

Standalone local MCP server for using PAIDEIA from Alt's local model.

Goal: make the same durable PAIDEIA course folder usable from Alt, not just
Claude Code / Codex / opencode. Alt captures lectures and runs a local model;
this MCP server owns the local folder contract, markdown artifact writes,
Exam Radar imports, repo/skill parsing, and deterministic heavy work.

```
Alt chat / local model
        |
        v
PAIDEIA MCP (local stdio)
        |
        v
~/courses/my-course/
  .course-meta
  materials/ converted/ course-index/ errors/ weakmap/
  quizzes/ mock/ twins/ chain/ derivations/ cheatsheet/
```

## Alt Setup

Install dependencies from this folder:

```bash
python3 -m pip install -e .
```

On Homebrew-managed Python, use a virtual environment if pip reports an
externally-managed environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

In Alt's MCP server dialog, choose the local stdio transport and use:

```text
명령어: /absolute/path/to/PAIDEIA-mcp/.venv/bin/python
전송 방식: 로컬 (stdio)
인수:
  -m
  paideia_mcp.bootstrap
글로벌 채팅에서 사용: on
이름: PAIDEIA
작업 디렉터리: /absolute/path/to/PAIDEIA-mcp
환경 변수:
  PAIDEIA_MCP_AUTO_INSTALL = 0
```

Important: the `인수` box takes one argument per line. Do not put
`python3 -m paideia_mcp.bootstrap` all in the `명령어` field.

If you did not create `.venv`, use this lighter setup instead:

```text
명령어: python3
전송 방식: 로컬 (stdio)
인수:
  -m
  paideia_mcp.bootstrap
글로벌 채팅에서 사용: on
이름: PAIDEIA
작업 디렉터리: /absolute/path/to/PAIDEIA-mcp
환경 변수:
  PAIDEIA_MCP_AUTO_INSTALL = 1
```

If Alt asks for a single command string instead of command/args fields:

```bash
python3 -m paideia_mcp.bootstrap
```

Transport/auth in Alt:

```text
Transport: local / stdio
Auth: none
Server URL: leave empty for stdio
```

The bootstrap entrypoint installs missing Python package dependencies into the
current user's site-packages before importing the MCP server. Set
`PAIDEIA_MCP_AUTO_INSTALL=0` to disable that behavior and fail with the manual
`pip install` command instead.

See `examples/alt-local-stdio.json` for a reference snippet. Treat it as a
field map, not a guaranteed Alt export format.

Before adding it to Alt, you can test the exact stdio path:

```bash
python3 scripts/smoke_stdio.py
```

To diagnose an install or course folder:

```bash
python3 scripts/doctor.py --project-root /absolute/path/to/course
# or, after `python3 -m pip install -e .`
paideia-doctor --project-root /absolute/path/to/course
```

The current Alt plugin SDK exposes notes/AI/storage/files, but not a plugin-side
MCP client API. The intended bridge is:

1. Alt SDK reads notes with `alt.notes.list` / `alt.notes.getContent`.
2. Alt's MCP-enabled local model or host integration calls PAIDEIA MCP with
   those note payloads.
3. PAIDEIA MCP writes the durable local course folder.

See `examples/alt-sdk-note-handoff.ts` for the SDK-side payload shape.

## How Alt Uses It

There are two classes of tools.

### Deterministic tools

These tools write/read PAIDEIA artifacts directly:

| Tool | Purpose |
|---|---|
| `init_course` | Create the course folder skeleton, `.course-meta`, `AGENTS.md`, `errors/log.md`, `.gitignore`, and optional git repo. |
| `ingest_pdfs` | Render/OCR `materials/**/*.pdf` into `converted/**`. |
| `grade_pdf` | Render/OCR one scanned answer PDF into `answers/converted/<stem>.md`. |
| `build_course_index` | Draft `course-index/{summary,patterns,coverage}.md` from `converted/**`. |
| `course_phase` | Return setup/diag/drill/mock/cram/cool, D-day, and top miss. |
| `import_exam_radar` | Parse Exam Radar's `exam-radar:v1` export and write `course-index/radar.md`, update `coverage.md` annotation, and seed a gold-zone weakmap. |
| `pattern_lookup` | Filter `course-index/patterns.md` by Pk or keyword. |
| `hwmap` | Return HW-density exam-priority rows from `coverage.md`. |
| `generate_weakmap` | Write a compact timestamped weakmap from `errors/log.md`. |
| `import_alt_note` | Take an Alt active note title/transcript and write durable `materials/lectures/*.md` plus `converted/lectures/*.md`. |
| `import_alt_notes` | Batch-import multiple Alt note payloads from `alt.notes.getContent`. |
| `bootstrap_alt_course` | Initialize a PAIDEIA course folder and import an initial Alt note batch in one call. |
| `save_action_artifact` | Save model-generated PAIDEIA outputs to canonical paths such as `quizzes/*`, `mock/*`, `derivations/*`, `cheatsheet/final.md`. |
| `save_course_index` | Save local-model analyze outputs to `course-index/summary.md`, `patterns.md`, and `coverage.md` together. |
| `save_grade_report` | Save local-model grading feedback under `answers/converted/` and append canonical error-log entries. |
| `read_artifact` / `write_artifact` / `append_error` | Safe local artifact operations under the course root. |
| `alt_workflow_guide` | Return the same Alt operating policy as a tool for clients that do not expose MCP prompts. |
| `paideia_doctor` | Diagnose install health, dependencies, course readiness, action prerequisites, and next steps. |

### PAIDEIA repo parser / action composer

These tools make all PAIDEIA actions available to Alt's local model:

| Tool | Purpose |
|---|---|
| `parse_paideia_repo` | Parse `PAIDEIA`, `PAIDEIA-codex`, or `PAIDEIA-opencode` into the canonical action catalog. |
| `list_paideia_actions` | List the 16 PAIDEIA actions Alt can perform. |
| `prepare_paideia_action` | Return the original PAIDEIA instruction, current course context, required artifacts, output hints, and write-tool contract for one action. |

The parser understands the source formats used across OPTIMETA's PAIDEIA line:
Codex skill folders (`plugins/paideia/skills/paideia-*/SKILL.md`), Claude
command markdown (`plugins/paideia/commands/*.md`), PAIDEIA-Hermes command
markdown (`commands/*.md`) plus mapped Hermes skills, and opencode prompt files
(`assets/prompts/*.md`). Canonical PAIDEIA actions are normalized to the same
16-action surface; source-only helpers such as `doctor` are preserved as
`extra_actions` in the manifest/catalog.

The important pattern is:

1. Alt calls `bootstrap_alt_course` for a new course with selected note transcripts,
   or `import_alt_notes` / `import_alt_note` for later lecture transcripts.
2. Alt calls `prepare_paideia_action(action="quiz", args="weakmap 5")`.
3. Alt's local model drafts the PAIDEIA artifact using the returned instruction.
4. Alt calls `save_action_artifact` to save standard outputs, or `write_artifact`
   for explicit paths like `course-index/summary.md`.
   For analyze, Alt calls `save_course_index`; for grading reports with mistakes,
   Alt calls `save_grade_report`.
5. If a failed/revised attempt should shape future study, Alt calls `append_error`
   or includes the errors in `save_grade_report`.

This is how plugin-like PAIDEIA behavior becomes possible without Claude Code:
MCP supplies the durable local graph, action recipes, and instructions; Alt's
local model supplies the generation step.

For model-first integration, call `alt_capability_manifest` or read
`paideia://alt/manifest`. It returns a JSON map from every canonical PAIDEIA
action to the MCP tools and local-model steps needed to execute it.

## MCP Prompts

If Alt exposes MCP prompts, the server publishes five ready-to-use operating
prompts:

```text
paideia-operating-guide
paideia-course-bootstrap
paideia-lecture-to-quiz
paideia-attempt-first-drill
paideia-exam-radar-import
```

If the client only exposes tools, call `alt_workflow_guide` with one of:
`operating-guide`, `course-bootstrap`, `lecture-to-quiz`,
`attempt-first-drill`, or `exam-radar-import`.

## MCP Resources

If Alt exposes MCP resources, the server publishes:

```text
paideia://alt/manifest       JSON action/tool manifest for local-model orchestration
paideia://alt/system-prompt  default operating prompt for Alt local models
```

## Tool Inventory

Current tool discovery should show 26 tools:

```text
ingest_pdfs
grade_pdf
build_course_index
course_phase
init_course
parse_paideia_repo
list_paideia_actions
prepare_paideia_action
list_artifacts
read_artifact
write_artifact
import_alt_note
import_alt_notes
bootstrap_alt_course
save_action_artifact
save_course_index
save_grade_report
append_error
parse_exam_radar_export
import_exam_radar
pattern_lookup
hwmap
generate_weakmap
alt_workflow_guide
alt_capability_manifest
paideia_doctor
```

## Layout

```
paideia_mcp/
├── bootstrap.py        dependency preflight + server launcher
├── server.py           stdio entrypoint, tool registration
├── repo_parser.py      parses PAIDEIA skills/prompts into an action catalog
├── action.py           composes instructions/context for Alt local models
├── alt_manifest.py     machine-readable Alt action/tool manifest
├── workspace.py        safe course-folder read/write/init and typed artifact writers
├── exam_radar.py       imports Exam Radar exam-radar:v1 exports
├── study_tools.py      hwmap/pattern/weakmap helpers
├── ingest.py           ingest_pdfs tool (dual-mode: rasterize-only vs ocr-complete)
├── grade.py            grade_pdf tool (same dual-mode)
├── analyze.py          build_course_index tool
├── phase.py            course_phase tool
└── ocr/
    ├── qwen3vl.py        local Ollama Qwen3-VL 8B
    └── tesseract.py      pytesseract eng and/or kor (whichever is installed)
```

No `openai_vision.py`: the `codex-native` engine doesn't run OCR inside the MCP. It rasterizes PDFs to `.paideia-cache/pages/<stem>/p01.png` and returns a manifest so the calling skill can read pages with Codex CLI's bundled vision — the same vision ChatGPT Plus/Pro/Business subscribers already pay for via their subscription. No `OPENAI_API_KEY`, no separate API billing.

## Engines

| Engine | Default? | MCP does OCR? | Needs | Quality on handwriting | Quality on slides |
|---|---|---|---|---|---|
| `codex-native` | yes | no — skill reads page images via Codex's built-in vision | Codex CLI logged in with ChatGPT Plus/Pro/Business/Edu/Enterprise (no extra API key) | high | high |
| `qwen3-vl` | no | yes | `ollama pull qwen3-vl:8b` (~6 GB) | high, offline | high, offline |
| `tesseract` | no | yes | `tesseract` + at least one of `tesseract-ocr-eng` / `tesseract-ocr-kor` traineddata | low | medium |

For Alt-local usage, prefer `qwen3-vl` or `tesseract` when you need OCR fully
inside the MCP process. Use `codex-native` only when a Codex client is the MCP
host and can read the returned page images with its own vision tool.

## Notes for Alt Integration

- This MCP server can write markdown files and append YAML logs inside a local
  PAIDEIA course folder.
- It does not automatically read Alt's private note database. Alt should pass
  active/selected note title/transcript/memo/summary payloads into
  `bootstrap_alt_course`, `import_alt_notes`, or `import_alt_note`.
- `import_exam_radar` already accepts the fixed markdown emitted by Exam Radar's
  copy button.
- `alt_capability_manifest` / `paideia://alt/manifest` gives Alt's local model
  the complete action-to-tool recipe table.
- `prepare_paideia_action` plus `save_action_artifact`, `save_course_index`,
  and `save_grade_report` is the bridge for the rest of PAIDEIA: quiz, twin,
  blind, chain, mock, derive, cheatsheet, weakmap, analyze, and grade workflows
  can all be driven by Alt's local model using the returned instructions plus
  canonical artifact writes.
