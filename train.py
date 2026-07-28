#!/usr/bin/env python3
"""Train nano GPT from random init → checkpoints/local-coder.pt (Path A)."""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import torch
from tokenizers import Tokenizer

from model.generate_utils import pick_device
from model.transformer import GPT, count_parameters, gpt_config_from_dict, load_config

ROOT = Path(__file__).resolve().parent


def load_token_ids(train_jsonl: Path, tokenizer: Tokenizer) -> list[int]:
    ids: list[int] = []
    with train_jsonl.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            text = json.loads(line)["text"]
            ids.extend(tokenizer.encode(text).ids)
    if len(ids) < 64:
        raise SystemExit(f"too few tokens in {train_jsonl}: {len(ids)}")
    return ids


def get_batch(
    data: torch.Tensor, batch_size: int, block_size: int, device: torch.device
) -> tuple[torch.Tensor, torch.Tensor]:
    ix = torch.randint(0, data.size(0) - block_size - 1, (batch_size,))
    x = torch.stack([data[i : i + block_size] for i in ix])
    y = torch.stack([data[i + 1 : i + 1 + block_size] for i in ix])
    return x.to(device), y.to(device)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "model" / "config.yaml")
    parser.add_argument(
        "--train-jsonl", type=Path, default=ROOT / "data" / "processed" / "train.jsonl"
    )
    parser.add_argument(
        "--tokenizer", type=Path, default=ROOT / "checkpoints" / "tokenizer.json"
    )
    parser.add_argument(
        "--out", type=Path, default=ROOT / "checkpoints" / "local-coder.pt"
    )
    parser.add_argument("--max-steps", type=int, default=None)
    parser.add_argument("--batch-size", type=int, default=None)
    parser.add_argument("--device", type=str, default=None)
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    raw = load_config(args.config)
    if args.max_steps is not None:
        raw["max_steps"] = args.max_steps
    if args.batch_size is not None:
        raw["batch_size"] = args.batch_size
    if args.seed is not None:
        raw["seed"] = args.seed

    if not args.tokenizer.is_file():
        raise SystemExit(f"missing tokenizer: {args.tokenizer} (run make tokenizer)")
    if not args.train_jsonl.is_file():
        raise SystemExit(f"missing train data: {args.train_jsonl} (run make data)")

    tokenizer = Tokenizer.from_file(str(args.tokenizer))
    raw["vocab_size"] = tokenizer.get_vocab_size()
    cfg = gpt_config_from_dict(raw)

    seed = int(raw.get("seed", 42))
    torch.manual_seed(seed)

    if args.device:
        device = torch.device(args.device)
    else:
        device = pick_device()
    if device.type == "cpu" and torch.backends.mps.is_available() is False:
        print("warning: no MPS — training on CPU (still Path A)", file=sys.stderr)
    elif device.type == "cpu":
        print("warning: forcing CPU", file=sys.stderr)
    else:
        print(f"device: {device}")

    # From-scratch: random init only — never load pretrained LLM weights
    model = GPT(cfg).to(device)
    n_params = count_parameters(model)
    print(f"params: {n_params:,} ({n_params / 1e6:.2f}M)")
    if not (10_000_000 <= n_params <= 40_000_000):
        print(
            f"warning: param count {n_params} outside 10–40M band; check config",
            file=sys.stderr,
        )

    print("tokenizing corpus…")
    token_ids = load_token_ids(args.train_jsonl, tokenizer)
    data = torch.tensor(token_ids, dtype=torch.long)
    print(f"tokens: {len(token_ids):,}")

    opt = torch.optim.AdamW(
        model.parameters(),
        lr=float(raw.get("learning_rate", 3e-4)),
        weight_decay=float(raw.get("weight_decay", 0.1)),
        betas=(0.9, 0.95),
    )

    batch_size = int(raw.get("batch_size", 8))
    grad_accum = int(raw.get("grad_accum", 4))
    max_steps = int(raw.get("max_steps", 2000))
    eval_interval = int(raw.get("eval_interval", 200))
    block_size = cfg.block_size

    model.train()
    t0 = time.time()
    last_loss = float("nan")
    try:
        for step in range(1, max_steps + 1):
            opt.zero_grad(set_to_none=True)
            loss_accum = 0.0
            for _ in range(grad_accum):
                xb, yb = get_batch(data, batch_size, block_size, device)
                _, loss = model(xb, yb)
                (loss / grad_accum).backward()
                loss_accum += float(loss.item())
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            last_loss = loss_accum / grad_accum
            if step % eval_interval == 0 or step == 1:
                elapsed = time.time() - t0
                tok_seen = step * batch_size * grad_accum * block_size
                tps = tok_seen / max(elapsed, 1e-9)
                print(
                    f"step {step}/{max_steps} loss={last_loss:.4f} "
                    f"tok/s~{tps:.0f} elapsed={elapsed:.1f}s"
                )
    except RuntimeError as e:
        msg = str(e).lower()
        if "out of memory" in msg or "oom" in msg or "memory" in msg:
            print(
                "OOM during train (EDGE-01). Host budget is 16GB unified (DEC-01). "
                "Lower batch_size / n_embd / block_size within nano caps in "
                "model/config.yaml. Do not switch to Ollama or pretrained LLMs.",
                file=sys.stderr,
            )
            return 1
        raise

    args.out.parent.mkdir(parents=True, exist_ok=True)
    ckpt = {
        "model_state": model.state_dict(),
        "config": {
            "vocab_size": cfg.vocab_size,
            "block_size": cfg.block_size,
            "n_layer": cfg.n_layer,
            "n_head": cfg.n_head,
            "n_embd": cfg.n_embd,
            "dropout": cfg.dropout,
            "bias": cfg.bias,
        },
        "tokenizer_path": str(args.tokenizer.relative_to(ROOT)),
        "train_meta": {
            "step": max_steps,
            "loss": last_loss if not math.isnan(last_loss) else None,
            "n_params": n_params,
            "seed": seed,
            "device": str(device),
        },
    }
    torch.save(ckpt, args.out)
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
