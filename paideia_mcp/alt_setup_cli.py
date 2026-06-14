"""Console entrypoint for Alt local-stdio setup fields."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .alt_setup import alt_setup_instructions


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-root", type=Path)
    parser.add_argument("--no-venv", action="store_true", help="Use python3 instead of .venv/bin/python.")
    parser.add_argument("--auto-install", action="store_true", help="Set PAIDEIA_MCP_AUTO_INSTALL=1.")
    parser.add_argument("--name", default="PAIDEIA")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of the copy-paste text.")
    args = parser.parse_args()

    result = alt_setup_instructions(
        package_root=str(args.package_root.expanduser().resolve()) if args.package_root else None,
        prefer_venv=not args.no_venv,
        auto_install=True if args.auto_install else None,
        server_name=args.name,
    )
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result["text"])


if __name__ == "__main__":
    main()
