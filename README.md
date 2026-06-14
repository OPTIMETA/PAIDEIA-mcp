<h1 align="center">ΠΑΙΔΕΙΑ · Paideia <sub>(MCP server for Alt)</sub></h1>

<p align="center">
  <strong>Your course. Your patterns. Your errors. Your cheatsheet.</strong><br>
  <em>A standalone local MCP server that brings the same permanent, editable, per-course study graph to Alt's local model — every artifact shaped by you, not by a generic syllabus. The MCP edition: the integration layer that lets PAIDEIA run from <a href="https://www.altalt.io/ko/">Alt</a>, not just from an agentic CLI.</em>
</p>

<p align="center">
  <a href="https://github.com/OPTIMETA/PAIDEIA-Alt"><img height="30" src="https://img.shields.io/badge/Exam_Radar-OPTIMETA_Alt_plugin-333333?style=for-the-badge&labelColor=000000&color=333333" alt="Exam Radar — OPTIMETA Alt plugin"></a>
</p>

<p align="center">
  <sub><em>Capture lectures with <a href="https://github.com/OPTIMETA/PAIDEIA-Alt"><strong>Exam Radar</strong></a> — OPTIMETA's Alt plugin — and study them with Paideia. This MCP server is the bridge that closes the loop inside Alt itself: import an Alt note batch, then pipe a roadmap straight in with <code>import_exam_radar</code>.</em></sub>
</p>

<p align="center">
  <img src="https://img.shields.io/github/license/OPTIMETA/PAIDEIA-mcp?style=flat-square&labelColor=000000&color=333333&cacheSeconds=3600" alt="License">
  <img src="https://img.shields.io/github/stars/OPTIMETA/PAIDEIA-mcp?style=flat-square&logo=github&logoColor=white&labelColor=000000&color=333333&cacheSeconds=3600" alt="GitHub stars">
  <img src="https://img.shields.io/github/last-commit/OPTIMETA/PAIDEIA-mcp?style=flat-square&labelColor=000000&color=333333&cacheSeconds=3600" alt="Last commit">
  <img src="https://img.shields.io/github/languages/top/OPTIMETA/PAIDEIA-mcp?style=flat-square&labelColor=000000&color=333333&cacheSeconds=3600" alt="Top language">
  &nbsp;
  <img src="https://img.shields.io/badge/MCP-000000?style=flat-square&labelColor=000000&color=000000&cacheSeconds=3600" alt="MCP">
  <img src="https://img.shields.io/badge/Alt-000000?style=flat-square&labelColor=000000&color=000000&cacheSeconds=3600" alt="Alt">
  <img src="https://img.shields.io/badge/Markdown-000000?style=flat-square&logo=markdown&logoColor=white&labelColor=000000&cacheSeconds=3600" alt="Markdown">
  <img src="https://img.shields.io/badge/Python-000000?style=flat-square&logo=python&logoColor=white&labelColor=000000&cacheSeconds=3600" alt="Python">
  <img src="https://img.shields.io/badge/Ollama-000000?style=flat-square&logo=ollama&logoColor=white&labelColor=000000&cacheSeconds=3600" alt="Ollama">
  <img src="https://img.shields.io/badge/Qwen3--VL-000000?style=flat-square&labelColor=000000&color=000000&cacheSeconds=3600" alt="Qwen3-VL">
  <img src="https://img.shields.io/badge/Tesseract-000000?style=flat-square&labelColor=000000&color=000000&cacheSeconds=3600" alt="Tesseract">
  &nbsp;
  <img src="https://img.shields.io/badge/LaTeX-000000?style=flat-square&logo=latex&logoColor=white&labelColor=000000&cacheSeconds=3600" alt="LaTeX">
  <img src="https://img.shields.io/badge/Obsidian-000000?style=flat-square&logo=obsidian&logoColor=white&labelColor=000000&cacheSeconds=3600" alt="Obsidian">
</p>

<p align="center">
  <a href="https://github.com/OPTIMETA/PAIDEIA"><strong>PAIDEIA</strong> — original Claude Code edition</a>
  &nbsp;·&nbsp;
  <a href="https://github.com/OPTIMETA/PAIDEIA-codex"><strong>PAIDEIA-codex</strong> — OpenAI Codex CLI edition</a>
  &nbsp;·&nbsp;
  <a href="https://github.com/OPTIMETA/PAIDEIA-opencode"><strong>PAIDEIA-opencode</strong> — opencode edition</a>
  &nbsp;·&nbsp;
  <a href="https://taewoopark.com"><strong>taewoopark.com</strong> — author site</a>
</p>

<p align="center">
  <sub>The Alt / MCP integration layer for the PAIDEIA study graph — same on-disk layout, same license, portable across every edition.</sub>
</p>

> **Using Alt instead of Claude Code, Codex, or opencode?** Same tool, same on-disk layout, same license — re-homed as a **local MCP server**. The original PAIDEIA is a Claude Code *plugin*; this edition is a self-contained stdio MCP server that owns the local folder contract, markdown artifact writes, Exam Radar imports, repo/skill parsing, and the deterministic heavy work, so Alt's local model can drive the same study graph. The graph it builds is byte-for-byte identical and portable across all editions.

> **Security notice.** PAIDEIA MCP installs as a local stdio MCP server — a `pip install -e .` Python package you point Alt at — and never asks you to download a `.zip`, run an `.exe`, or use any installer. Any other repository using the PAIDEIA name is not affiliated with this project unless it is explicitly linked from this README.

<p align="center">
  <em>Generic study tools teach you the average syllabus. Paideia teaches you <strong>your</strong> syllabus —<br>
  from your professor's notes, your HW emphases, your handwriting, your errors. Every artifact is a markdown file you can edit.</em>
</p>

---

## What Paideia means

In ancient Greece, **Παιδεία** was never the deposit of facts into a passive student. It was the lifelong formation of a complete human being — through structured encounter with primary texts, guided practice under a master, and reflective dialogue that folds feedback into deeper revision.

This MCP server implements that cycle for the specific, bounded problem of **exam preparation** in math, physics, and engineering courses:

```
  ingest ──▶ analyze ──▶ drill ──▶ grade ──▶ weakmap ──▶ cheatsheet
     ▲                                                        │
     └────────────────── feedback loop ───────────────────────┘
```

Every stage produces a markdown artifact that lives in your course folder forever. Nothing is ephemeral. Nothing is hidden behind an API. Nothing stops working when the next funding winter hits.

---

## Why an MCP edition

PAIDEIA was born as a Claude Code plugin. The heavy lifting — parallel vision ingest, strategy grading, pattern extraction from *your* solutions — never depended on Claude specifically; it depended on *any* host that can run instructions against a course folder. Alt captures lectures and runs a local model, but it is not an agentic CLI with skills and subagents. So instead of porting the verbs, this edition re-homes the deterministic core into a **standalone local stdio MCP server**.

Goal: make the same durable PAIDEIA course folder usable from Alt, not just Claude Code / Codex / opencode. The server owns the local folder contract, markdown artifact writes, Exam Radar imports, repo/skill parsing, and deterministic heavy work; Alt's local model supplies the generation step.

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

The study graph on disk is **byte-for-byte the same** as every other edition. `course-index/patterns.md`, `errors/log.md`, `weakmap/weakmap_<ts>.md`, `cheatsheet/final.md` — all the artifacts the Claude edition writes, this edition also writes, in the same format. Fork a course folder between editions and the new runner picks up without friction.

---

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

You can print these exact fields for your current checkout:

```bash
python3 scripts/alt_setup.py
# or, after install
paideia-alt-setup
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

---

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

---

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

---

## MCP Resources

If Alt exposes MCP resources, the server publishes:

```text
paideia://alt/manifest       JSON action/tool manifest for local-model orchestration
paideia://alt/system-prompt  default operating prompt for Alt local models
```

---

## Tool Inventory

Current tool discovery should show 54 tools: 27 canonical tool names plus 27
Alt-search namespace aliases. If Alt searches for `PAIDEIA__init_course`, use
the alias directly; it routes to the same handler as `init_course`.

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
alt_setup_instructions
paideia_doctor
```

Every canonical tool above is also exposed with a `PAIDEIA__` prefix, for
example `PAIDEIA__init_course`, `PAIDEIA__write_artifact`, and
`PAIDEIA__alt_setup_instructions`. These aliases exist because Alt's tool
search may look for server-prefixed names.

In Alt chat, call PAIDEIA MCP tools directly by name. Do not use
`alt_tool_search_bm25` with `category: "alt"` to find PAIDEIA tools; that
category searches Alt-native note tools, not connected MCP server tools.

---

## Engines

| Engine | Default? | MCP does OCR? | Needs | Quality on handwriting | Quality on slides |
|---|---|---|---|---|---|
| `codex-native` | yes | no — skill reads page images via Codex's built-in vision | Codex CLI logged in with ChatGPT Plus/Pro/Business/Edu/Enterprise (no extra API key) | high | high |
| `qwen3-vl` | no | yes | `ollama pull qwen3-vl:8b` (~6 GB) | high, offline | high, offline |
| `tesseract` | no | yes | `tesseract` + at least one of `tesseract-ocr-eng` / `tesseract-ocr-kor` traineddata | low | medium |

For Alt-local usage, prefer `qwen3-vl` or `tesseract` when you need OCR fully
inside the MCP process. Use `codex-native` only when a Codex client is the MCP
host and can read the returned page images with its own vision tool.

---

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

---

## What ships

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

---

## Connect

<p align="center">
  <a href="https://github.com/TaewoooPark"><img src="https://img.shields.io/badge/-GitHub-181717?style=for-the-badge&logo=github&logoColor=white&cacheSeconds=3600" alt="GitHub"></a>
  <a href="https://x.com/theoverstrcture"><img src="https://img.shields.io/badge/-X-000000?style=for-the-badge&logo=x&logoColor=white&cacheSeconds=3600" alt="X (Twitter)"></a>
  <a href="https://www.linkedin.com/in/taewoo-park-427a05352"><img src="https://img.shields.io/badge/-LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white&cacheSeconds=3600" alt="LinkedIn"></a>
  <a href="https://www.instagram.com/t.wo0_x/"><img src="https://img.shields.io/badge/-Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white&cacheSeconds=3600" alt="Instagram"></a>
  <a href="https://taewoopark.com"><img src="https://img.shields.io/badge/-taewoopark.com-000000?style=for-the-badge&logo=safari&logoColor=white&cacheSeconds=3600" alt="Personal site"></a>
  <a href="mailto:ptw151125@kaist.ac.kr"><img src="https://img.shields.io/badge/-Email-D14836?style=for-the-badge&logo=gmail&logoColor=white&cacheSeconds=3600" alt="Email"></a>
</p>

---

## License

MIT. Use freely. Fork and modify for your own courses — the point of PAIDEIA is that the study graph it builds is yours to shape, not a fixed product you have to live with.

---

<p align="center">
  <em>Generic curricula teach the average student. Παιδεία — formation, one student at a time.</em>
</p>
