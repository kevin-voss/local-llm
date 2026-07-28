# AGENTS.md — Local Coder LLM from scratch (M4 16GB)

**Path A:** custom decoder-only Transformer in **PyTorch (MPS)** → train from random init → **`generate.py`** (text) and **`agent.py`** (tools → `workspace/`) load `checkpoints/local-coder.pt`. **No Ollama**, no GGUF, no pretrained base LLM / LoRA, no MCP / LangChain.

## Hardware contract

- Target: Apple Silicon MacBook Pro **M4, 16GB unified memory**
- Nano model caps (`model/config.yaml`): roughly 10–40M params; `block_size` ≤ 512
- Close heavy apps during `make train`; no parallel train jobs

## Architecture (one path)

```text
HF (cached) + data/style/*.jsonl (+ tools.jsonl)
  → scripts/prepare_data.py → data/processed/
  → scripts/train_tokenizer.py → checkpoints/tokenizer.json
  → train.py (from scratch) → checkpoints/local-coder.pt
  → generate.py                          # text-only
  → agent.py                             # mkdir/write/read/run/done under workspace/
  → eval/run_eval.py + eval/run_agent_eval.py
```

No Crew Orbit app packages. No cloud LLM judge. No Ollama in the happy path.

## Makefile targets

| Target | Purpose |
|--------|---------|
| `make data` | Build processed corpus / JSONL |
| `make tokenizer` | Train BPE → `checkpoints/tokenizer.json` |
| `make train` | From-scratch train → `checkpoints/local-coder.pt` |
| `make eval` | Latency + structural + golden compile |
| `make eval-latency` | AC-01 (llm-m4) |
| `make eval-structural` | AC-03 / AC-04 (llm-m4) |
| `make eval-goldens` | AC-05 (llm-m4) |
| `make eval-agent` | Agent parser/sandbox units + toy tasks |

## Acceptance subjects

- Text: **`checkpoints/local-coder.pt`** via **`generate.py`**
- Tools: same checkpoint via **`agent.py`** writing under **`workspace/`**

## Quality honesty

From-scratch nano models **struggle** at complex React/Java and real apps. Style JSONL teaches code habits; `tools.jsonl` teaches the JSON tool protocol. v1 gates are pipeline + structural asserts + compiling goldens + agent sandbox/parser + **taught toy scaffolds** — not Copilot-level codegen or Spring/AWS generators.

Retrain after changing tool data: `make data tokenizer train`.

## Feature packages

- `features/local-coder-llm-m4/` — follow `/implement-feature local-coder-llm-m4`
- `features/local-coder-cli-agent/` — follow `/implement-feature local-coder-cli-agent`

## Safety

- No secrets in repo; no cloud API keys for train/generate after local caches exist
- Agent FS confined to `workspace/`; `run` allowlisted only; confirm `run` unless `--yes`
- Compile/lint only — do not run untrusted network services from model output
- Document dataset licenses in root `README.md`
