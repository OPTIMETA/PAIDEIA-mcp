"""Smoke-test the PAIDEIA MCP stdio server through a real MCP client."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import tempfile
from pathlib import Path

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


async def _run(course_root: Path) -> None:
    package_root = Path(__file__).resolve().parents[1]
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "paideia_mcp.bootstrap"],
        cwd=str(package_root),
        env={"PAIDEIA_MCP_AUTO_INSTALL": "0"},
    )

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            prompts = await session.list_prompts()
            resources = await session.list_resources()
            print(f"tools: {len(tools.tools)}")
            print(", ".join(tool.name for tool in tools.tools))
            print(f"prompts: {len(prompts.prompts)}")
            print(", ".join(prompt.name for prompt in prompts.prompts))
            print(f"resources: {len(resources.resources)}")
            print(", ".join(resource.name for resource in resources.resources))

            manifest = await session.read_resource("paideia://alt/manifest")
            manifest_json = json.loads(manifest.contents[0].text)
            print(f"manifest actions: {manifest_json['action_count']}")

            created = await session.call_tool(
                "init_course",
                {
                    "project_root": str(course_root),
                    "course_name": "PAIDEIA MCP Smoke",
                    "exam_date": "2099-01-01",
                    "git_init": False,
                },
            )
            print(json.dumps(json.loads(created.content[0].text), indent=2))

            imported = await session.call_tool(
                "import_alt_notes",
                {
                    "project_root": str(course_root),
                    "notes": [
                        {
                            "note_id": "smoke-1",
                            "title": "Smoke lecture",
                            "transcript": "This transcript verifies Alt note batch handoff.",
                        }
                    ],
                },
            )
            imported_json = json.loads(imported.content[0].text)
            print(f"imported notes: {imported_json['imported_count']}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--course-root",
        type=Path,
        help="Optional course folder for init_course. Defaults to a temporary folder.",
    )
    args = parser.parse_args()

    if args.course_root is None:
        with tempfile.TemporaryDirectory(prefix="paideia-mcp-smoke-") as tmp:
            asyncio.run(_run(Path(tmp) / "course"))
    else:
        asyncio.run(_run(args.course_root.expanduser().resolve()))


if __name__ == "__main__":
    main()
