#!/usr/bin/env python3
"""Build data/processed/train.jsonl + corpus.txt from style JSONL (+ optional HF)."""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STYLE = ROOT / "data" / "style"
OUT = ROOT / "data" / "processed"

SPECIAL = {
    "system": "<|system|>",
    "user": "<|user|>",
    "assistant": "<|assistant|>",
    "end": "<|end|>",
}

# Chat serialization (single format — see technical.md)
# <|system|>\n...\n<|user|>\n...\n<|assistant|>\n...\n<|end|>\n


def serialize_messages(messages: list[dict[str, str]]) -> str:
    parts: list[str] = []
    for msg in messages:
        role = msg["role"]
        content = msg["content"]
        if role == "system":
            parts.append(f"{SPECIAL['system']}\n{content}\n")
        elif role == "user":
            parts.append(f"{SPECIAL['user']}\n{content}\n")
        elif role == "assistant":
            parts.append(f"{SPECIAL['assistant']}\n{content}\n{SPECIAL['end']}\n")
        else:
            raise ValueError(f"unknown role: {role}")
    return "".join(parts)


def load_style_jsonl() -> list[dict]:
    rows: list[dict] = []
    for path in sorted(STYLE.glob("*.jsonl")):
        with path.open(encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError as e:
                    raise SystemExit(f"{path}:{line_no}: invalid JSON: {e}") from e
                if "messages" not in obj:
                    raise SystemExit(f"{path}:{line_no}: missing messages")
                rows.append(obj)
    return rows


def try_load_hf(max_rows: int, seed: int) -> list[dict]:
    """Optional coding samples from HF; skip cleanly if offline/unavailable."""
    if max_rows <= 0:
        return []
    try:
        from datasets import load_dataset
    except ImportError:
        print("datasets not installed; skipping HF", file=sys.stderr)
        return []

    system = (STYLE / "SYSTEM.md").read_text(encoding="utf-8").strip()
    out: list[dict] = []
    # Small, code-oriented public sample; capped for 16GB nano train
    try:
        ds = load_dataset(
            "code_search_net",
            "python",
            split="train",
            trust_remote_code=True,
        )
    except Exception as e:  # noqa: BLE001 — offline / network / schema
        print(f"HF skip ({type(e).__name__}: {e})", file=sys.stderr)
        return []

    rng = random.Random(seed)
    indices = list(range(min(len(ds), max_rows * 20)))
    rng.shuffle(indices)
    for i in indices:
        if len(out) >= max_rows:
            break
        row = ds[i]
        code = row.get("func_code_string") or row.get("whole_func_string") or ""
        doc = row.get("func_documentation_string") or "Complete the function."
        if not code or len(code) < 40 or len(code) > 2000:
            continue
        out.append(
            {
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": f"Write code: {doc[:400]}"},
                    {
                        "role": "assistant",
                        "content": f"```python\n{code.strip()}\n```",
                    },
                ],
                "source": "hf:code_search_net",
            }
        )
    print(f"HF rows kept: {len(out)}")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hf-max", type=int, default=200, help="max HF rows (0=style only)")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    style = load_style_jsonl()
    print(f"style rows: {len(style)}")
    hf = try_load_hf(args.hf_max, args.seed)
    all_rows = style + hf
    rng = random.Random(args.seed)
    rng.shuffle(all_rows)

    train_path = args.out / "train.jsonl"
    corpus_path = args.out / "corpus.txt"
    with train_path.open("w", encoding="utf-8") as tf, corpus_path.open(
        "w", encoding="utf-8"
    ) as cf:
        for row in all_rows:
            text = serialize_messages(row["messages"])
            rec = {"text": text, "messages": row["messages"]}
            if "source" in row:
                rec["source"] = row["source"]
            tf.write(json.dumps(rec, ensure_ascii=False) + "\n")
            cf.write(text)
            if not text.endswith("\n"):
                cf.write("\n")

    meta = {
        "n_train": len(all_rows),
        "n_style": len(style),
        "n_hf": len(hf),
        "serialization": "<|system|>/<|user|>/<|assistant|>/<|end|>",
        "train_jsonl": str(train_path.relative_to(ROOT)),
        "corpus_txt": str(corpus_path.relative_to(ROOT)),
    }
    (args.out / "meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {train_path} ({len(all_rows)} rows)")
    print(f"wrote {corpus_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
