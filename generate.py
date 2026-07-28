#!/usr/bin/env python3
"""CLI inference for checkpoints/local-coder.pt (Path A — no Ollama)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from model.generate_utils import generate_text, load_checkpoint, pick_device

ROOT = Path(__file__).resolve().parent
DEFAULT_CKPT = ROOT / "checkpoints" / "local-coder.pt"
DEFAULT_SYSTEM = (ROOT / "data" / "style" / "SYSTEM.md").read_text(encoding="utf-8").strip()


def run_once(
    checkpoint: Path,
    prompt: str,
    *,
    max_new_tokens: int,
    temperature: float,
    seed: int | None,
    system: str | None,
) -> int:
    if not checkpoint.is_file():
        print(
            f"missing checkpoint: {checkpoint}\nrun make train",
            file=sys.stderr,
        )
        return 2
    device = pick_device()
    if device.type == "cpu":
        print("warning: no MPS — generating on CPU", file=sys.stderr)
    print(f"Loading {checkpoint} on {device}...")
    try:
        model, tokenizer, _, device = load_checkpoint(checkpoint, device=device)
    except FileNotFoundError as e:
        print(f"missing artifact: {e}\nrun make tokenizer && make train", file=sys.stderr)
        return 2
    except RuntimeError as e:
        msg = str(e).lower()
        if "out of memory" in msg or "oom" in msg:
            print(
                "OOM during generate. See DEC-01/DEC-06 (16GB nano caps in model/config.yaml).",
                file=sys.stderr,
            )
            return 1
        raise
    result = generate_text(
        model,
        tokenizer,
        prompt,
        system=system,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        seed=seed,
        device=device,
    )
    print(result["text"])
    return 0


def repl(
    checkpoint: Path,
    *,
    max_new_tokens: int,
    temperature: float,
    seed: int | None,
    system: str | None,
) -> int:
    if not checkpoint.is_file():
        print(
            f"missing checkpoint: {checkpoint}\nrun make train",
            file=sys.stderr,
        )
        return 2
    device = pick_device()
    if device.type == "cpu":
        print("warning: no MPS — generating on CPU", file=sys.stderr)
    print(f"Loading {checkpoint} on {device}...")
    model, tokenizer, _, device = load_checkpoint(checkpoint, device=device)
    print("Ready. Empty line or Ctrl-D to exit.")
    while True:
        try:
            prompt = input(">>> ").strip()
        except EOFError:
            print()
            break
        if not prompt:
            break
        result = generate_text(
            model,
            tokenizer,
            prompt,
            system=system,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            seed=seed,
            device=device,
        )
        print(result["text"])
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
    parser.add_argument("--prompt", type=str, default=None, help="one-shot prompt")
    parser.add_argument("--max-new-tokens", type=int, default=256)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--no-system", action="store_true")
    args = parser.parse_args()
    system = None if args.no_system else DEFAULT_SYSTEM
    if args.prompt is not None:
        return run_once(
            args.checkpoint,
            args.prompt,
            max_new_tokens=args.max_new_tokens,
            temperature=args.temperature,
            seed=args.seed,
            system=system,
        )
    return repl(
        args.checkpoint,
        max_new_tokens=args.max_new_tokens,
        temperature=args.temperature,
        seed=args.seed,
        system=system,
    )


if __name__ == "__main__":
    raise SystemExit(main())
