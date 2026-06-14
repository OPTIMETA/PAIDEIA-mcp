"""Source-tree wrapper for the Alt setup instruction CLI."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from paideia_mcp.alt_setup_cli import main


if __name__ == "__main__":
    main()
