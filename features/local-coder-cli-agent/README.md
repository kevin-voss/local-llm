---
feature: Local Coder CLI Agent (tools for small apps)
slug: local-coder-cli-agent
status: VERIFIED
baseline_sha: 3e1dd7bc73827c32242197f4b6f78572369e916f
created: 2026-07-29
updated: 2026-07-29
implementation_sha: dcf0c814b079ce631a4376960681eba704b2a20e
verification_sha: a3e6262b498200af45b20944f5fe5efad257edff
---

# Local Coder CLI Agent (tools for small apps)

Add a **clean CLI agent** on Path A so the local nano model can build **small apps** by calling a fixed tool set: create folders/files, read files, run a short allowlisted command list, then finish — all inside a sandboxed `workspace/`. Same `checkpoints/local-coder.pt`; no Ollama, no MCP, no Spring/AWS scope in v1.

Honest scope: the loop and sandbox are the product. The nano model will only reliably drive tools on **taught** toy tasks after tool-trace training data is mixed in and weights are retrained.

## Reading order

1. `product.md` — decisions, journeys, UX
2. `technical.md` — one architecture and contracts
3. `acceptance.md` — AC / EDGE and test matrix
4. `implement.md` — ordered STEP-* plan
5. This README — status and handoff

## Readiness checklist

- [x] One architecture: `agent.py` tool loop over Path A generate
- [x] All decisions locked as `DEC-*` (no dual agent frameworks)
- [x] ACs honest for nano + tool format (not Copilot/Spring/AWS)
- [x] P0/P1 edges covered (sandbox escape, bad JSON, run allowlist)
- [x] ≤12 sequential steps for one agent
- [x] Five-file package only
- [x] No migration / multi-provider designs

## Blockers

None.

## Accepted defaults (finalize)

| Concern | Locked as | Choice |
|---------|-----------|--------|
| Primary UX | DEC-01 | `python agent.py` REPL + `--task` one-shot |
| Text-only CLI | DEC-02 | Keep `generate.py` unchanged |
| Tools | DEC-03 | Fixed: `mkdir`, `write_file`, `read_file`, `run`, `done` |
| Sandbox | DEC-04 | All FS ops under `workspace/` (gitignored) |
| Protocol | DEC-05 | One JSON object per model turn (fenced `json`) |
| Shell | DEC-06 | Allowlisted argv only; confirm `run` unless `--yes` |
| Turn budget | DEC-07 | Max 8 tool turns per task |
| Data | DEC-08 | Committed `data/style/tools.jsonl` + tool system prompt; retrain |
| Stack | DEC-09 | Pure Python loop; no MCP / LangChain / Ollama |
| Eval | DEC-10 | Parser + sandbox unit tests + `make eval-agent` toy tasks |
| Quality | DEC-11 | Ship gate = loop + sandbox + taught toys; not real apps |
| Confirm default | DEC-12 | Interactive confirm on `run`; `--yes` for eval/CI |

## Verification

| Check | Result |
|-------|--------|
| `make test` | 28 passed |
| `make eval-agent` | units + hello-main toy PASS |
| `make eval-structural` | PASS post-retrain |
| Missing ckpt | `agent.py` exit 2 |
| Live smoke | `write_file` → `done` for hello/main.py |

## Handoff

Implemented on `main`. Retrain locally after pull if checkpoint is stale: `make data tokenizer train`.
