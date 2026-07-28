# Implement — Local Coder CLI Agent (tools for small apps)

One agent, sequential. Stay on Path A — extend with `agent.py` tools; do not add Ollama/MCP/LangChain.

## STEP-01 — Workspace + docs identity

**Outcome:** `workspace/` sandbox dir gitignored; README/AGENTS describe agent CLI as the small-app surface with honesty note.

**Paths**
- Create: `workspace/.gitkeep`
- Edit: `.gitignore` (`workspace/*` keep gitkeep), `README.md`, `AGENTS.md`

**Depends on:** —

**Requirements:** DEC-01, DEC-02, DEC-04, DEC-11, AC-08, EDGE-09, EDGE-10

**Tests / commands:** Docs mention `agent.py` + `workspace/`; no Ollama happy path

**Docs:** Quickstart block for agent; keep generate.py text-only section

---

## STEP-02 — Sandbox, allowlist, parser (no model)

**Outcome:** Pure Python modules enforce path safety, run allowlist, and JSON tool parse.

**Paths**
- Create: `agent/__init__.py`, `agent/sandbox.py`, `agent/allowlist.py`, `agent/parse.py`
- Create: `tests/test_agent_sandbox.py`, `tests/test_agent_allowlist.py`, `tests/test_agent_parse.py`

**Depends on:** STEP-01

**Requirements:** DEC-03, DEC-04, DEC-05, DEC-06, AC-02, AC-03, AC-04, EDGE-01, EDGE-03, EDGE-04, EDGE-07

**Tests / commands:** `pytest tests/test_agent_*.py -q`

**Docs:** —

---

## STEP-03 — Tool executors

**Outcome:** `mkdir` / `write_file` / `read_file` / `run` / `done` return structured observations; `run` respects confirm callback.

**Paths**
- Create: `agent/tools.py`
- Edit: tests for tools (temp workspace)

**Depends on:** STEP-02

**Requirements:** DEC-03, DEC-06, DEC-12, EDGE-05, EDGE-07

**Tests / commands:** pytest tool happy path + deny cases

**Docs:** —

---

## STEP-04 — Agent loop + `agent.py` CLI

**Outcome:** REPL and `--task` / `--yes` / `--max-turns` drive generate → parse → execute loop.

**Paths**
- Create: `agent/loop.py`, `agent.py`
- Reuse: `model/generate_utils.py`

**Depends on:** STEP-03

**Requirements:** DEC-01, DEC-02, DEC-07, DEC-12, AC-01, AC-07, EDGE-02, EDGE-06, EDGE-08

**Tests / commands:** Missing ckpt → exit 2; mocked-generate unit test for loop `done`; manual smoke when ckpt present

**Docs:** Daily use snippet in README

---

## STEP-05 — Tool system prompt + `tools.jsonl`

**Outcome:** ≥30 committed tool-trace examples + `SYSTEM_TOOLS.md` teaching the JSON protocol and toy scaffolds.

**Paths**
- Create: `data/style/SYSTEM_TOOLS.md`, `data/style/tools.jsonl`
- Edit: `data/style/README.md`; optional `scripts/generate_tools_data.py` if generation helps

**Depends on:** STEP-01

**Requirements:** DEC-05, DEC-08, AC-05, EDGE-09

**Tests / commands:** JSONL parse; each assistant has a parseable tool JSON fence

**Docs:** `data/style/README.md`

---

## STEP-06 — Data pipeline includes tools + retrain

**Outcome:** `make data` packs tool rows; operator retrains so checkpoint learns protocol; structural eval re-checked.

**Paths**
- Edit: `scripts/prepare_data.py` only if needed (glob should already pick up `tools.jsonl`)
- Run: `make data tokenizer train` (document duration; use existing train.py)
- Verify: `make eval-structural` still acceptable post-retrain

**Depends on:** STEP-05

**Requirements:** DEC-08, AC-05, EDGE-10

**Tests / commands:** `rg '"tool"' data/processed/train.jsonl` (or equivalent) shows tool rows; train writes `checkpoints/local-coder.pt`

**Docs:** README “retrain after tool data” note

---

## STEP-07 — `make eval-agent` harness

**Outcome:** Unit targets + at least one live toy task via agent with temp/sandbox root and `--yes`.

**Paths**
- Create: `eval/run_agent_eval.py`, `eval/agent_cases.yaml`
- Edit: `Makefile` (`eval-agent`), `eval/README.md`

**Depends on:** STEP-04, STEP-06

**Requirements:** DEC-10, AC-01, AC-06

**Tests / commands:** `make eval-agent` exit 0

**Docs:** `eval/README.md` agent section

---

## STEP-08 — Polish UX + final verification

**Outcome:** Clear tool logging, confirm copy, error messages; full AC pass; package evidence ready for VERIFIED at implement time.

**Paths**
- Edit: `agent.py` / `agent/loop.py` UX strings; README quickstart
- Run: `make test`, `make eval-agent`, spot `generate.py` still works

**Depends on:** STEP-01 … STEP-07

**Requirements:** AC-07, AC-08, EDGE-09

**Tests / commands:** Full evidence matrix green

**Docs:** Final README agent section

---

## Dependency notes

- STEP-05 `[parallel-safe]` with STEP-02–04 after STEP-01
- STEP-06 requires STEP-05; STEP-07 requires trained ckpt from STEP-06

## Docs targets

| Doc | Owner step |
|-----|------------|
| `README.md`, `AGENTS.md` | STEP-01, STEP-08 |
| `data/style/README.md` | STEP-05 |
| `eval/README.md` | STEP-07 |

## Evidence table

| Step / AC | Status | Files or evidence | Tests | Commit |
|-----------|--------|-------------------|-------|--------|
| STEP-01 | done | `workspace/.gitkeep`, `.gitignore`, `README.md`, `AGENTS.md` | docs review | dcf0c81 |
| STEP-02 | done | `agent/sandbox.py`, `allowlist.py`, `parse.py` + unit tests | `pytest tests/test_agent_*.py` 26 agent + 2 model = 28 | dcf0c81 |
| STEP-03 | done | `agent/tools.py`, `tests/test_agent_tools.py` | confirm/deny/oversized | dcf0c81 |
| STEP-04 | done | `agent/loop.py`, `agent.py`, `generate_from_messages` | missing ckpt exit 2; mocked loop done | dcf0c81 |
| STEP-05 | done | `SYSTEM_TOOLS.md`, `tools.jsonl` (35 rows), `generate_tools_data.py` | all assistants parseable | dcf0c81 |
| STEP-06 | done | `make data` → 235 rows incl. tools; `make train` → `local-coder.pt`; `make eval-structural` PASS | tool strings in train.jsonl | dcf0c81 |
| STEP-07 | done | `eval/run_agent_eval.py`, `agent_cases.yaml`, `make eval-agent` | exit 0 | dcf0c81 |
| STEP-08 | done | UX logging; full AC matrix | `make test`, `make eval-agent`, generate smoke | (this package commit) |
| AC-01 | pass | `make eval-agent` hello-main → `workspace/eval-hello-main/hello/main.py` | live agent | dcf0c81 |
| AC-02 | pass | sandbox reject `../` / abs / symlink | `test_agent_sandbox.py` | dcf0c81 |
| AC-03 | pass | rm/curl/npm rejected | `test_agent_allowlist.py` | dcf0c81 |
| AC-04 | pass | fenced JSON parse; prose fails closed | `test_agent_parse.py` | dcf0c81 |
| AC-05 | pass | tools.jsonl in prepare; retrain docs | `make data` + README | dcf0c81 |
| AC-06 | pass | `make eval-agent` | units + toy | dcf0c81 |
| AC-07 | pass | confirm callback; `--yes` for eval | `test_agent_loop.py` / tools | dcf0c81 |
| AC-08 | pass | README + AGENTS agent + generate coexistence + honesty | review | dcf0c81 |
