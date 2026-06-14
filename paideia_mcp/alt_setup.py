"""Generate exact Alt local-stdio setup fields for this MCP server."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def _package_root(package_root: str | None = None) -> Path:
    if package_root:
        return Path(package_root).expanduser().resolve()
    return Path(__file__).resolve().parents[1]


def _command_for(root: Path, prefer_venv: bool) -> tuple[str, bool]:
    venv_python = root / ".venv" / "bin" / "python"
    if prefer_venv and venv_python.exists():
        return str(venv_python), True
    if prefer_venv:
        return str(venv_python), False
    return "python3", False


def alt_setup_instructions(
    package_root: str | None = None,
    prefer_venv: bool = True,
    auto_install: bool | None = None,
    server_name: str = "PAIDEIA",
) -> dict[str, Any]:
    """Return exact values for Alt's local stdio MCP server form."""

    root = _package_root(package_root)
    command, venv_exists = _command_for(root, prefer_venv)
    if auto_install is None:
        auto_install = not prefer_venv
    env = {"PAIDEIA_MCP_AUTO_INSTALL": "1" if auto_install else "0"}
    args = ["-m", "paideia_mcp.bootstrap"]
    text = f"""Alt MCP 서버 추가 입력값

명령어
{command}

전송 방식
로컬 (stdio)

인수
-m
paideia_mcp.bootstrap

글로벌 채팅에서 사용
켜기

고급 > 이름
{server_name}

고급 > 작업 디렉터리
{root}

고급 > 환경 변수
PAIDEIA_MCP_AUTO_INSTALL = {env["PAIDEIA_MCP_AUTO_INSTALL"]}

주의
- 인수는 한 줄에 하나씩 넣으세요.
- 명령어 칸에 `python3 -m paideia_mcp.bootstrap`를 통째로 넣지 마세요.
"""
    if prefer_venv and not venv_exists:
        text += (
            "\n현재 .venv/bin/python이 아직 없습니다. 먼저 실행하세요:\n\n"
            f"cd {root}\n"
            "python3 -m venv .venv\n"
            "source .venv/bin/activate\n"
            "python -m pip install -e .\n"
        )

    return {
        "schema": "paideia-alt-setup:v1",
        "package_root": str(root),
        "transport": "stdio",
        "command": command,
        "args": args,
        "args_multiline": "\n".join(args),
        "global_chat": True,
        "name": server_name,
        "working_directory": str(root),
        "env": env,
        "prefer_venv": prefer_venv,
        "venv_python_exists": venv_exists,
        "single_command_fallback": f"{sys.executable} -m paideia_mcp.bootstrap",
        "text": text.strip(),
        "json": json.dumps(
            {
                "name": server_name,
                "transport": "stdio",
                "command": command,
                "args": args,
                "cwd": str(root),
                "auth": "none",
                "env": env,
            },
            ensure_ascii=False,
            indent=2,
        ),
    }
