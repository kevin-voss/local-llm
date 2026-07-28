"""Agent loop with mocked generate (AC-07, EDGE-06)."""

from __future__ import annotations

from pathlib import Path

from agent.loop import run_agent_loop


def test_loop_reaches_done(tmp_path: Path):
    root = tmp_path / "ws"
    replies = [
        '```json\n{"tool":"mkdir","path":"hello"}\n```',
        '```json\n{"tool":"write_file","path":"hello/main.py","content":"print(\'Hello\')\\n"}\n```',
        '```json\n{"tool":"done","summary":"Created hello/main.py"}\n```',
    ]
    i = {"n": 0}

    def generate(_messages):
        text = replies[i["n"]]
        i["n"] += 1
        return text

    result = run_agent_loop(
        "Create hello/main.py that prints Hello",
        system="sys",
        generate=generate,
        root=root,
        max_turns=8,
        auto_yes=True,
    )
    assert result.done
    assert result.exit_code == 0
    assert (root / "hello" / "main.py").is_file()
    assert "Hello" in (root / "hello" / "main.py").read_text(encoding="utf-8")


def test_turn_limit(tmp_path: Path):
    def generate(_messages):
        return '```json\n{"tool":"mkdir","path":"x"}\n```'

    result = run_agent_loop(
        "loop forever",
        system="sys",
        generate=generate,
        root=tmp_path / "ws",
        max_turns=3,
        auto_yes=True,
    )
    assert not result.done
    assert result.exit_code == 1
    assert "max_turns" in result.stop_reason


def test_parse_failures_abort(tmp_path: Path):
    def generate(_messages):
        return "no json here"

    result = run_agent_loop(
        "task",
        system="sys",
        generate=generate,
        root=tmp_path / "ws",
        max_turns=8,
        auto_yes=True,
    )
    assert result.exit_code == 1
    assert "parse failures" in result.stop_reason


def test_confirm_declines_run(tmp_path: Path):
    replies = [
        '```json\n{"tool":"run","argv":["pwd"]}\n```',
        '```json\n{"tool":"done","summary":"skipped run"}\n```',
    ]
    i = {"n": 0}

    def generate(_messages):
        text = replies[i["n"]]
        i["n"] += 1
        return text

    result = run_agent_loop(
        "pwd",
        system="sys",
        generate=generate,
        root=tmp_path / "ws",
        max_turns=8,
        auto_yes=False,
        confirm_run=lambda _a: False,
    )
    assert result.done
    # second message after first assistant is TOOL_RESULT declined
    users = [m for m in result.history if m["role"] == "user"]
    assert any("declined" in m["content"] for m in users)
