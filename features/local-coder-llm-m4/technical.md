# Technical — Local Coder LLM from scratch (M4 16GB)

## Current system

| Evidence | Finding |
|----------|---------|
| Repo | Greenfield toolkit docs + partial prior Ollama-oriented docs/data style files |
| Prior architecture | Ollama + mlx-lm LoRA + Qwen 7B — **superseded by Path A** |
| Production data | None |

### Reuse

- `data/style/` schema + `SYSTEM.md` house rules (still the teaching signal)
- Feature workflow under `.cursor/commands/`
- Chat JSONL idea for supervised-style packing

### Extend

- Replace serve/train stack with from-scratch PyTorch modules

### Delete / do not keep

- Ollama Modelfiles, GGUF export scripts, Continue→Ollama config, mlx-lm LoRA on Qwen, any Makefile targets that call `ollama`
- Dual “also support Ollama” paths

## Final architecture (one path)

```text
HF (cached) + data/style/*.jsonl
        │
        ▼
 scripts/prepare_data.py → data/processed/train.jsonl (+ plain corpus txt)
        │
        ▼
 scripts/train_tokenizer.py → checkpoints/tokenizer.json
        │
        ▼
 train.py  (PyTorch MPS, random init) → checkpoints/local-coder.pt
        │
        ▼
 generate.py  ←── eval/run_eval.py (latency + structural asserts)
        │
        └── style goldens → tsc / eslint / javac (data quality gate)
```

| Concern | Single implementation |
|---------|----------------------|
| Model | Decoder-only Transformer in `model/` (our code) |
| Framework | PyTorch, device `mps` \| `cpu` |
| Weights | `checkpoints/local-coder.pt` from **scratch** |
| Tokenizer | BPE via `tokenizers`, trained here |
| Infer | `generate.py` |
| Eval | Python harness (no Ollama) |
| Orchestration | Makefile |

## Repository layout (target)

```text
AGENTS.md
README.md
Makefile
requirements.txt
train.py
generate.py
model/
  __init__.py
  config.yaml          # nano hyperparams (DEC-06 caps)
  transformer.py       # GPT-style blocks: attn, mlp, ln, embedding
  generate_utils.py    # sampling, KV-less step loop OK for nano
data/
  style/               # committed JSONL + SYSTEM.md
  processed/           # gitignore
scripts/
  prepare_data.py
  train_tokenizer.py
  extract_code.py
checkpoints/           # gitignore *.pt; keep .gitkeep
eval/
  run_eval.py
  cases.yaml           # prompts + structural expects
  fixtures/            # tsconfig/eslint for golden compile
features/local-coder-llm-m4/
```

## Model contract

Minimal GPT-style decoder:

- Token embedding + positional embedding (learned)
- `n_layer` Transformer blocks: pre-norm causal self-attention + MLP
- LM head (optionally weight-tied with embeddings)
- Config fields: `vocab_size`, `block_size`, `n_layer`, `n_head`, `n_embd`, `dropout`

Caps (DEC-06): `n_layer≤8`, `n_embd≤512`, `n_head≤8`, `block_size≤512`, `vocab_size≤16000`.

Checkpoint dict (illustrative):

```python
{
  "model_state": ...,
  "config": {...},
  "tokenizer_path": "checkpoints/tokenizer.json",
  "train_meta": {"step": int, "loss": float},
}
```

## Data → tokens

1. `prepare_data.py` writes chat JSONL and a concatenated `data/processed/corpus.txt` for tokenizer training.
2. Chat serialization for LM training (single format):

```text
<|system|>\n...\n<|user|>\n...\n<|assistant|>\n...\n<|end|>\n
```

Special tokens registered in the BPE trainer.

3. `train.py` packs token ids into `block_size` chunks (or packed chat documents with EOS). Next-token prediction loss.

## Train hyperparams (16GB-safe)

Lock in `model/config.yaml` + train CLI defaults:

| Knob | Guidance |
|------|----------|
| Device | `mps` if `torch.backends.mps.is_available()` else `cpu` |
| Batch | small (e.g. 8–32 tokens-batches fitting 16GB); start batch 8, grad accum if needed |
| `block_size` | ≤ 512 |
| Optimizer | AdamW |
| Precision | fp32 default on MPS; optional autocast only if stable |
| Steps/epochs | config constants; stop by max_steps + eval loss print |
| Seed | fixed default for reproducibility |

On OOM: exit non-zero; suggest lowering batch/`n_embd` within caps — **do not** switch to Ollama/pretrained.

## `generate.py` contract

```bash
python generate.py --checkpoint checkpoints/local-coder.pt --prompt "..."
python generate.py   # REPL
```

- Loads config + weights + tokenizer
- Autoregressive loop; temperature default 0.2 for eval; CLI flag override
- Prints assistant-visible text (strip special tokens)
- Exit 2 if checkpoint missing

## Eval contracts

### Latency (`eval/run_eval.py` latency mode)

- Import or subprocess `generate.py` generation API
- Warm-up 1, measure 5; median TTFT & tok/s
- Pass: TTFT &lt; 2.0s and ≥ 15 tok/s on M4 MPS with nano config (CPU may be exempt documented — **gate device is MPS** when available)

### Structural cases

- Load cases from `eval/cases.yaml`
- Assert markdown fences / keywords per DEC-10
- Fail closed on missing fence (EDGE extractor)

### Style golden compile

- Extract assistant content from committed `data/style/*.jsonl`
- Run `tsc --noEmit`, eslint, `javac` — proves **targets** are valid, independent of model quality

## Security / tenancy

- Local single-user; no auth
- No cloud keys required for train/generate/eval after HF cache exists
- Do not execute model output as code beyond compile/lint
- License notes: datasets + our code; **no third-party base LLM weights**

## Concurrency / idempotency

- Single train job; Makefile sequential
- `make data|tokenizer|train|eval` overwrite known outputs idempotently

## Performance / observability

- Log device, param count, tokens/sec during train
- Eval prints JSON summary line for evidence

## Deletions

Remove or never merge: `modelfiles/`, `scripts/export_ollama.sh`, Continue Ollama examples, mlx-lm/Qwen instructions in root docs, Ollama acceptance subject language.
