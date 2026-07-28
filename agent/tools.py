"""Fixed tool executors: mkdir, write_file, read_file, run, done."""

from __future__ import annotations

import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agent.allowlist import check_allowlist, normalize_argv
from agent.parse import ToolCall
from agent.sandbox import MAX_FILE_BYTES, SandboxError, ensure_root, resolve_in_sandbox

ConfirmFn = Callable[[list[str]], bool]

RUN_TIMEOUT_S = 15
RUN_OUTPUT_CAP = 4 * 1024


@dataclass
class ToolResult:
    observation: str
    done: bool = False
    summary: str = ""
    skipped: bool = False


def _truncate(s: str, n: int = RUN_OUTPUT_CAP) -> str:
    if len(s) <= n:
        return s
    return s[:n] + "\n...[truncated]"


def execute_tool(
    call: ToolCall,
    root: Path,
    *,
    confirm_run: ConfirmFn | None = None,
    auto_yes: bool = False,
) -> ToolResult:
    root = ensure_root(root)
    tool = call.tool

    if tool == "done":
        summary = call.args.get("summary") or ""
        return ToolResult(
            observation=f"ok: done ({summary})" if summary else "ok: done",
            done=True,
            summary=summary,
        )

    if tool == "mkdir":
        try:
            path = resolve_in_sandbox(root, call.args["path"])
        except SandboxError as e:
            return ToolResult(observation=str(e))
        path.mkdir(parents=True, exist_ok=True)
        rel = path.relative_to(root.resolve())
        return ToolResult(observation=f"ok: created {rel.as_posix()}/")

    if tool == "write_file":
        content = call.args["content"]
        content_bytes = content.encode("utf-8")
        if len(content_bytes) > MAX_FILE_BYTES:
            return ToolResult(
                observation=(
                    f"error: content exceeds {MAX_FILE_BYTES} bytes "
                    f"({len(content_bytes)} bytes)"
                )
            )
        try:
            path = resolve_in_sandbox(root, call.args["path"])
        except SandboxError as e:
            return ToolResult(observation=str(e))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        rel = path.relative_to(root.resolve())
        return ToolResult(
            observation=f"ok: wrote {rel.as_posix()} ({len(content_bytes)} bytes)"
        )

    if tool == "read_file":
        try:
            path = resolve_in_sandbox(root, call.args["path"])
        except SandboxError as e:
            return ToolResult(observation=str(e))
        if not path.is_file():
            rel = call.args["path"]
            return ToolResult(observation=f"error: file not found: {rel}")
        data = path.read_bytes()
        if len(data) > MAX_FILE_BYTES:
            return ToolResult(
                observation=(
                    f"error: file exceeds {MAX_FILE_BYTES} bytes ({len(data)} bytes)"
                )
            )
        text = data.decode("utf-8", errors="replace")
        rel = path.relative_to(root.resolve())
        return ToolResult(
            observation=f"ok: read {rel.as_posix()} ({len(data)} bytes)\n{text}"
        )

    if tool == "run":
        try:
            argv = normalize_argv(call.args)
        except ValueError as e:
            return ToolResult(observation=f"error: {e}")
        decision = check_allowlist(argv, root)
        if not decision.ok:
            return ToolResult(
                observation=decision.error or "error: command not allowlisted"
            )
        if not auto_yes:
            ok = True
            if confirm_run is not None:
                ok = confirm_run(decision.argv)
            if not ok:
                return ToolResult(
                    observation="error: run declined by operator",
                    skipped=True,
                )
        return _run_argv(decision.argv, root)

    return ToolResult(observation=f"error: unknown tool: {tool}")


def _run_argv(argv: list[str], root: Path) -> ToolResult:
    root = root.resolve()
    try:
        proc = subprocess.run(
            argv,
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=RUN_TIMEOUT_S,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return ToolResult(observation=f"error: run timed out after {RUN_TIMEOUT_S}s")
    except OSError as e:
        return ToolResult(observation=f"error: run failed: {e}")

    out = _truncate((proc.stdout or "") + (proc.stderr or ""))
    if proc.returncode == 0:
        body = out.strip() or "(no output)"
        return ToolResult(observation=f"ok: exit 0\n{body}")
    return ToolResult(
        observation=f"error: exit {proc.returncode}\n{out.strip() or '(no output)'}"
    )


def format_observation(result: ToolResult) -> str:
    return f"TOOL_RESULT\n{result.observation}"
