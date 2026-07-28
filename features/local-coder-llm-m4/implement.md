# Implement — Local Coder LLM from scratch (M4 16GB)

One agent, sequential. **Path A only** — do not add Ollama, GGUF, or pretrained base weights.

## STEP-01 — Project identity (Path A)

**Outcome:** Root docs and `.gitignore` describe from-scratch PyTorch nano LLM; Ollama language removed.

**Paths**
- Create/Edit: `AGENTS.md`, `README.md`, `.gitignore`
- Delete if present: Ollama-centric happy-path docs references; `modelfiles/` instructions

**Depends on:** —

**Requirements:** DEC-01, DEC-02, DEC-13, EDGE-08, EDGE-10

**Tests / commands:** README states Path A + quality caveat; `.gitignore` includes `checkpoints/*.pt`, `data/processed/`, `.venv/`, `eval/results/`

**Docs:** Prerequisites = Python 3.11+, PyTorch MPS, optional JDK/Node for golden compile — **not** Ollama.

---

## STEP-02 — Style data + system prompt

**Outcome:** Committed style JSONL + `SYSTEM.md` remain teaching signal; README notes goldens must compile.

**Paths**
- Keep/Edit: `data/style/*` (schema unchanged)
- Edit: `data/style/README.md` (tokenizer/train from scratch; no Modelfile)

**Depends on:** STEP-01

**Requirements:** DEC-09, AC-05

**Tests / commands:** JSONL parse; spot-check bans on `any` / `React.FC`

**Docs:** `data/style/README.md`

---

## STEP-03 — Data preparation

**Outcome:** `make data` writes `data/processed/train.jsonl` + `corpus.txt` for tokenizer.

**Paths**
- Create/Edit: `scripts/prepare_data.py`, `requirements.txt`, Makefile `data`

**Depends on:** STEP-02

**Requirements:** DEC-09, AC-06

**Tests / commands:** `make data`; files exist; chat serialization documented

**Docs:** README Data section

---

## STEP-04 — Model package (Transformer)

**Outcome:** Nano GPT-style model in `model/` with config caps enforced.

**Paths**
- Create: `model/config.yaml`, `model/transformer.py`, `model/__init__.py`, `model/generate_utils.py`

**Depends on:** STEP-01

**Requirements:** DEC-03, DEC-06, AC-02

**Tests / commands:** Unit test: construct model, forward dummy batch on MPS/CPU; assert param count within 10–40M band

**Docs:** Brief `model` section in README

---

## STEP-05 — Tokenizer training

**Outcome:** `make tokenizer` → `checkpoints/tokenizer.json` with special tokens.

**Paths**
- Create: `scripts/train_tokenizer.py`, Makefile `tokenizer`, `checkpoints/.gitkeep`

**Depends on:** STEP-03

**Requirements:** DEC-07

**Tests / commands:** Encode/decode roundtrip on sample chat string

**Docs:** README Tokenizer

---

## STEP-06 — `train.py` from scratch

**Outcome:** `make train` writes `checkpoints/local-coder.pt` from random init.

**Paths**
- Create: `train.py`, Makefile `train`

**Depends on:** STEP-04, STEP-05

**Requirements:** DEC-08, EDGE-01, EDGE-09, AC-02, AC-06

**Tests / commands:** Short smoke max_steps; verify checkpoint keys; confirm no HF model weight download for LLM base

**Docs:** Train section + OOM hints

---

## STEP-07 — `generate.py`

**Outcome:** CLI REPL + `--prompt` loads checkpoint and generates offline.

**Paths**
- Create: `generate.py`

**Depends on:** STEP-06

**Requirements:** DEC-05, DEC-04, EDGE-02, AC-01, AC-02

**Tests / commands:** Missing ckpt → exit 2; smoke prompt on trained ckpt

**Docs:** Daily use in README

---

## STEP-08 — Extractor + style golden compile

**Outcome:** `make eval-goldens` compiles/lints committed style assistants.

**Paths**
- Create: `scripts/extract_code.py`, `eval/fixtures/*`, Makefile `eval-goldens`

**Depends on:** STEP-02

**Requirements:** AC-05, EDGE-03, EDGE-07

**Tests / commands:** Goldens pass tsc/eslint/javac

**Docs:** `eval/README.md`

---

## STEP-09 — Eval harness (latency + structural)

**Outcome:** `make eval` runs latency + structural cases against `generate.py`.

**Paths**
- Create: `eval/run_eval.py`, `eval/cases.yaml`, `eval/AB_CHECKLIST.md`, Makefile `eval`, `eval-latency`, `eval-structural`

**Depends on:** STEP-07, STEP-08

**Requirements:** AC-01, AC-03, AC-04, AC-07, DEC-10, DEC-12, DEC-14, EDGE-04, EDGE-05, EDGE-06

**Tests / commands:** `make eval` exit codes; temperature ≤ 0.2 on gated runs

**Docs:** Eval thresholds + honesty note

---

## STEP-10 — Purge Ollama leftovers + E2E smoke

**Outcome:** No Ollama in happy path; `make data tokenizer train eval` documented and smoke-run.

**Paths**
- Delete: `modelfiles/`, `scripts/export_ollama.sh`, Continue Ollama configs, any mlx-lm/Qwen export docs if present
- Edit: Makefile phony targets; root README quickstart

**Depends on:** STEP-01 … STEP-09

**Requirements:** EDGE-10, AC-06

**Tests / commands:** `rg -i ollama Makefile README.md AGENTS.md` → no required happy-path hits; pipeline smoke

**Docs:** Final quickstart block

---

## Dependency notes

- STEP-04 `[parallel-safe]` with STEP-02–03 after STEP-01
- STEP-08 `[parallel-safe]` with STEP-04–07 after STEP-02

## Docs targets

| Doc | Owner step |
|-----|------------|
| `AGENTS.md`, `README.md` | STEP-01, STEP-10 |
| `data/style/README.md` | STEP-02 |
| `eval/README.md` | STEP-08, STEP-09 |

## Evidence table

| Step / AC | Status | Files or evidence | Tests | Commit |
|-----------|--------|-------------------|-------|--------|
| STEP-01 | done | `AGENTS.md`, `README.md`, `.gitignore` Path A | docs + gitignore caps | _(impl)_ |
| STEP-02 | done | `data/style/*`, generator fixes for compile | banned `any`/`React.FC` = 0 | _(impl)_ |
| STEP-03 | done | `scripts/prepare_data.py`, `make data` | train.jsonl + corpus.txt | _(impl)_ |
| STEP-04 | done | `model/*` nano GPT 11.36M params | `make test` 2 passed | _(impl)_ |
| STEP-05 | done | `scripts/train_tokenizer.py`, ByteLevel decoder | encode/decode roundtrip | _(impl)_ |
| STEP-06 | done | `train.py` → `checkpoints/local-coder.pt` | 2000 steps MPS loss≈0.027 | _(impl)_ |
| STEP-07 | done | `generate.py` REPL + `--prompt` | missing ckpt exit 2; smoke Button | _(impl)_ |
| STEP-08 | done | `scripts/extract_code.py`, `eval/fixtures` | tsc/eslint/javac PASS | _(impl)_ |
| STEP-09 | done | `eval/run_eval.py`, `cases.yaml`, `AB_CHECKLIST.md` | structural+latency PASS | _(impl)_ |
| STEP-10 | done | no `modelfiles/` / export_ollama; Makefile Path A | rg ollama = reject-only | _(impl)_ |
| AC-01 | pass | median TTFT 0.012s, 73.9 tok/s MPS | `make eval-latency` | _(impl)_ |
| AC-02 | pass | random-init `train.py`; no pretrained LLM load | review + `make test` | _(impl)_ |
| AC-03 | pass | react-button, react-counter | `make eval-structural` | _(impl)_ |
| AC-04 | pass | java-record, java-service | `make eval-structural` | _(impl)_ |
| AC-05 | pass | 100 TS + 100 Java goldens | `make eval-goldens` | _(impl)_ |
| AC-06 | pass | `make data tokenizer train` + generate | pipeline smoke | _(impl)_ |
| AC-07 | pass | `eval/AB_CHECKLIST.md` non-gating | manual checklist present | _(impl)_ |
