<h1 align="center">ΠΑΙΔΕΙΑ · Paideia <sub>(Alt용 MCP 서버)</sub></h1>

<p align="center">
  <strong>당신의 과목, 당신의 패턴, 당신의 오답, 당신의 치트시트.</strong><br>
  <em>같은 영속적·편집 가능한 과목별 학습 그래프를 Alt의 로컬 모델로 가져오는 독립형 로컬 MCP 서버입니다 — 모든 산출물이 일반 실러버스가 아니라 당신의 손끝에서 빚어집니다. MCP 에디션: PAIDEIA를 에이전트 CLI뿐 아니라 <a href="https://www.altalt.io/ko/">Alt</a>에서도 돌릴 수 있게 해 주는 통합 레이어입니다.</em>
</p>

<p align="center">
  <a href="https://github.com/OPTIMETA/PAIDEIA-Alt"><img height="30" src="https://img.shields.io/badge/Exam_Radar-OPTIMETA_Alt_plugin-333333?style=for-the-badge&labelColor=000000&color=333333" alt="Exam Radar — OPTIMETA Alt 플러그인"></a>
</p>

<p align="center">
  <sub><em>강의는 <a href="https://github.com/OPTIMETA/PAIDEIA-Alt"><strong>Exam Radar</strong></a>(OPTIMETA의 Alt 플러그인)로 잡고, 공부는 Paideia로 합니다. 이 MCP 서버는 그 고리를 Alt 안에서 닫아 주는 다리입니다 — Alt 노트 묶음을 가져온 뒤, 로드맵은 <code>import_exam_radar</code>로 곧장 흘려보내세요.</em></sub>
</p>

<p align="center">
  <img src="https://img.shields.io/github/license/OPTIMETA/PAIDEIA-mcp?style=flat-square&labelColor=000000&color=333333&cacheSeconds=3600" alt="라이선스">
  <img src="https://img.shields.io/github/stars/OPTIMETA/PAIDEIA-mcp?style=flat-square&logo=github&logoColor=white&labelColor=000000&color=333333&cacheSeconds=3600" alt="GitHub 스타 수">
  <img src="https://img.shields.io/github/last-commit/OPTIMETA/PAIDEIA-mcp?style=flat-square&labelColor=000000&color=333333&cacheSeconds=3600" alt="최근 커밋">
  <img src="https://img.shields.io/github/languages/top/OPTIMETA/PAIDEIA-mcp?style=flat-square&labelColor=000000&color=333333&cacheSeconds=3600" alt="주요 언어">
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
  <a href="./README.md">English README</a>
  &nbsp;·&nbsp;
  <a href="https://github.com/OPTIMETA/PAIDEIA"><strong>PAIDEIA</strong> — 원본 Claude Code 에디션</a>
  &nbsp;·&nbsp;
  <a href="https://github.com/OPTIMETA/PAIDEIA-codex"><strong>PAIDEIA-codex</strong> — OpenAI Codex CLI 에디션</a>
  &nbsp;·&nbsp;
  <a href="https://github.com/OPTIMETA/PAIDEIA-opencode"><strong>PAIDEIA-opencode</strong> — opencode 에디션</a>
</p>

<p align="center">
  <sub>PAIDEIA 학습 그래프를 위한 Alt / MCP 통합 레이어 — 동일한 디스크 레이아웃, 동일한 라이선스, 모든 에디션 간 이식 가능.</sub>
</p>

> **Claude Code·Codex·opencode 대신 Alt를 쓰시나요?** 같은 도구, 같은 디스크 레이아웃, 같은 라이선스 — **로컬 MCP 서버**로 다시 자리 잡았습니다. 원본 PAIDEIA는 Claude Code *플러그인*이지만, 이 에디션은 로컬 폴더 계약·마크다운 산출물 기록·Exam Radar 가져오기·레포/스킬 파싱·결정론적 무거운 작업을 직접 소유하는 독립형 stdio MCP 서버라서, Alt의 로컬 모델이 같은 학습 그래프를 구동할 수 있습니다. 만들어지는 그래프는 바이트 단위로 동일하며 모든 에디션 간 이식됩니다.

> **보안 공지.** PAIDEIA MCP는 로컬 stdio MCP 서버 — Alt가 가리키는 `pip install -e .` 파이썬 패키지 — 로 설치되며, `.zip`을 받거나 `.exe`를 실행하거나 별도 설치 프로그램을 쓰라고 요구하지 않습니다. PAIDEIA 이름을 쓰는 다른 저장소가 이 README에서 명시적으로 링크되어 있지 않다면, 그것은 이 프로젝트와 무관합니다.

<p align="center">
  <em>일반적인 학습 도구는 평균적인 실러버스를 가르칩니다. Paideia는 <strong>당신의</strong> 실러버스를 가르칩니다 —<br>
  당신의 교수님 강의노트, 당신의 숙제 경향, 당신의 필기, 당신의 오답에서 출발해서요. 모든 산출물은 당신이 직접 편집할 수 있는 마크다운 파일입니다.</em>
</p>

---

## Paideia라는 이름에 대하여

고대 그리스에서 **Παιδεία(파이데이아)**는 수동적인 학생에게 사실을 주입하는 일이 아니었습니다. 그것은 원전과의 구조화된 만남, 스승 아래에서의 연습, 그리고 피드백을 더 깊은 수정으로 되돌려 보내는 성찰적 대화를 통한 — 한 인간을 평생에 걸쳐 형성해 가는 일이었습니다.

이 MCP 서버는 그 순환을 **수학·물리·공학 과목의 시험 준비**라는 구체적이고 한정된 문제에 맞추어 구현합니다.

```
  ingest ──▶ analyze ──▶ drill ──▶ grade ──▶ weakmap ──▶ cheatsheet
     ▲                                                        │
     └────────────────── feedback loop ───────────────────────┘
```

모든 단계는 당신의 과목 폴더에 영원히 남는 마크다운 산출물을 만듭니다. 사라지는 것은 없습니다. API 뒤에 숨겨지는 것도 없습니다. 다음 자금 한파가 와도 멈추는 것은 없습니다.

---

## 왜 MCP 에디션인가

PAIDEIA는 Claude Code 플러그인으로 태어났습니다. 무거운 작업 — 병렬 비전 인제스트, 전략 채점, *당신의* 풀이에서 뽑아낸 패턴 추출 — 은 Claude 자체에 의존한 적이 없습니다. 그것은 과목 폴더를 상대로 지시를 실행할 수 있는 *어떤* 호스트에든 의존했습니다. Alt는 강의를 캡처하고 로컬 모델을 돌리지만, 스킬과 서브에이전트를 갖춘 에이전트 CLI는 아닙니다. 그래서 이 에디션은 동사를 이식하는 대신, 결정론적 코어를 **독립형 로컬 stdio MCP 서버**로 다시 자리 잡게 했습니다.

목표: 같은 영속적 PAIDEIA 과목 폴더를 Claude Code / Codex / opencode뿐 아니라 Alt에서도 쓸 수 있게 하는 것. 서버는 로컬 폴더 계약·마크다운 산출물 기록·Exam Radar 가져오기·레포/스킬 파싱·결정론적 무거운 작업을 소유하고, 생성 단계는 Alt의 로컬 모델이 맡습니다.

```
Alt 채팅 / 로컬 모델
        |
        v
PAIDEIA MCP (로컬 stdio)
        |
        v
~/courses/my-course/
  .course-meta
  materials/ converted/ course-index/ errors/ weakmap/
  quizzes/ mock/ twins/ chain/ derivations/ cheatsheet/
```

디스크 위의 학습 그래프는 다른 모든 에디션과 **바이트 단위로 동일**합니다. `course-index/patterns.md`, `errors/log.md`, `weakmap/weakmap_<ts>.md`, `cheatsheet/final.md` — Claude 에디션이 기록하는 모든 산출물을 이 에디션도 같은 포맷으로 기록합니다. 과목 폴더를 에디션 사이에서 포크해도 새 러너가 마찰 없이 이어받습니다.

---

## Alt 설정

이 폴더에서 의존성을 설치합니다.

```bash
python3 -m pip install -e .
```

Homebrew로 관리되는 Python에서 pip가 externally-managed 환경 오류를 내면 가상환경을 사용합니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Alt의 MCP 서버 대화상자에서 로컬 stdio 전송 방식을 골라 다음을 사용합니다.

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

현재 체크아웃에 맞는 정확한 필드 값을 출력할 수 있습니다.

```bash
python3 scripts/alt_setup.py
# 또는 설치 이후
paideia-alt-setup
```

중요: `인수` 칸은 한 줄에 인수 하나씩 받습니다. `python3 -m paideia_mcp.bootstrap`을 통째로 `명령어` 칸에 넣지 마세요.

`.venv`를 만들지 않았다면 더 가벼운 다음 설정을 대신 사용합니다.

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

Alt가 command/args 필드 대신 단일 명령 문자열을 요구하면:

```bash
python3 -m paideia_mcp.bootstrap
```

Alt에서의 전송/인증:

```text
Transport: local / stdio
Auth: none
Server URL: stdio면 비워 둠
```

bootstrap 엔트리포인트는 MCP 서버를 임포트하기 전에, 빠진 파이썬 패키지 의존성을 현재 사용자의 site-packages에 설치합니다. `PAIDEIA_MCP_AUTO_INSTALL=0`으로 이 동작을 끄면, 수동 `pip install` 명령을 안내하며 대신 실패합니다.

참고용 스니펫은 `examples/alt-local-stdio.json`을 보세요. 보장된 Alt 내보내기 포맷이 아니라 필드 맵으로 다루세요.

Alt에 추가하기 전에, 정확한 stdio 경로를 테스트할 수 있습니다.

```bash
python3 scripts/smoke_stdio.py
```

설치나 과목 폴더를 진단하려면:

```bash
python3 scripts/doctor.py --project-root /absolute/path/to/course
# 또는 `python3 -m pip install -e .` 이후
paideia-doctor --project-root /absolute/path/to/course
```

현재 Alt 플러그인 SDK는 notes/AI/storage/files는 노출하지만, 플러그인 측 MCP 클라이언트 API는 노출하지 않습니다. 의도된 다리는 이렇습니다.

1. Alt SDK가 `alt.notes.list` / `alt.notes.getContent`로 노트를 읽습니다.
2. Alt의 MCP 지원 로컬 모델 또는 호스트 통합이 그 노트 페이로드를 들고 PAIDEIA MCP를 호출합니다.
3. PAIDEIA MCP가 영속적 로컬 과목 폴더를 기록합니다.

SDK 측 페이로드 형태는 `examples/alt-sdk-note-handoff.ts`를 보세요.

---

## Alt가 사용하는 방식

도구는 두 부류입니다.

### 결정론적 도구

이 도구들은 PAIDEIA 산출물을 직접 기록/읽습니다.

| 도구 | 용도 |
|---|---|
| `init_course` | 과목 폴더 골격, `.course-meta`, `AGENTS.md`, `errors/log.md`, `.gitignore`, 선택적 git 레포 생성. |
| `ingest_pdfs` | `materials/**/*.pdf`를 `converted/**`로 렌더/OCR. |
| `grade_pdf` | 스캔한 답안 PDF 하나를 `answers/converted/<stem>.md`로 렌더/OCR. |
| `build_course_index` | `converted/**`에서 `course-index/{summary,patterns,coverage}.md` 초안 작성. |
| `course_phase` | setup/diag/drill/mock/cram/cool, D-day, 최다 오답 반환. |
| `import_exam_radar` | Exam Radar의 `exam-radar:v1` 내보내기를 파싱해 `course-index/radar.md`를 쓰고, `coverage.md` 주석을 갱신하고, gold-zone weakmap을 시드. |
| `pattern_lookup` | `course-index/patterns.md`를 Pk 또는 키워드로 필터. |
| `hwmap` | `coverage.md`에서 HW 밀도 기반 시험 우선순위 행 반환. |
| `generate_weakmap` | `errors/log.md`에서 타임스탬프가 찍힌 간결한 weakmap 작성. |
| `import_alt_note` | Alt 활성 노트의 제목/전사를 받아 영속적 `materials/lectures/*.md`와 `converted/lectures/*.md` 기록. |
| `import_alt_notes` | `alt.notes.getContent`의 여러 Alt 노트 페이로드를 일괄 가져오기. |
| `bootstrap_alt_course` | PAIDEIA 과목 폴더 초기화와 초기 Alt 노트 묶음 가져오기를 한 번에. |
| `save_action_artifact` | 모델이 생성한 PAIDEIA 출력을 `quizzes/*`, `mock/*`, `derivations/*`, `cheatsheet/final.md` 같은 정규 경로에 저장. |
| `save_course_index` | 로컬 모델 analyze 출력을 `course-index/summary.md`, `patterns.md`, `coverage.md`에 함께 저장. |
| `save_grade_report` | 로컬 모델 채점 피드백을 `answers/converted/` 아래 저장하고 정규 오답 로그 항목 추가. |
| `read_artifact` / `write_artifact` / `append_error` | 과목 루트 안에서의 안전한 로컬 산출물 작업. |
| `alt_workflow_guide` | MCP 프롬프트를 노출하지 않는 클라이언트를 위해, 같은 Alt 운영 정책을 도구로 반환. |
| `paideia_doctor` | 설치 상태, 의존성, 과목 준비도, 액션 사전조건, 다음 단계 진단. |

### PAIDEIA 레포 파서 / 액션 컴포저

이 도구들은 모든 PAIDEIA 액션을 Alt의 로컬 모델이 쓸 수 있게 합니다.

| 도구 | 용도 |
|---|---|
| `parse_paideia_repo` | `PAIDEIA`, `PAIDEIA-codex`, `PAIDEIA-opencode`를 정규 액션 카탈로그로 파싱. |
| `list_paideia_actions` | Alt가 수행할 수 있는 16개 PAIDEIA 액션 나열. |
| `prepare_paideia_action` | 한 액션에 대한 원본 PAIDEIA 지시, 현재 과목 컨텍스트, 필요 산출물, 출력 힌트, 기록 도구 계약 반환. |

파서는 OPTIMETA PAIDEIA 라인 전반의 소스 포맷을 이해합니다:
Codex 스킬 폴더(`plugins/paideia/skills/paideia-*/SKILL.md`), Claude
커맨드 마크다운(`plugins/paideia/commands/*.md`), PAIDEIA-Hermes 커맨드
마크다운(`commands/*.md`)과 매핑된 Hermes 스킬, opencode 프롬프트 파일
(`assets/prompts/*.md`). 정규 PAIDEIA 액션은 같은 16개 액션 표면으로
정규화되며, `doctor` 같은 소스 전용 헬퍼는 매니페스트/카탈로그에서
`extra_actions`로 보존됩니다.

핵심 패턴은 이렇습니다.

1. Alt가 새 과목에 대해 선택한 노트 전사로 `bootstrap_alt_course`를,
   이후 강의 전사에는 `import_alt_notes` / `import_alt_note`를 호출.
2. Alt가 `prepare_paideia_action(action="quiz", args="weakmap 5")`를 호출.
3. Alt의 로컬 모델이 반환된 지시로 PAIDEIA 산출물을 작성.
4. Alt가 표준 출력은 `save_action_artifact`로, `course-index/summary.md` 같은
   명시적 경로는 `write_artifact`로 저장.
   analyze는 `save_course_index`로, 오답이 있는 채점 보고서는 `save_grade_report`로.
5. 실패/수정된 시도가 이후 학습을 형성해야 한다면, Alt가 `append_error`를 호출하거나
   `save_grade_report`에 오답을 포함.

이것이 Claude Code 없이 플러그인 같은 PAIDEIA 동작을 가능하게 하는 방식입니다.
MCP는 영속적 로컬 그래프·액션 레시피·지시를 공급하고, Alt의 로컬 모델은 생성 단계를 공급합니다.

모델 우선 통합에는 `alt_capability_manifest`를 호출하거나 `paideia://alt/manifest`를 읽으세요.
모든 정규 PAIDEIA 액션을, 그것을 실행하는 데 필요한 MCP 도구와 로컬 모델 단계로 매핑한 JSON을 반환합니다.

---

## MCP 프롬프트

Alt가 MCP 프롬프트를 노출하면, 서버는 즉시 쓸 수 있는 운영 프롬프트 다섯 개를 게시합니다.

```text
paideia-operating-guide
paideia-course-bootstrap
paideia-lecture-to-quiz
paideia-attempt-first-drill
paideia-exam-radar-import
```

클라이언트가 도구만 노출한다면, `alt_workflow_guide`를 다음 중 하나로 호출하세요:
`operating-guide`, `course-bootstrap`, `lecture-to-quiz`,
`attempt-first-drill`, `exam-radar-import`.

---

## MCP 리소스

Alt가 MCP 리소스를 노출하면, 서버는 다음을 게시합니다.

```text
paideia://alt/manifest       로컬 모델 오케스트레이션용 JSON 액션/도구 매니페스트
paideia://alt/system-prompt  Alt 로컬 모델용 기본 운영 프롬프트
```

---

## 도구 목록

현재 도구 탐색에는 54개 도구가 보여야 합니다: 정규 도구 이름 27개에 Alt-검색
네임스페이스 별칭 27개. Alt가 `PAIDEIA__init_course`를 검색하면, 그 별칭을 바로
쓰세요 — `init_course`와 같은 핸들러로 라우팅됩니다.

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

위 모든 정규 도구는 `PAIDEIA__` 접두사로도 노출됩니다. 예: `PAIDEIA__init_course`,
`PAIDEIA__write_artifact`, `PAIDEIA__alt_setup_instructions`. 이 별칭들은 Alt의 도구
검색이 서버 접두사가 붙은 이름을 찾을 수 있기 때문에 존재합니다.

Alt 채팅에서는 PAIDEIA MCP 도구를 이름으로 직접 호출하세요. PAIDEIA 도구를 찾으려고
`alt_tool_search_bm25`를 `category: "alt"`로 쓰지 마세요. 그 카테고리는 연결된 MCP
서버 도구가 아니라 Alt 네이티브 노트 도구를 검색합니다.

---

## 엔진

두 엔진 모두 **MCP 프로세스 안에서** OCR을 끝냅니다 — 외부 에이전트의 비전
단계 없이 완성된 마크다운을 과목 폴더에 씁니다. 이건 Alt에 중요한데, Alt 플러그인
샌드박스는 페이지 이미지를 읽을 수 없어 호스트-비전 엔진은 여기서 무동작이기
때문입니다. 그래서 PAIDEIA MCP가 OCR을 직접 합니다.

| 엔진 | 기본값? | 필요 조건 | 필기 품질 | 슬라이드 품질 |
|---|---|---|---|---|
| `qwen3-vl` | **예** | `ollama pull qwen3-vl:8b` (~6 GB) | 높음, 오프라인 | 높음, 오프라인 |
| `tesseract` | 아니오 | `tesseract` + `tesseract-ocr-eng` / `tesseract-ocr-kor` traineddata 중 하나 이상 | 낮음 | 중간 |

`qwen3-vl`이 기본값입니다. Ollama가 닿지 않거나 모델이 안 받아졌을 때는 **자동으로
`tesseract`로 폴백**해 기본 설치로도 결과가 나옵니다. provenance 헤더와 채점 tier에는
실제로 동작한 엔진이 기록됩니다. 가장 가벼운 무다운로드 경로를 원하면 `tesseract`를
바로 고르세요.

---

## Alt 통합 참고

- 이 MCP 서버는 로컬 PAIDEIA 과목 폴더 안에 마크다운 파일을 쓰고 YAML 로그를
  덧붙일 수 있습니다.
- Alt의 비공개 노트 데이터베이스를 자동으로 읽지는 않습니다. Alt가 활성/선택된
  노트의 제목/전사/메모/요약 페이로드를 `bootstrap_alt_course`,
  `import_alt_notes`, `import_alt_note`로 넘겨야 합니다.
- `import_exam_radar`는 Exam Radar의 복사 버튼이 내보내는 고정 마크다운을 이미
  받아들입니다.
- `alt_capability_manifest` / `paideia://alt/manifest`는 Alt의 로컬 모델에게
  완전한 액션-도구 레시피 표를 줍니다.
- `prepare_paideia_action`에 `save_action_artifact`, `save_course_index`,
  `save_grade_report`를 더하면 나머지 PAIDEIA로 가는 다리가 됩니다: quiz, twin,
  blind, chain, mock, derive, cheatsheet, weakmap, analyze, grade 워크플로우 모두
  반환된 지시와 정규 산출물 기록을 써서 Alt의 로컬 모델로 구동할 수 있습니다.

---

## 무엇이 들어 있나

```
paideia_mcp/
├── bootstrap.py        의존성 사전점검 + 서버 런처
├── server.py           stdio 엔트리포인트, 도구 등록
├── repo_parser.py      PAIDEIA 스킬/프롬프트를 액션 카탈로그로 파싱
├── action.py           Alt 로컬 모델용 지시/컨텍스트 구성
├── alt_manifest.py     기계 판독용 Alt 액션/도구 매니페스트
├── workspace.py        안전한 과목 폴더 읽기/쓰기/초기화 + 타입별 산출물 기록기
├── exam_radar.py       Exam Radar exam-radar:v1 내보내기 가져오기
├── study_tools.py      hwmap/pattern/weakmap 헬퍼
├── ingest.py           ingest_pdfs 도구 (렌더 + in-process OCR → converted/**)
├── grade.py            grade_pdf 도구 (렌더 + in-process OCR → answers/converted/)
├── analyze.py          build_course_index 도구
├── phase.py            course_phase 도구
└── ocr/
    ├── __init__.py      엔진 디스패치 + qwen3-vl→tesseract 폴백
    ├── qwen3vl.py        로컬 Ollama Qwen3-VL 8B
    └── tesseract.py      pytesseract eng 및/또는 kor (설치된 것)
```

OCR은 이 두 엔진으로 MCP 프로세스 안에서 전부 처리됩니다 — 호스트-비전
(`codex-native` / `openai_vision.py`) 경로는 없습니다. Alt 플러그인 샌드박스가
페이지 이미지를 못 읽어서, OCR을 호스트에 미루는 엔진은 여기서 아무것도 만들지
못하기 때문입니다. `qwen3-vl`(기본값)은 Ollama가 없으면 `tesseract`로 폴백하므로,
두 엔진 세트만으로 자족적입니다.

---

## 연결

<p align="center">
  <a href="https://github.com/TaewoooPark"><img src="https://img.shields.io/badge/-GitHub-181717?style=for-the-badge&logo=github&logoColor=white&cacheSeconds=3600" alt="GitHub"></a>
  <a href="https://x.com/theoverstrcture"><img src="https://img.shields.io/badge/-X-000000?style=for-the-badge&logo=x&logoColor=white&cacheSeconds=3600" alt="X (Twitter)"></a>
  <a href="https://www.linkedin.com/in/taewoo-park-427a05352"><img src="https://img.shields.io/badge/-LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white&cacheSeconds=3600" alt="LinkedIn"></a>
  <a href="https://www.instagram.com/t.wo0_x/"><img src="https://img.shields.io/badge/-Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white&cacheSeconds=3600" alt="Instagram"></a>
  <a href="https://taewoopark.com"><img src="https://img.shields.io/badge/-taewoopark.com-000000?style=for-the-badge&logo=safari&logoColor=white&cacheSeconds=3600" alt="개인 사이트"></a>
  <a href="mailto:ptw151125@kaist.ac.kr"><img src="https://img.shields.io/badge/-Email-D14836?style=for-the-badge&logo=gmail&logoColor=white&cacheSeconds=3600" alt="이메일"></a>
</p>

---

## 라이선스

MIT. 자유롭게 쓰세요. 당신의 과목에 맞게 포크하고 수정하세요 — PAIDEIA의 핵심은, 그것이 만드는 학습 그래프가 당신이 감수해야 할 고정된 제품이 아니라 당신이 빚어 가는 당신의 것이라는 데 있습니다.

---

<p align="center">
  <em>일반적인 커리큘럼은 평균적인 학생을 가르칩니다. Παιδεία — 형성, 한 번에 한 학생씩.</em>
</p>
