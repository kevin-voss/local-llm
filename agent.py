#!/usr/bin/env python3
"""CLI agent: Path A model + fixed tools under workspace/ (no Ollama/MCP)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from agent.loop import run_agent_loop
from agent.sandbox import ensure_root
from model.generate_utils import generate_from_messages, load_checkpoint, pick_device

ROOT = Path(__file__).resolve().parent
DEFAULT_CKPT = ROOT / "checkpoints" / "local-coder.pt"
DEFAULT_WORKSPACE = ROOT / "workspace"
DEFAULT_SYSTEM = (ROOT / "data" / "style" / "SYSTEM_TOOLS.md").read_text(
    encoding="utf-8"
).strip()


def _confirm_run(argv: list[str]) -> bool:
    print(f"Run allowlisted command: {argv!r} ? [y/N] ", end="", flush=True)
    try:
        line = input().strip().lower()
    except EOFError:
        print()
        return False
    return line in {"y", "yes"}


def _print_tool(turn: int, tool: str, args: dict, result) -> None:
    if tool == "mkdir":
        detail = args.get("path", "")
        print(f"→ [{turn}] mkdir {detail}")
    elif tool == "write_file":
        print(f"→ [{turn}] write_file {args.get('path', '')}")
    elif tool == "read_file":
        print(f"→ [{turn}] read_file {args.get('path', '')}")
    elif tool == "run":
        argv = args.get("argv") or args.get("cmd")
        status = "skipped" if result.skipped else ("ok" if result.observation.startswith("ok:") else "err")
        print(f"→ [{turn}] run {argv}  ({status})")
    elif tool == "done":
        print(f"→ [{turn}] done {args.get('summary', '')}")
    else:
        print(f"→ [{turn}] {tool}")


def _load_model(checkpoint: Path):
    if not checkpoint.is_file():
        print(
            f"missing checkpoint: {checkpoint}\nrun make train",
            file=sys.stderr,
        )
        raise SystemExit(2)
    device = pick_device()
    if device.type == "cpu":
        print("warning: no MPS — generating on CPU", file=sys.stderr)
    print(f"Loading {checkpoint} on {device}...")
    try:
        model, tokenizer, _, device = load_checkpoint(checkpoint, device=device)
    except FileNotFoundError as e:
        print(
            f"missing artifact: {e}\nrun make tokenizer && make train",
            file=sys.stderr,
        )
        raise SystemExit(2) from e
    except RuntimeError as e:
        msg = str(e).lower()
        if "out of memory" in msg or "oom" in msg:
            print(
                "OOM during agent load. See nano caps in model/config.yaml.",
                file=sys.stderr,
            )
            raise SystemExit(1) from e
        raise
    return model, tokenizer, device


def run_task(
    task: str,
    *,
    checkpoint: Path,
    workspace: Path,
    max_turns: int,
    max_new_tokens: int,
    temperature: float,
    seed: int | None,
    yes: bool,
    system: str,
) -> int:
    model, tokenizer, device = _load_model(checkpoint)
    root = ensure_root(workspace)

    def generate(messages: list[dict[str, str]]) -> str:
        result = generate_from_messages(
            model,
            tokenizer,
            messages,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            seed=seed,
            device=device,
        )
        return result["text"]

    loop = run_agent_loop(
        task,
        system=system,
        generate=generate,
        root=root,
        max_turns=max_turns,
        auto_yes=yes,
        confirm_run=None if yes else _confirm_run,
        on_tool=_print_tool,
        on_parse_error=lambda turn, err: print(f"→ [{turn}] parse error: {err}", file=sys.stderr),
    )
    if loop.done:
        print(f"done: {loop.summary}" if loop.summary else "done")
        return 0
    print(loop.stop_reason, file=sys.stderr)
    return loop.exit_code


def repl(
    *,
    checkpoint: Path,
    workspace: Path,
    max_turns: int,
    max_new_tokens: int,
    temperature: float,
    seed: int | None,
    yes: bool,
    system: str,
) -> int:
    model, tokenizer, device = _load_model(checkpoint)
    root = ensure_root(workspace)
    print("Ready. Empty line or Ctrl-D to exit.")

    def generate(messages: list[dict[str, str]]) -> str:
        result = generate_from_messages(
            model,
            tokenizer,
            messages,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            seed=seed,
            device=device,
        )
        return result["text"]

    while True:
        try:
            task = input(">>> ").strip()
        except EOFError:
            print()
            break
        if not task:
            break
        loop = run_agent_loop(
            task,
            system=system,
            generate=generate,
            root=root,
            max_turns=max_turns,
            auto_yes=yes,
            confirm_run=None if yes else _confirm_run,
            on_tool=_print_tool,
            on_parse_error=lambda turn, err: print(
                f"→ [{turn}] parse error: {err}", file=sys.stderr
            ),
        )
        if loop.done:
            print(f"done: {loop.summary}" if loop.summary else "done")
        else:
            print(loop.stop_reason, file=sys.stderr)
        print()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=DEFAULT_CKPT,
        help="path to local-coder.pt",
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=DEFAULT_WORKSPACE,
        help="sandbox root (default: ./workspace)",
    )
    parser.add_argument("--task", type=str, default=None, help="one-shot task")
    parser.add_argument("--max-turns", type=int, default=8)
    parser.add_argument("--max-new-tokens", type=int, default=256)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--yes",
        action="store_true",
        help="auto-approve allowlisted run commands",
    )
    parser.add_argument(
        "--system-file",
        type=Path,
        default=ROOT / "data" / "style" / "SYSTEM_TOOLS.md",
    )
    args = parser.parse_args()
    if not args.system_file.is_file():
        print(f"missing system prompt: {args.system_file}", file=sys.stderr)
        return 2
    system = args.system_file.read_text(encoding="utf-8").strip()
    kwargs = dict(
        checkpoint=args.checkpoint,
        workspace=args.workspace,
        max_turns=args.max_turns,
        max_new_tokens=args.max_new_tokens,
        temperature=args.temperature,
        seed=args.seed,
        yes=args.yes,
        system=system,
    )
    if args.task is not None:
        return run_task(args.task, **kwargs)
    return repl(**kwargs)


if __name__ == "__main__":
    raise SystemExit(main())
