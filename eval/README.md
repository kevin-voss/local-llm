# Eval harness (Path A)

Acceptance subject: **`checkpoints/local-coder.pt`** via **`generate.py`** only. No Ollama.

## Commands

| Target | Gate |
|--------|------|
| `make eval-latency` | AC-01 warm median TTFT & tok/s (MPS) |
| `make eval-structural` | AC-03 / AC-04 fences + style cues |
| `make eval-goldens` | AC-05 style assistants compile/lint |
| `make eval` | all of the above |

## Honesty

Nano from-scratch models struggle at complex React/Java. Structural asserts grade habits (fences, keywords); golden compile proves the **teaching data** is real. Full `tsc`/`javac` on model output is not a v1 ship gate.

## Offline

With checkpoint, tokenizer, and local Node/JDK toolchains installed, `make eval` works with network disabled (EDGE-05).

## Fixtures

`eval/fixtures/` holds tsconfig/eslint/package.json for golden compile. Run `npm install` under fixtures once (Makefile does this).
