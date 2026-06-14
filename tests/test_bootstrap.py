"""Regression tests for the PAIDEIA bootstrap script."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from paideia_mcp.workspace import init_course


@pytest.mark.skipif(shutil.which("git") is None, reason="git not installed")
def test_bootstrap_merges_gitignore_into_existing_repo(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text("existing-entry\n", encoding="utf-8")

    init_course(
        str(tmp_path),
        course_name="Bootstrap Smoke",
        exam_date="2099-01-01",
        exam_type="final",
        weak_zones="unknown",
        ocr_engine="codex-native",
    )

    body = gitignore.read_text(encoding="utf-8")
    assert "existing-entry" in body
    assert "answers/*.pdf" in body
    assert "errors/log.md" not in body
    assert "answers/converted/*.md" not in body
