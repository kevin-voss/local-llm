"""Agent turn loop: generate → parse → execute until done / max_turns."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agent.parse import ParseError, parse_tool_call
from agent.tools import ToolResult, execute_tool, format_observation

GenerateFn = Callable[[list[dict[str, str]]], str]
ConfirmFn = Callable[[list[str]], bool]


@dataclass
class LoopResult:
    exit_code: int
    summary: str = ""
    turns: int = 0
    done: bool = False
    history: list[dict[str, str]] = field(default_factory=list)
    stop_reason: str = ""


def run_agent_loop(
    task: str,
    *,
    system: str,
    generate: GenerateFn,
    root: Path,
    max_turns: int = 8,
    auto_yes: bool = False,
    confirm_run: ConfirmFn | None = None,
    on_tool: Callable[[int, str, dict[str, Any], ToolResult], None] | None = None,
    on_parse_error: Callable[[int, str], None] | None = None,
    max_consecutive_parse_failures: int = 3,
) -> LoopResult:
    """Drive one task. `generate` returns assistant text for the current messages."""
    messages: list[dict[str, str]] = [
        {"role": "system", "content": system},
        {"role": "user", "content": task},
    ]
    consecutive_parse_failures = 0

    for turn in range(1, max_turns + 1):
        text = generate(messages)
        messages.append({"role": "assistant", "content": text})

        try:
            call = parse_tool_call(text)
            consecutive_parse_failures = 0
        except ParseError as e:
            consecutive_parse_failures += 1
            obs = f"TOOL_RESULT\n{e}"
            if on_parse_error:
                on_parse_error(turn, str(e))
            messages.append({"role": "user", "content": obs})
            if consecutive_parse_failures >= max_consecutive_parse_failures:
                return LoopResult(
                    exit_code=1,
                    turns=turn,
                    history=messages,
                    stop_reason=(
                        f"aborted after {max_consecutive_parse_failures} "
                        "consecutive parse failures"
                    ),
                )
            continue

        result = execute_tool(
            call,
            root,
            confirm_run=confirm_run,
            auto_yes=auto_yes,
        )
        if on_tool:
            on_tool(turn, call.tool, call.args, result)

        if result.done:
            return LoopResult(
                exit_code=0,
                summary=result.summary,
                turns=turn,
                done=True,
                history=messages,
                stop_reason="done",
            )

        messages.append({"role": "user", "content": format_observation(result)})

    return LoopResult(
        exit_code=1,
        turns=max_turns,
        history=messages,
        stop_reason=f"stopped at max_turns={max_turns} without done",
    )
