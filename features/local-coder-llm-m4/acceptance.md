# Acceptance — Local Coder LLM from scratch (M4 16GB)

## Edge cases

### EDGE-01 — MPS / unified memory OOM during train (P0)

**Behavior:** `train.py` exits non-zero; message cites 16GB budget and nano caps in `model/config.yaml`. Does not download a pretrained LLM or invoke Ollama.

### EDGE-02 — Acceptance subject is `checkpoints/local-coder.pt` via `generate.py` (P0)

**Behavior:** Eval fails fast if checkpoint or tokenizer missing. No Ollama/cloud endpoints.

### EDGE-03 — Fence extraction failures (P1)

**Behavior:** Structural cases fail clearly if no recoverable fenced block when the case requires one.

### EDGE-04 — Nondeterminism (P1)

**Behavior:** Gated generation uses temperature ≤ 0.2 and fixed seed where applicable. Asserts are deterministic (regex/string/compile on goldens).

### EDGE-05 — Offline gate (P0)

**Behavior:** With checkpoint, tokenizer, and tools local, `make eval` works with network disabled.

### EDGE-06 — Cold vs warm latency (P1)

**Behavior:** AC-01 discards one warm-up; medians use next five.

### EDGE-07 — Single-file Java in style goldens (P1)

**Behavior:** Java style examples and structural Java cases assume one compilation unit.

### EDGE-08 — Honest quality expectation (P0 product)

**Behavior:** README states nano from-scratch models struggle at complex React/Java. Ship gate does **not** require commercial-coder quality.

### EDGE-09 — Concurrent train jobs (P1)

**Behavior:** Unsupported; documented. Makefile does not parallelize train.

### EDGE-10 — No Ollama regression (P0)

**Behavior:** Repo docs and Makefile contain no required Ollama steps for the happy path. Presence of leftover Ollama-only scripts is a defect to delete.

## Acceptance criteria

### AC-01 — Local execution and warm performance

**Given** `checkpoints/local-coder.pt` and tokenizer exist on M4 with MPS  
**When** `eval/run_eval.py` latency mode runs the fixed prompt (warm + median of 5)  
**Then** generation runs entirely via local PyTorch (`generate.py` path), offline  
**And** median TTFT &lt; 2.0 seconds  
**And** median ≥ 15 tokens/second  

Links: DEC-01, DEC-05, DEC-14, EDGE-02, EDGE-05, EDGE-06

### AC-02 — From-scratch ownership

**Given** the repository model package  
**When** an operator inspects train/infer  
**Then** weights are produced by `train.py` from random init (no pretrained LLM load)  
**And** inference loads only our checkpoint + tokenizer  
**And** happy path does not use Ollama  

Links: DEC-02, DEC-03, DEC-04, DEC-08, EDGE-10

### AC-03 — TypeScript / React structural generation

**Given** structural eval cases for React/TS  
**When** `generate.py` answers the case prompts  
**Then** outputs that claim code include a `typescript` or `tsx` fence when required  
**And** asserts check house-style cues (e.g. `function`, `interface`) and ban `any` / `React.FC` when TS-like content appears  
**And** full `tsc` pass on **model** output is **not** a v1 ship gate (see AC-05 for goldens)  

Links: DEC-10, EDGE-03, EDGE-04, EDGE-08

### AC-04 — Java structural generation

**Given** structural eval cases for Java  
**When** `generate.py` answers those prompts  
**Then** outputs include a `java` fence when required  
**And** asserts check cues required by the case (e.g. `record` or `class`, access modifiers)  
**And** full `javac` pass on **model** output is **not** a v1 ship gate  

Links: DEC-10, EDGE-03, EDGE-07, EDGE-08

### AC-05 — Style golden compile (data quality)

**Given** committed `data/style/*.jsonl` assistant targets  
**When** extract + `tsc`/`eslint`/`javac` run in eval  
**Then** goldens pass static checks (teaching signal is real code)  

Links: DEC-09, DEC-10, EDGE-07

### AC-06 — Toolkit reproducibility

**Given** deps installed and HF cache available per README  
**When** operator runs `make data tokenizer train eval`  
**Then** stages write documented artifacts ending in a usable `generate.py` session  

Links: DEC-13, AC-02

### AC-07 — Manual A/B (non-gating)

**Given** same prompt on trained ckpt vs randomly initialized same config  
**When** operator fills `eval/AB_CHECKLIST.md`  
**Then** checklist records whether trained output is more code-like / on-style  
**And** result does not affect `make eval` exit code  

Links: DEC-12

## Traceability matrix

| AC | Test layer | Test target | Evidence command or method |
|----|------------|-------------|----------------------------|
| AC-01 | Script | `generate.py` / ckpt | `make eval-latency` |
| AC-02 | Review + smoke | `model/`, `train.py`, Makefile | No `ollama` in happy path; train from scratch |
| AC-03 | Eval structural | React/TS cases | `make eval-structural` |
| AC-04 | Eval structural | Java cases | `make eval-structural` |
| AC-05 | Compile | `data/style` goldens | `make eval-goldens` |
| AC-06 | Make integration | Full pipeline | `make data tokenizer train eval` |
| AC-07 | Manual | Checklist | `eval/AB_CHECKLIST.md` |
