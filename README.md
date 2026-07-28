# Local Coder LLM from scratch (M4 16GB)

**Path A — 100% from scratch.** Build a small decoder-only Transformer in Python, train your own weights, run them with `generate.py`. **No Ollama.**

Target stack flavor in the data: **Java 17+**, **TypeScript**, **React**. Host: MacBook Pro **M4 / 16GB**.

## Honest expectations

Training a model from scratch that writes solid React/Java needs **massive** data and compute. On 16GB we ship a **nano** model (~10–40M params). It is for learning the full loop (data → tokenize → train → generate → eval). It will **not** match pretrained 7B coder models.

## Hardware

| Item | Value |
|------|-------|
| Chip | Apple Silicon M4 |
| Memory | **16GB unified** (hard budget) |
| Runtime | PyTorch **MPS** (CPU fallback with warning) |
| Infer | `generate.py` + `checkpoints/local-coder.pt` |

Close browsers/IDEs during `make train`.

## Prerequisites

- macOS on Apple Silicon
- Python **3.11+**
- PyTorch with MPS
- Node **20+** and JDK **17+** only for style-golden compile/lint in eval

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Quickstart

```bash
make data          # data/processed/
make tokenizer     # checkpoints/tokenizer.json
make train         # checkpoints/local-coder.pt
python generate.py --prompt "Write a React button with typed props"
make eval          # latency + structural + golden compile
```

Daily use:

```bash
python generate.py
```

## Pipeline

```text
style JSONL + filtered HF
  → prepare_data
  → train_tokenizer (BPE)
  → train.py (random init)
  → generate.py
```

## Data

- House style: `data/style/*.jsonl` + `data/style/SYSTEM.md`
- HF rows filtered/capped in `scripts/prepare_data.py`
- Train does **not** call cloud LLM APIs

## Train / generate

- Model code: `model/` (our Transformer)
- Config caps: `model/config.yaml`
- Checkpoint: `checkpoints/local-coder.pt`
- Infer entrypoint: `generate.py`

## Eval

| Gate | Command | What it proves |
|------|---------|----------------|
| Latency | `make eval-latency` | Warm TTFT &lt; 2s, ≥ 15 tok/s on MPS |
| Structural | `make eval-structural` | Fences + house-style cues from the model |
| Goldens | `make eval-goldens` | Committed style assistants compile/lint |
| Full | `make eval` | All of the above |

Manual A/B (trained vs untrained same arch): `eval/AB_CHECKLIST.md` (non-gating).

## Out of scope

Ollama, GGUF, Continue.dev, fine-tuning Qwen/Llama, cloud judges.

## Licenses / attribution

| Artifact | Notes |
|----------|-------|
| Our model code + checkpoints you train | This project |
| HF datasets | IDs/licenses via `scripts/prepare_data.py` / cards |
| Style JSONL | `data/style/` |

No third-party base LLM weights in this path.

## Layout

```text
AGENTS.md  README.md  Makefile  requirements.txt
train.py  generate.py
model/  data/  scripts/  checkpoints/  eval/
features/local-coder-llm-m4/
```

## Feature package

`features/local-coder-llm-m4/` — product/technical/acceptance/implement.
