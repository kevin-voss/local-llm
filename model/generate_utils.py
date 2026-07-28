"""Shared generation helpers for generate.py and eval."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import torch
from tokenizers import Tokenizer

from model.transformer import GPT, GPTConfig, gpt_config_from_dict, load_config

SPECIAL = {
    "system": "<|system|>",
    "user": "<|user|>",
    "assistant": "<|assistant|>",
    "end": "<|end|>",
}


def pick_device(prefer_mps: bool = True) -> torch.device:
    if prefer_mps and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def serialize_chat(messages: list[dict[str, str]], include_assistant_start: bool = False) -> str:
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
    if include_assistant_start:
        parts.append(f"{SPECIAL['assistant']}\n")
    return "".join(parts)


def strip_special(text: str) -> str:
    out = text
    if SPECIAL["end"] in out:
        out = out.split(SPECIAL["end"])[0]
    for tok in SPECIAL.values():
        out = out.replace(tok, "")
    return out.strip()


def load_checkpoint(
    checkpoint_path: Path | str,
    device: torch.device | None = None,
) -> tuple[GPT, Tokenizer, dict[str, Any], torch.device]:
    path = Path(checkpoint_path)
    if not path.is_file():
        raise FileNotFoundError(str(path))
    device = device or pick_device()
    ckpt = torch.load(path, map_location="cpu", weights_only=False)
    cfg = gpt_config_from_dict(ckpt["config"])
    model = GPT(cfg)
    model.load_state_dict(ckpt["model_state"])
    model.to(device)
    model.eval()
    tok_path = Path(ckpt.get("tokenizer_path", "checkpoints/tokenizer.json"))
    if not tok_path.is_file():
        # allow relative to repo root
        alt = Path(__file__).resolve().parents[1] / tok_path
        tok_path = alt if alt.is_file() else tok_path
    if not tok_path.is_file():
        raise FileNotFoundError(f"tokenizer missing: {tok_path}")
    tokenizer = Tokenizer.from_file(str(tok_path))
    return model, tokenizer, ckpt, device


def prompt_to_ids(tokenizer: Tokenizer, user_prompt: str, system: str | None = None) -> list[int]:
    messages: list[dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user_prompt})
    text = serialize_chat(messages, include_assistant_start=True)
    return tokenizer.encode(text).ids


def messages_to_ids(tokenizer: Tokenizer, messages: list[dict[str, str]]) -> list[int]:
    text = serialize_chat(messages, include_assistant_start=True)
    return tokenizer.encode(text).ids


@torch.no_grad()
def _generate_from_ids(
    model: GPT,
    tokenizer: Tokenizer,
    ids: list[int],
    *,
    max_new_tokens: int = 256,
    temperature: float = 0.2,
    top_k: int | None = 40,
    seed: int | None = 42,
    device: torch.device | None = None,
) -> dict[str, Any]:
    device = device or next(model.parameters()).device
    if seed is not None:
        torch.manual_seed(seed)
        if device.type == "mps":
            torch.mps.manual_seed(seed)
    # truncate from the left if needed, keep room for generation
    block = model.config.block_size
    if len(ids) >= block:
        ids = ids[-(block - 1) :]
    x = torch.tensor([ids], dtype=torch.long, device=device)
    eos_id = tokenizer.token_to_id(SPECIAL["end"])
    t0 = time.perf_counter()
    first_token_at: float | None = None
    out = x
    for _ in range(max_new_tokens):
        idx_cond = out[:, -block:]
        logits, _ = model(idx_cond)
        logits = logits[:, -1, :] / max(temperature, 1e-6)
        if top_k is not None:
            v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
            logits[logits < v[:, [-1]]] = float("-inf")
        probs = torch.softmax(logits, dim=-1)
        next_id = torch.multinomial(probs, num_samples=1)
        if first_token_at is None:
            first_token_at = time.perf_counter()
        out = torch.cat((out, next_id), dim=1)
        if eos_id is not None and int(next_id.item()) == eos_id:
            break
    t1 = time.perf_counter()
    new_ids = out[0, len(ids) :].tolist()
    raw = tokenizer.decode(new_ids)
    text = strip_special(raw)
    n_new = max(len(new_ids), 1)
    ttft = (first_token_at - t0) if first_token_at else (t1 - t0)
    elapsed = max(t1 - t0, 1e-9)
    return {
        "text": text,
        "raw": raw,
        "ttft_s": ttft,
        "tokens": n_new,
        "tok_per_s": n_new / elapsed,
        "elapsed_s": elapsed,
    }


@torch.no_grad()
def generate_text(
    model: GPT,
    tokenizer: Tokenizer,
    prompt: str,
    *,
    system: str | None = None,
    max_new_tokens: int = 256,
    temperature: float = 0.2,
    top_k: int | None = 40,
    seed: int | None = 42,
    device: torch.device | None = None,
) -> dict[str, Any]:
    ids = prompt_to_ids(tokenizer, prompt, system=system)
    return _generate_from_ids(
        model,
        tokenizer,
        ids,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        top_k=top_k,
        seed=seed,
        device=device,
    )


@torch.no_grad()
def generate_from_messages(
    model: GPT,
    tokenizer: Tokenizer,
    messages: list[dict[str, str]],
    *,
    max_new_tokens: int = 256,
    temperature: float = 0.2,
    top_k: int | None = 40,
    seed: int | None = 42,
    device: torch.device | None = None,
) -> dict[str, Any]:
    """Multi-turn generation for the agent loop (system/user/assistant history)."""
    ids = messages_to_ids(tokenizer, messages)
    return _generate_from_ids(
        model,
        tokenizer,
        ids,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        top_k=top_k,
        seed=seed,
        device=device,
    )


def fresh_untrained(
    config: GPTConfig | None = None,
    device: torch.device | None = None,
) -> GPT:
    """Random-init same architecture for AC-07 A/B (non-gating)."""
    device = device or pick_device()
    if config is None:
        config = gpt_config_from_dict(load_config())
    model = GPT(config)
    model.to(device)
    model.eval()
    return model
