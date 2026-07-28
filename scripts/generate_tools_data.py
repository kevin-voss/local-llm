#!/usr/bin/env python3
"""Generate data/style/tools.jsonl (≥30 tool-trace rows)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "style" / "tools.jsonl"
SYSTEM = (ROOT / "data" / "style" / "SYSTEM_TOOLS.md").read_text(encoding="utf-8").strip()


def fence(obj: dict) -> str:
    return "```json\n" + json.dumps(obj, ensure_ascii=False) + "\n```"


def row(*messages: dict) -> dict:
    return {"messages": [{"role": "system", "content": SYSTEM}, *messages]}


def main() -> int:
    rows: list[dict] = []

    # --- single-step mkdir ---
    for name in ("hello", "demo", "app", "src", "pkg", "util", "scripts", "notes"):
        rows.append(
            row(
                {"role": "user", "content": f"Create a folder named {name}"},
                {"role": "assistant", "content": fence({"tool": "mkdir", "path": name})},
            )
        )

    # --- single-step write_file ---
    writes = [
        (
            "Create hello/main.py that prints Hello",
            "hello/main.py",
            "print('Hello')\n",
        ),
        (
            "Write demo/app.py that prints hi",
            "demo/app.py",
            "print('hi')\n",
        ),
        (
            "Write notes/README.md with title Demo",
            "notes/README.md",
            "# Demo\n",
        ),
        (
            "Create util/add.py with an add function",
            "util/add.py",
            "def add(a, b):\n    return a + b\n",
        ),
        (
            "Write scripts/hello.py that prints Hello world",
            "scripts/hello.py",
            "print('Hello world')\n",
        ),
        (
            "Create pkg/__init__.py empty",
            "pkg/__init__.py",
            "",
        ),
        (
            "Write app/main.py that prints ok",
            "app/main.py",
            "print('ok')\n",
        ),
        (
            "Create src/greet.py with greet()",
            "src/greet.py",
            "def greet(name):\n    return f'hi {name}'\n",
        ),
    ]
    for user, path, content in writes:
        rows.append(
            row(
                {"role": "user", "content": user},
                {
                    "role": "assistant",
                    "content": fence(
                        {"tool": "write_file", "path": path, "content": content}
                    ),
                },
            )
        )

    # --- read_file ---
    for path in ("hello/main.py", "demo/app.py", "notes/README.md", "util/add.py"):
        rows.append(
            row(
                {"role": "user", "content": f"Read {path}"},
                {
                    "role": "assistant",
                    "content": fence({"tool": "read_file", "path": path}),
                },
            )
        )

    # --- run ---
    runs = [
        (["pwd"], "Show the current directory with pwd"),
        (["ls"], "List files with ls"),
        (["ls", "hello"], "List the hello folder"),
        (
            ["python3", "-m", "py_compile", "hello/main.py"],
            "Compile-check hello/main.py",
        ),
        (
            ["python3", "-m", "py_compile", "demo/app.py"],
            "Compile-check demo/app.py",
        ),
        (
            ["python3", "-m", "py_compile", "util/add.py"],
            "Compile-check util/add.py",
        ),
    ]
    for argv, user in runs:
        rows.append(
            row(
                {"role": "user", "content": user},
                {"role": "assistant", "content": fence({"tool": "run", "argv": argv})},
            )
        )

    # --- done ---
    for summary in (
        "Created hello/main.py",
        "Created demo app",
        "Wrote README",
        "Finished scaffold",
    ):
        rows.append(
            row(
                {"role": "user", "content": "Finish the task"},
                {
                    "role": "assistant",
                    "content": fence({"tool": "done", "summary": summary}),
                },
            )
        )

    # --- multi-turn toy: hello app ---
    rows.append(
        row(
            {
                "role": "user",
                "content": "Create hello/main.py that prints Hello",
            },
            {
                "role": "assistant",
                "content": fence({"tool": "mkdir", "path": "hello"}),
            },
            {
                "role": "user",
                "content": "TOOL_RESULT\nok: created hello/",
            },
            {
                "role": "assistant",
                "content": fence(
                    {
                        "tool": "write_file",
                        "path": "hello/main.py",
                        "content": "print('Hello')\n",
                    }
                ),
            },
            {
                "role": "user",
                "content": "TOOL_RESULT\nok: wrote hello/main.py (14 bytes)",
            },
            {
                "role": "assistant",
                "content": fence(
                    {
                        "tool": "run",
                        "argv": ["python3", "-m", "py_compile", "hello/main.py"],
                    }
                ),
            },
            {
                "role": "user",
                "content": "TOOL_RESULT\nok: exit 0\n(no output)",
            },
            {
                "role": "assistant",
                "content": fence(
                    {"tool": "done", "summary": "Created hello/main.py"}
                ),
            },
        )
    )

    # --- multi-turn: demo ---
    rows.append(
        row(
            {
                "role": "user",
                "content": "Create a folder demo and write demo/app.py that prints hi",
            },
            {
                "role": "assistant",
                "content": fence({"tool": "mkdir", "path": "demo"}),
            },
            {
                "role": "user",
                "content": "TOOL_RESULT\nok: created demo/",
            },
            {
                "role": "assistant",
                "content": fence(
                    {
                        "tool": "write_file",
                        "path": "demo/app.py",
                        "content": "print('hi')\n",
                    }
                ),
            },
            {
                "role": "user",
                "content": "TOOL_RESULT\nok: wrote demo/app.py (12 bytes)",
            },
            {
                "role": "assistant",
                "content": fence({"tool": "done", "summary": "Created demo/app.py"}),
            },
        )
    )

    # --- multi-turn after parse error recovery teaching ---
    rows.append(
        row(
            {"role": "user", "content": "Make notes/README.md with # Notes"},
            {
                "role": "assistant",
                "content": fence(
                    {
                        "tool": "write_file",
                        "path": "notes/README.md",
                        "content": "# Notes\n",
                    }
                ),
            },
            {
                "role": "user",
                "content": "TOOL_RESULT\nok: wrote notes/README.md (8 bytes)",
            },
            {
                "role": "assistant",
                "content": fence({"tool": "done", "summary": "Wrote notes/README.md"}),
            },
        )
    )

    # --- write creates parents (single write without mkdir) ---
    rows.append(
        row(
            {
                "role": "user",
                "content": "Create hello/main.py that prints Hello",
            },
            {
                "role": "assistant",
                "content": fence(
                    {
                        "tool": "write_file",
                        "path": "hello/main.py",
                        "content": "print('Hello')\n",
                    }
                ),
            },
        )
    )
    rows.append(
        row(
            {
                "role": "user",
                "content": "Create hello/main.py that prints Hello",
            },
            {
                "role": "assistant",
                "content": fence(
                    {
                        "tool": "write_file",
                        "path": "hello/main.py",
                        "content": "print('Hello')\n",
                    }
                ),
            },
            {
                "role": "user",
                "content": "TOOL_RESULT\nok: wrote hello/main.py (14 bytes)",
            },
            {
                "role": "assistant",
                "content": fence(
                    {"tool": "done", "summary": "Created hello/main.py"}
                ),
            },
        )
    )

    assert len(rows) >= 30, len(rows)
    OUT.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {OUT} ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
