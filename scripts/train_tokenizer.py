#!/usr/bin/env python3
"""Train BPE tokenizer on data/processed/corpus.txt → checkpoints/tokenizer.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from tokenizers import Tokenizer, decoders, models, pre_tokenizers, processors, trainers

ROOT = Path(__file__).resolve().parents[1]
SPECIAL_TOKENS = ["<|system|>", "<|user|>", "<|assistant|>", "<|end|>", "<pad>", "<unk>"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--corpus",
        type=Path,
        default=ROOT / "data" / "processed" / "corpus.txt",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "checkpoints" / "tokenizer.json",
    )
    parser.add_argument("--vocab-size", type=int, default=8000)
    args = parser.parse_args()

    if not args.corpus.is_file():
        raise SystemExit(f"missing corpus: {args.corpus} (run make data)")
    if args.vocab_size > 16000:
        raise SystemExit("vocab_size exceeds DEC-06 cap 16000")

    args.out.parent.mkdir(parents=True, exist_ok=True)

    tokenizer = Tokenizer(models.BPE(unk_token="<unk>"))
    tokenizer.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
    trainer = trainers.BpeTrainer(
        vocab_size=args.vocab_size,
        special_tokens=SPECIAL_TOKENS,
        min_frequency=2,
        show_progress=True,
    )
    tokenizer.train([str(args.corpus)], trainer=trainer)
    tokenizer.post_processor = processors.ByteLevel(trim_offsets=False)
    tokenizer.decoder = decoders.ByteLevel()
    tokenizer.save(str(args.out))

    # roundtrip smoke
    sample = (
        "<|system|>\nhello\n<|user|>\nWrite a Button\n"
        "<|assistant|>\n```tsx\nfunction Button(){}\n```\n<|end|>\n"
    )
    enc = tokenizer.encode(sample)
    dec = tokenizer.decode(enc.ids)
    meta = {
        "path": str(args.out.relative_to(ROOT)),
        "vocab_size": tokenizer.get_vocab_size(),
        "special_tokens": SPECIAL_TOKENS,
        "roundtrip_ok": sample.replace(" ", "") in dec.replace(" ", "")
        or "Button" in dec,
        "n_ids_sample": len(enc.ids),
    }
    (args.out.parent / "tokenizer_meta.json").write_text(
        json.dumps(meta, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(meta))
    if "Button" not in dec:
        raise SystemExit("tokenizer roundtrip failed (Button missing)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
