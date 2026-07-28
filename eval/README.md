# Eval harness (Path A)

Acceptance subjects:

- Text: **`checkpoints/local-coder.pt`** via **`generate.py`**
- Tools: same checkpoint via **`agent.py`** under a sandbox workspace

No Ollama.

## Commands

| Target | Gate |
|--------|------|
| `make eval-latency` | AC-01 warm median TTFT & tok/s (MPS) |
| `make eval-structural` | AC-03 / AC-04 fences + style cues |
| `make eval-goldens` | AC-05 style assistants compile/lint |
| `make eval` | latency + structural + goldens |
| `make eval-agent` | Agent parser/sandbox/allowlist units + toy task (`eval/agent_cases.yaml`) |

## Honesty

Nano from-scratch models struggle at complex React/Java and real apps. Structural asserts grade habits (fences, keywords); golden compile proves the **teaching data** is real. Agent eval proves the tool loop + sandbox + a **taught toy scaffold** — not Spring/AWS generators. Full `tsc`/`javac` on model output is not a v1 ship gate.

Agent toys write under `workspace/eval-*` (cleaned per case). Requires a checkpoint retrained after `data/style/tools.jsonl` is included (`make data tokenizer train`).

## Offline

With checkpoint, tokenizer, and local Node/JDK toolchains installed, `make eval` works with network disabled (EDGE-05).

## Fixtures

`eval/fixtures/` holds tsconfig/eslint/package.json for golden compile. Run `npm install` under fixtures once (Makefile does this).
