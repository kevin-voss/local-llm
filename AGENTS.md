# AGENTS.md — Local Coder LLM from scratch (M4 16GB)

**Path A:** custom decoder-only Transformer in **PyTorch (MPS)** → train from random init → **`generate.py`** loads `checkpoints/local-coder.pt`. **No Ollama**, no GGUF, no pretrained base LLM / LoRA.

## Hardware contract

- Target: Apple Silicon MacBook Pro **M4, 16GB unified memory**
- Nano model caps (`model/config.yaml`): roughly 10–40M params; `block_size` ≤ 512
- Close heavy apps during `make train`; no parallel train jobs

## Architecture (one path)

```text
HF (cached) + data/style/*.jsonl
  → scripts/prepare_data.py → data/processed/
  → scripts/train_tokenizer.py → checkpoints/tokenizer.json
  → train.py (from scratch) → checkpoints/local-coder.pt
  → generate.py
  → eval/run_eval.py (latency + structural; style goldens → tsc|eslint|javac)
```

No Crew Orbit app packages. No cloud LLM judge. No Ollama in the happy path.

## Makefile targets

| Target | Purpose |
|--------|---------|
| `make data` | Build processed corpus / JSONL |
| `make tokenizer` | Train BPE → `checkpoints/tokenizer.json` |
| `make train` | From-scratch train → `checkpoints/local-coder.pt` |
| `make eval` | Latency + structural + golden compile |
| `make eval-latency` | AC-01 |
| `make eval-structural` | AC-03 / AC-04 |
| `make eval-goldens` | AC-05 |

## Acceptance subject

**`checkpoints/local-coder.pt`** via **`generate.py`** only.

## Quality honesty

From-scratch nano models **struggle** at complex React/Java. Style JSONL is the teaching signal; v1 gates are pipeline + structural asserts + compiling **goldens**, not Copilot-level codegen.

## Feature package

`features/local-coder-llm-m4/` — follow `/implement-feature local-coder-llm-m4`.

## Safety

- No secrets in repo; no cloud API keys for train/generate after local caches exist
- Compile/lint only — do not run untrusted network services from model output
- Document dataset licenses in root `README.md`
