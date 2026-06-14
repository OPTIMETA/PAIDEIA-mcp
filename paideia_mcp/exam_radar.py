"""Import OPTIMETA Exam Radar exports into a PAIDEIA course graph."""

from __future__ import annotations

import datetime as _dt
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .workspace import next_timestamped_path, resolve_root


@dataclass(frozen=True)
class RadarTopic:
    name: str
    exam_prob: int
    zone: str
    lecture_signal: bool


_TOPIC_RX = re.compile(
    r"^\s*(?:[-*]|\d+[.)])\s*(?P<name>.+?)\s*"
    r"(?:·|\|)?\s*시험\s*확률\s*(?P<prob>\d{1,3})\s*%?\s*(?P<sig>.*)$"
)


def _zone_from_heading(line: str) -> str | None:
    if line.startswith("## "):
        if "골드존" in line or "지금 할 것" in line:
            return "gold"
        if "이미 다진" in line or "유지만" in line or "잘 알" in line:
            return "strong"
        if "버려도 안전" in line or "안 해도 되는" in line:
            return "skip"
    return None


def parse_exam_radar_export(export_md: str) -> dict[str, Any]:
    """Parse the fixed Exam Radar markdown export form."""

    if "exam-radar:v1" not in export_md:
        raise ValueError("missing exam-radar:v1 marker")

    course = None
    dday = None
    topics: list[RadarTopic] = []
    zone: str | None = None
    for raw in export_md.splitlines():
        line = raw.strip()
        if line.startswith("- 코스:"):
            course = line.split(":", 1)[1].strip()
            continue
        if line.startswith("- 시험까지:"):
            dday = line.split(":", 1)[1].strip()
            continue
        next_zone = _zone_from_heading(line)
        if next_zone:
            zone = next_zone
            continue
        if not zone:
            continue
        if "없음" in line and not re.search(r"\d", line):
            continue
        match = _TOPIC_RX.match(line)
        if not match:
            continue
        name = re.sub(r"\s+", " ", match.group("name")).strip()
        name = name.rstrip("·|-").strip()
        prob = max(0, min(100, int(match.group("prob"))))
        sig = "🎙" in match.group("sig") or "mic" in match.group("sig").lower()
        topics.append(RadarTopic(name=name, exam_prob=prob, zone=zone, lecture_signal=sig))

    return {
        "course": course,
        "dday": dday,
        "topics": [t.__dict__ for t in topics],
        "gold_count": sum(1 for t in topics if t.zone == "gold"),
        "strong_count": sum(1 for t in topics if t.zone == "strong"),
        "skip_count": sum(1 for t in topics if t.zone == "skip"),
    }


def _radar_markdown(course: str, dday: str | None, topics: list[RadarTopic]) -> str:
    imported = _dt.date.today().isoformat()
    rows = "\n".join(
        f"| {t.name} | {t.exam_prob}% | {t.zone} | {'mic' if t.lecture_signal else '·'} |"
        for t in sorted(topics, key=lambda x: ({"gold": 0, "strong": 1, "skip": 2}.get(x.zone, 9), -x.exam_prob))
    )
    gold = [t for t in topics if t.zone == "gold"]
    skip = [t for t in topics if t.zone == "skip"]
    gold_lines = "\n".join(f"- {t.name} ({t.exam_prob}%)" for t in sorted(gold, key=lambda x: -x.exam_prob))
    skip_lines = "\n".join(f"- {t.name} ({t.exam_prob}%)" for t in sorted(skip, key=lambda x: -x.exam_prob))
    return f"""<!-- SOURCE: Exam Radar (Alt), exam-radar:v1, course={course}, {dday or 'D-?'}, imported {imported} -->
# Lecture-emphasis signal - {course}

Imported from Exam Radar. Exam probability here is lecture emphasis
(professor spoken stress + repetition across recordings), independent of HW
density in `coverage.md`.

| Topic | Exam prob | Zone | Lecture signal |
|---|---:|---|---|
{rows}

## Now (gold zone)

High exam probability, still weak - drill these first:
{gold_lines or "- (none)"}

## Safe to drop

{skip_lines or "- (none)"}
"""


def _append_coverage_emphasis(coverage: Path, topics: list[RadarTopic]) -> int:
    """Append/replace a simple lecture-emphasis section in coverage.md."""

    if not coverage.exists():
        return 0
    text = coverage.read_text(encoding="utf-8", errors="replace")
    start = "\n## Lecture emphasis from Exam Radar\n"
    if start in text:
        text = text.split(start, 1)[0].rstrip() + "\n"
    emphasized = [t for t in topics if t.zone == "gold" or t.exam_prob >= 70]
    quiet = [t for t in topics if t.zone == "skip" or t.exam_prob < 40]
    lines = [
        start.strip(),
        "",
        "Lecture emphasis is an independent signal from Alt/Exam Radar. It annotates",
        "the HW-derived tier; it does not replace it.",
        "",
        "### Strong spoken signal",
        *(f"- {t.name} - {t.exam_prob}% ({t.zone})" for t in emphasized),
        "",
        "### Low spoken signal / safe-drop candidates",
        *(f"- {t.name} - {t.exam_prob}% ({t.zone})" for t in quiet),
        "",
    ]
    coverage.write_text(text.rstrip() + "\n\n" + "\n".join(lines), encoding="utf-8")
    return len(emphasized)


def _weakmap_markdown(course: str, topics: list[RadarTopic]) -> str:
    gold = sorted([t for t in topics if t.zone == "gold"], key=lambda x: -x.exam_prob)
    lines = "\n".join(
        f"- {t.name} ({t.exam_prob}%, from Exam Radar gold zone) - map to related §/Pk, then drill."
        for t in gold
    )
    return f"""# Weakmap - Exam Radar import

Course: {course}
Source: Exam Radar gold zone

## User-declared weaknesses

{lines or "- (none)"}

## Next drill

- Run `prepare_paideia_action` for `quiz weakmap` or `derive <topic>`.
- Once `course-index/patterns.md` exists, map each topic to concrete Pk labels.
"""


def import_exam_radar(
    project_root: str | None,
    export_md: str,
    course_name: str | None = None,
) -> dict[str, Any]:
    """Write radar.md, update coverage.md if present, and seed a weakmap."""

    parsed = parse_exam_radar_export(export_md)
    root = resolve_root(project_root)
    root.joinpath("course-index").mkdir(parents=True, exist_ok=True)
    root.joinpath("weakmap").mkdir(parents=True, exist_ok=True)

    topics = [RadarTopic(**item) for item in parsed["topics"]]
    course = course_name or parsed["course"] or "PAIDEIA course"
    radar_path = root / "course-index" / "radar.md"
    radar_path.write_text(_radar_markdown(course, parsed["dday"], topics), encoding="utf-8")

    coverage_path = root / "course-index" / "coverage.md"
    emphasized_count = _append_coverage_emphasis(coverage_path, topics)

    weakmap_path = next_timestamped_path(str(root), "weakmap", "weakmap")
    weakmap_path.write_text(_weakmap_markdown(course, topics), encoding="utf-8")

    return {
        "project_root": str(root),
        "course": course,
        "topics": len(topics),
        "gold": parsed["gold_count"],
        "strong": parsed["strong_count"],
        "skip": parsed["skip_count"],
        "radar_path": str(radar_path.relative_to(root)),
        "coverage_updated": coverage_path.exists(),
        "coverage_emphasized_count": emphasized_count,
        "weakmap_path": str(weakmap_path.relative_to(root)),
    }

