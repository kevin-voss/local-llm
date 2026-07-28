"""Unit tests for nano GPT (AC-02 / DEC-06)."""

from __future__ import annotations

import torch

from model.transformer import GPT, GPTConfig, count_parameters, load_config, gpt_config_from_dict


def test_config_caps_enforced():
    try:
        GPTConfig(n_layer=9).validate_caps()
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_forward_and_param_band():
    raw = load_config()
    cfg = gpt_config_from_dict(
        {
            **raw,
            "vocab_size": 8000,
            "block_size": 64,
            "n_layer": 6,
            "n_head": 6,
            "n_embd": 384,
        }
    )
    model = GPT(cfg)
    n = count_parameters(model)
    assert 10_000_000 <= n <= 40_000_000, n
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    model.to(device)
    x = torch.randint(0, cfg.vocab_size, (2, 16), device=device)
    y = torch.randint(0, cfg.vocab_size, (2, 16), device=device)
    logits, loss = model(x, y)
    assert logits.shape == (2, 16, cfg.vocab_size)
    assert loss is not None
    assert torch.isfinite(loss)
