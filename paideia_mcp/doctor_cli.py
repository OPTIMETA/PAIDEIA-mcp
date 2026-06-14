"""Console entrypoint for PAIDEIA MCP diagnostics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .doctor import paideia_doctor


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--project-root",
        type=Path,
        help="Course folder to diagnose. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        help="Optional PAIDEIA / PAIDEIA-codex / PAIDEIA-opencode repo root.",
    )
    args = parser.parse_args()

    result = paideia_doctor(
        project_root=str(args.project_root.expanduser().resolve()) if args.project_root else None,
        repo_root=str(args.repo_root.expanduser().resolve()) if args.repo_root else None,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
