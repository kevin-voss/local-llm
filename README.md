# Local Coder LLM from scratch (M4 16GB)

**Path A — 100% from scratch.** Build a small decoder-only Transformer in Python, train your own weights, then:

- **Text-only:** `generate.py` (no tools)
- **Small apps / scaffolds:** `agent.py` (fixed tools under `workspace/`)

**No Ollama.** No MCP, LangChain, or cloud agent stack.

Target stack flavor in the data: **Java 17+**, **TypeScript**, **React**, plus **tool-trace** rows for the CLI agent. Host: MacBook Pro **M4 / 16GB**.

## Honest expectations

Training a model from scratch that writes solid React/Java or builds real apps needs **massive** data and compute. On 16GB we ship a **nano** model (~10–40M params).

- `generate.py` is for learning the full loop (data → tokenize → train → generate → eval). It will **not** match pretrained 7B coder models.
- `agent.py` is for **small taught scaffolds** (e.g. one Python file + folder) after tool JSONL is mixed in and you retrain. It is **not** a Spring Boot / AWS / production app builder.

## Hardware

| Item | Value |
|------|-------|
| Chip | Apple Silicon M4 |
| Memory | **16GB unified** (hard budget) |
| Runtime | PyTorch **MPS** (CPU fallback with warning) |
| Infer (text) | `generate.py` + `checkpoints/local-coder.pt` |
| Infer (tools) | `agent.py` + same checkpoint → `workspace/` |

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
make data          # data/processed/ (includes data/style/tools.jsonl)
make tokenizer     # checkpoints/tokenizer.json
make train         # checkpoints/local-coder.pt  (retrain after tool data)
python generate.py --prompt "Write a React button with typed props"
python agent.py --task "Create hello/main.py that prints Hello" --yes
make eval          # latency + structural + golden compile
make eval-agent    # parser/sandbox units + toy agent task
```

Daily use:

```bash
# Text-only (unchanged Path A surface)
python generate.py

# Build a tiny scaffold with tools (sandbox: workspace/)
python agent.py
python agent.py --task "Create a Python hello app under hello/" --yes
```

**Retrain after tool data:** whenever you change `data/style/tools.jsonl` or `SYSTEM_TOOLS.md`, run `make data tokenizer train` so the checkpoint learns the JSON tool protocol.

## Pipeline

```text
style JSONL (+ tools.jsonl) + filtered HF
  → prepare_data
  → train_tokenizer (BPE)
  → train.py (random init)
  → generate.py          # text-only
  → agent.py             # tools → workspace/
```

## Data

- House style: `data/style/*.jsonl` + `data/style/SYSTEM.md`
- Tool traces: `data/style/tools.jsonl` + `data/style/SYSTEM_TOOLS.md`
- HF rows filtered/capped in `scripts/prepare_data.py`
- Train does **not** call cloud LLM APIs

## Train / generate / agent

- Model code: `model/` (our Transformer)
- Config caps: `model/config.yaml`
- Checkpoint: `checkpoints/local-coder.pt`
- Text entrypoint: `generate.py`
- Agent entrypoint: `agent.py` (tools: `mkdir`, `write_file`, `read_file`, `run`, `done`)
- Sandbox: all FS ops under `workspace/` (gitignored contents)

`run` is allowlisted only (`ls`, `pwd`, `python3 -m py_compile <file>`). Interactive use prompts before `run` unless you pass `--yes`.

## Eval

| Gate | Command | What it proves |
|------|---------|----------------|
| Latency | `make eval-latency` | Warm TTFT &lt; 2s, ≥ 15 tok/s on MPS |
| Structural | `make eval-structural` | Fences + house-style cues from the model |
| Goldens | `make eval-goldens` | Committed style assistants compile/lint |
| Agent | `make eval-agent` | Parser/sandbox/allowlist units + toy agent task |
| Full | `make eval` | Latency + structural + goldens |

Manual A/B (trained vs untrained same arch): `eval/AB_CHECKLIST.md` (non-gating).

## Out of scope

Ollama, GGUF, Continue.dev, fine-tuning Qwen/Llama, cloud judges, MCP, LangChain, unrestricted shell.

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
train.py  generate.py  agent.py
model/  agent/  data/  scripts/  checkpoints/  eval/  workspace/
features/local-coder-llm-m4/
features/local-coder-cli-agent/
```

## Feature packages

- `features/local-coder-llm-m4/` — Path A nano toolkit
- `features/local-coder-cli-agent/` — CLI agent with tools
