"""Tool executors (EDGE-05, EDGE-07) + confirm callback."""

from __future__ import annotations

from pathlib import Path

from agent.parse import ToolCall
from agent.tools import execute_tool


def test_write_mkdir_read(tmp_path: Path):
    root = tmp_path / "ws"
    r1 = execute_tool(ToolCall("mkdir", {"path": "hello"}, {}), root)
    assert r1.observation.startswith("ok:")
    r2 = execute_tool(
        ToolCall(
            "write_file",
            {"path": "hello/main.py", "content": "print('Hello')\n"},
            {},
        ),
        root,
    )
    assert "wrote" in r2.observation
    assert (root / "hello" / "main.py").read_text(encoding="utf-8") == "print('Hello')\n"
    r3 = execute_tool(ToolCall("read_file", {"path": "hello/main.py"}, {}), root)
    assert "Hello" in r3.observation


def test_escape_write(tmp_path: Path):
    root = tmp_path / "ws"
    r = execute_tool(
        ToolCall("write_file", {"path": "../escape.txt", "content": "x"}, {}),
        root,
    )
    assert "escapes workspace" in r.observation
    assert not (tmp_path / "escape.txt").exists()


def test_oversized_write(tmp_path: Path):
    root = tmp_path / "ws"
    big = "x" * (64 * 1024 + 1)
    r = execute_tool(
        ToolCall("write_file", {"path": "big.txt", "content": big}, {}),
        root,
    )
    assert "exceeds" in r.observation


def test_run_allowlist_and_confirm(tmp_path: Path):
    root = tmp_path / "ws"
    root.mkdir(parents=True, exist_ok=True)
    (root / "a.py").write_text("print(1)\n", encoding="utf-8")
    denied = execute_tool(
        ToolCall("run", {"argv": ["rm", "-rf", "."]}, {}),
        root,
        auto_yes=True,
    )
    assert "not allowlisted" in denied.observation

    declined = execute_tool(
        ToolCall("run", {"argv": ["pwd"]}, {}),
        root,
        auto_yes=False,
        confirm_run=lambda _a: False,
    )
    assert declined.skipped
    assert "declined" in declined.observation

    ok = execute_tool(
        ToolCall("run", {"argv": ["pwd"]}, {}),
        root,
        auto_yes=True,
    )
    assert ok.observation.startswith("ok:")


def test_done():
    r = execute_tool(ToolCall("done", {"summary": "Created hello"}, {}), Path("."))
    assert r.done
    assert r.summary == "Created hello"
