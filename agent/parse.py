"""Extract and validate one JSON tool call from model output."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

TOOLS = frozenset({"mkdir", "write_file", "read_file", "run", "done"})

_FENCE_RE = re.compile(
    r"```(?:json)?\s*\n(.*?)\n```",
    re.DOTALL | re.IGNORECASE,
)


@dataclass(frozen=True)
class ToolCall:
    tool: str
    args: dict[str, Any]
    raw: dict[str, Any]


class ParseError(ValueError):
    pass


def _validate(obj: dict[str, Any]) -> ToolCall:
    if not isinstance(obj, dict):
        raise ParseError("error: tool call must be a JSON object")
    tool = obj.get("tool")
    if tool not in TOOLS:
        raise ParseError(f"error: unknown or missing tool: {tool!r}")
    if tool == "mkdir":
        if "path" not in obj or not isinstance(obj["path"], str):
            raise ParseError("error: mkdir requires string path")
        return ToolCall(tool, {"path": obj["path"]}, obj)
    if tool == "write_file":
        if "path" not in obj or not isinstance(obj["path"], str):
            raise ParseError("error: write_file requires string path")
        if "content" not in obj or not isinstance(obj["content"], str):
            raise ParseError("error: write_file requires string content")
        return ToolCall(
            tool, {"path": obj["path"], "content": obj["content"]}, obj
        )
    if tool == "read_file":
        if "path" not in obj or not isinstance(obj["path"], str):
            raise ParseError("error: read_file requires string path")
        return ToolCall(tool, {"path": obj["path"]}, obj)
    if tool == "run":
        if "argv" not in obj and "cmd" not in obj:
            raise ParseError("error: run requires argv or cmd")
        args: dict[str, Any] = {}
        if "argv" in obj:
            args["argv"] = obj["argv"]
        if "cmd" in obj:
            args["cmd"] = obj["cmd"]
        return ToolCall(tool, args, obj)
    # done
    summary = obj.get("summary", "")
    if summary is not None and not isinstance(summary, str):
        raise ParseError("error: done summary must be a string")
    return ToolCall(tool, {"summary": summary or ""}, obj)


def parse_tool_call(text: str) -> ToolCall:
    """Parse exactly one tool call; fail closed if none/invalid."""
    if not text or not text.strip():
        raise ParseError("error: no valid JSON tool call in model output")

    candidates: list[str] = []
    for m in _FENCE_RE.finditer(text):
        candidates.append(m.group(1).strip())

    # Bare JSON object fallback (entire strip or first {...})
    stripped = text.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        candidates.append(stripped)
    else:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start != -1 and end > start:
            candidates.append(stripped[start : end + 1])

    last_err: Exception | None = None
    for blob in candidates:
        try:
            obj = json.loads(blob)
        except json.JSONDecodeError as e:
            last_err = e
            continue
        if isinstance(obj, list):
            raise ParseError(
                "error: parallel tool arrays not supported; emit one JSON object"
            )
        try:
            return _validate(obj)
        except ParseError as e:
            last_err = e
            continue

    if last_err is not None:
        raise ParseError(f"error: invalid JSON tool call: {last_err}")
    raise ParseError("error: no valid JSON tool call in model output")
