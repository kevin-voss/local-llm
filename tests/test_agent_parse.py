"""JSON tool protocol parser (AC-04, EDGE-03)."""

from __future__ import annotations

import pytest

from agent.parse import ParseError, parse_tool_call


def test_fenced_write_file():
    text = '''Sure.
```json
{"tool":"write_file","path":"hello/main.py","content":"print('Hello')\\n"}
```
'''
    call = parse_tool_call(text)
    assert call.tool == "write_file"
    assert call.args["path"] == "hello/main.py"
    assert "Hello" in call.args["content"]


def test_done():
    call = parse_tool_call('```json\n{"tool":"done","summary":"ok"}\n```')
    assert call.tool == "done"
    assert call.args["summary"] == "ok"


def test_run_argv():
    call = parse_tool_call(
        '```json\n{"tool":"run","argv":["python3","-m","py_compile","a.py"]}\n```'
    )
    assert call.tool == "run"
    assert call.args["argv"][0] == "python3"


def test_missing_json_fails():
    with pytest.raises(ParseError, match="no valid JSON"):
        parse_tool_call("I'll just mkdir hello without JSON")


def test_array_rejected():
    with pytest.raises(ParseError, match="parallel"):
        parse_tool_call('```json\n[{"tool":"mkdir","path":"a"}]\n```')


def test_unknown_tool():
    with pytest.raises(ParseError, match="unknown"):
        parse_tool_call('```json\n{"tool":"bash","cmd":"rm -rf /"}\n```')
