#!/usr/bin/env python3
"""Extract fenced code blocks from text or style JSONL assistants."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

FENCE_RE = re.compile(
    r"```(?P<lang>[a-zA-Z0-9_+-]*)\s*\n(?P<code>.*?)```",
    re.DOTALL,
)


def extract_fences(text: str) -> list[tuple[str, str]]:
    return [(m.group("lang").lower(), m.group("code")) for m in FENCE_RE.finditer(text)]


def first_fence(text: str, langs: set[str] | None = None) -> tuple[str, str] | None:
    blocks = extract_fences(text)
    if not blocks:
        return None
    if langs is None:
        return blocks[0]
    for lang, code in blocks:
        if lang in langs:
            return lang, code
    return None


def require_fence(text: str, langs: set[str] | None = None) -> tuple[str, str]:
    hit = first_fence(text, langs)
    if hit is None:
        wanted = ",".join(sorted(langs)) if langs else "any"
        raise ValueError(f"no recoverable fenced block (wanted langs: {wanted})")
    return hit


def iter_style_assistants(style_dir: Path):
    for path in sorted(style_dir.glob("*.jsonl")):
        with path.open(encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                for msg in obj["messages"]:
                    if msg["role"] == "assistant":
                        yield path, i, msg["content"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--style-dir", type=Path, default=Path("data/style"))
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()
    if args.list:
        n = 0
        for path, i, content in iter_style_assistants(args.style_dir):
            try:
                lang, _ = require_fence(content)
            except ValueError as e:
                print(f"FAIL {path}:{i}: {e}", file=sys.stderr)
                return 1
            n += 1
            print(f"{path.name}:{i} lang={lang}")
        print(f"ok {n} assistants with fences")
        return 0
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
