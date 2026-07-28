# Product — Local Coder LLM from scratch (M4 16GB)

## Problem

There is no small, offline, **from-scratch** coding-LLM loop on this M4 16GB Mac: define a tiny Transformer, train weights from random init on Java/TS/React-flavored text, and generate with a local `.pth` — without depending on Ollama or a pretrained 7B base.

## Actors

| Actor | Role |
|-------|------|
| Solo developer (operator) | Builds data, trains, runs `generate.py`, runs eval |

No multi-tenant users. No IDE plugin requirement in v1.

## Goals

1. Own the neural net: model code + tokenizer + train + `generate.py` in this repo.
2. Entire generate path offline after data/checkpoint exist locally.
3. Measurable warm latency on this 16GB host (nano model should clear speed gates).
4. Training data and prompts target house style (modern React/TS, Java 17+).
5. Eval proves the **pipeline** and **structural** generation habits; does not pretend nano weights match commercial coder models.
6. Makefile-driven; one architecture; no Ollama.

## Non-goals

- Ollama, GGUF, llama.cpp serve, Continue.dev integration
- Fine-tuning or loading Qwen/Llama/any pretrained LLM weights
- MLX-only stack (PyTorch MPS is the chosen train/infer runtime)
- Production-grade React/Java assistant quality
- Cloud inference or cloud LLM-as-judge
- Crew Orbit app packages
- RAG / agents / multi-model routing

## Scope

### In

- Custom decoder-only Transformer (Python/PyTorch)
- BPE tokenizer trained on our corpus
- `train.py` → `checkpoints/local-coder.pt`
- `generate.py` interactive + one-shot CLI
- Data prep (HF filter + committed style JSONL)
- Eval harness (latency + structural asserts + compile checks on style goldens)

### Out

See Non-goals. Explicitly **Path A only** — not “LoRA a base model later” as a live path.

## Decisions

### DEC-01 — Host memory budget is 16GB unified

**Decision:** Train/infer defaults assume **16GB** M4 unified memory.

**Rejected:** 36GB+ hyperparams; dual RAM profiles.

### DEC-02 — Path A: from scratch, no Ollama

**Decision:** Build and run **our** model only. Inference is Python loading `.pt`/`.pth`. **No Ollama** in product, Makefile, or eval.

**Rationale:** User-selected Path A; greenfield one architecture.

**Rejected:** Ollama serve; GGUF export; pretrained base + LoRA as v1.

### DEC-03 — PyTorch + MPS

**Decision:** Implement and train with **PyTorch**, device **`mps`** when available else `cpu`.

**Rationale:** Matches from-scratch `.pth` workflow; MPS is the Apple Silicon accelerator for this path.

**Rejected:** mlx-lm LoRA on external weights; JAX; training-only-on-CPU requirement.

### DEC-04 — Checkpoint artifact

**Decision:** Single canonical checkpoint path: **`checkpoints/local-coder.pt`** (torch.save dict: model state, config, tokenizer ref/meta). `.pth` alias allowed as copy/symlink name if needed; docs standardize on `.pt`.

**Rejected:** Ollama tags; multiple competing checkpoint formats.

### DEC-05 — Inference is `generate.py` only

**Decision:** Operator runs `python generate.py` (REPL and `--prompt` one-shot). Eval shells out to the same entrypoint or imports its generate function.

**Rejected:** HTTP server, Ollama API, Continue.dev as v1 surfaces.

### DEC-06 — Nano model size

**Decision:** Fixed small config in `model/config.yaml` (order-of-magnitude **10–40M parameters**): e.g. `n_layer` ≤ 8, `n_embd` ≤ 512, `n_head` ≤ 8, `block_size` ≤ 512, vocab ≤ 16k. Exact integers locked in config at implement time within these caps.

**Rationale:** From-scratch on 16GB; larger configs need massive data/compute the host does not have.

**Rejected:** 7B+ from scratch; “grow later” dual configs in Makefile.

### DEC-07 — Tokenizer trained on our data

**Decision:** Train a **BPE** tokenizer with Hugging Face `tokenizers` on the prepared corpus; persist under `checkpoints/tokenizer.json` (or alongside checkpoint). Generation and train share one tokenizer.

**Rejected:** Tiktoken/GPT-2 vocab as sole path; char-level-only as the product tokenizer.

### DEC-08 — Full training from random init

**Decision:** `train.py` initializes weights randomly and optimizes next-token (and/or packed chat) loss on `data/processed/`. No weight download of external LLMs.

**Rejected:** Start from Qwen/Llama; LoRA adapters on frozen big models.

### DEC-09 — Data = filtered HF + committed style JSONL

**Decision:** Same data product idea: HF coding rows filtered/capped + `data/style/*.jsonl`. Format for train: tokenized text derived from chat messages (system/user/assistant serialization documented in technical.md).

**Rejected:** HF-only; runtime cloud synthetic generation.

### DEC-10 — Eval harness (honest gates)

**Decision:**
- **Model gate:** Python eval calls generation; **structural** asserts (fences, language tags, ban `any` / `React.FC` when TS-like, require style cues per case).
- **Data gate:** Committed style assistant goldens must pass `tsc`/`eslint`/`javac` (proves targets are real).
- **No** cloud judge. Promptfoo optional only if wired to a **local script provider** calling `generate.py`; default is pure Python/`make eval` to avoid Node+Ollama assumptions.

**Rejected:** Requiring nano model to pass full `tsc` on every generation as v1 ship gate; Ollama-based Promptfoo.

### DEC-11 — No IDE integration in v1

**Decision:** CLI only (`generate.py`). Continue.dev / VS Code plugins are out of scope.

**Rejected:** Continue→Ollama; custom IDE extension.

### DEC-12 — A/B vs untrained same architecture

**Decision:** Manual checklist compares trained checkpoint vs freshly initialized same config (same prompt). Non-gating.

**Rejected:** A/B vs Qwen/Ollama base.

### DEC-13 — Standalone toolkit layout

**Decision:** `model/`, `data/`, `scripts/`, `eval/`, `checkpoints/` (gitignored weights), `train.py`, `generate.py`, Makefile, `AGENTS.md`, `README.md`. No Crew Orbit apps. No `modelfiles/` Ollama assets.

**Rejected:** Crew Orbit multi-package scaffold.

### DEC-14 — Latency protocol

**Decision:** Warm `generate.py` (one discard), fixed prompt, **median of 5** TTFT and tok/s. Thresholds sized for nano MPS (see AC-01).

**Rejected:** Cold-start gate; measuring Ollama.

## Business rules

1. After checkpoint + tokenizer exist, `generate.py` and `make eval` work offline.
2. Acceptance subject is **`checkpoints/local-coder.pt`** via `generate.py` — nothing else.
3. Do not add Ollama as a “convenience” wrapper.
4. Document clearly in README: from-scratch nano models **struggle** at complex React/Java; style JSONL is the teaching signal, not a quality guarantee.
5. Close heavy apps during train; no parallel train jobs.

## Journeys

### Happy path

1. Install Python 3.11+, PyTorch (MPS), JDK/Node only for data/eval toolchains as needed.
2. `make data` → corpus + tokenizer train input.
3. `make tokenizer` → `checkpoints/tokenizer.json`.
4. `make train` → `checkpoints/local-coder.pt`.
5. `python generate.py --prompt "..."` or REPL.
6. `make eval` → latency + structural + style-data compile gates.

### Daily use

```text
python generate.py
>>> Write a React button with typed props.
```

## UX states (CLI)

| State | Behavior |
|-------|----------|
| Primary | Prompt in, streamed/printed tokens out |
| Loading | Prints device + checkpoint path while loading |
| Empty | Missing checkpoint → exit non-zero: “run make train” |
| Error | CUDA/MPS OOM → cite DEC-01/06; corrupt ckpt → clear error |
| Unavailable | No MPS → fall back to CPU with warning (still Path A) |

## Mock views

```text
$ python generate.py --prompt "Write a React Button with Props interface"
Loading checkpoints/local-coder.pt on mps...
```typescript
function Button(props: ButtonProps) {
  ...
}
```

$ make eval
==> latency (warm n=5) PASS
==> structural cases PASS
==> style golden compile PASS
```
