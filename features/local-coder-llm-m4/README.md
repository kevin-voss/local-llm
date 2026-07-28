---
feature: Local Coder LLM from scratch (M4 16GB)
slug: local-coder-llm-m4
status: VERIFIED
baseline_sha: none
created: 2026-07-28
updated: 2026-07-28
---

# Local Coder LLM from scratch (M4 16GB)

**Path A:** build a **decoder-only Transformer in Python from scratch**, train it on Java/TS/React-flavored data, and run it with **`generate.py` loading a custom `.pth`**. No Ollama, no GGUF, no base-model LoRA, no Continue→Ollama.

Honest scope: this is a **nano from-scratch LLM toolkit** on 16GB M4. It will be slower/weaker than pretrained 7B coders; complex production React/Java is a training aspiration, not a claim that v1 replaces Copilot.

## Reading order

1. `product.md` — decisions, scope, journeys
2. `technical.md` — single architecture and contracts
3. `acceptance.md` — AC / EDGE and test matrix
4. `implement.md` — ordered STEP-* plan
5. This README — status and handoff

## Readiness checklist

- [x] Architecture pivoted to Path A (user-approved); 16GB hard budget
- [x] All decisions locked as `DEC-*` (no Ollama dual path)
- [x] ACs recalibrated for from-scratch nano model honesty
- [x] P0/P1 edges covered; every AC testable
- [x] ≤12 sequential steps for one agent
- [x] Five-file package only
- [x] No migration / multi-provider designs

## Blockers

None.

## Accepted defaults (finalize)

| Concern | Locked as | Choice |
|---------|-----------|--------|
| Host RAM | DEC-01 | 16GB unified — hard budget |
| Path | DEC-02 | **From-scratch** Transformer; **no Ollama** |
| Framework | DEC-03 | **PyTorch + MPS** (Apple Silicon) |
| Artifact | DEC-04 | Checkpoint `checkpoints/local-coder.pt` (`.pth`/`.pt`) |
| Infer | DEC-05 | **`generate.py`** only (CLI loop) |
| Size | DEC-06 | Nano config (~10–40M params); constants in `model/config.yaml` |
| Tokenizer | DEC-07 | Train BPE on our corpus (`tokenizers`); save with checkpoint |
| Train | DEC-08 | Full train from random init (`train.py`) |
| Data | DEC-09 | Filtered HF coding + committed `data/style/*.jsonl` |
| Eval | DEC-10 | Python harness → `generate.py` + structural asserts; compilers gate **style data** + structural model checks |
| IDE | DEC-11 | **None in v1** (CLI only) |
| A/B | DEC-12 | Manual vs **untrained same arch** (non-gating) |
| Project shape | DEC-13 | Standalone toolkit (not Crew Orbit apps) |
| Latency protocol | DEC-14 | Warm load; median of 5 via `generate.py` |

## Superseded (delete if present in tree)

Ollama tags, GGUF export, Modelfiles, mlx-lm LoRA on Qwen, Continue→Ollama configs — **out of architecture**. Do not revive.

## Handoff

```text
/implement-feature local-coder-llm-m4
```
