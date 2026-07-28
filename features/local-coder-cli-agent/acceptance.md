# Acceptance — Local Coder CLI Agent (tools for small apps)

## Edge cases

### EDGE-01 — Path escape (P0)

**Behavior:** `../`, absolute paths, and symlink escapes are rejected with a clear `TOOL_RESULT` error; no write outside `workspace/`.

### EDGE-02 — Missing checkpoint (P0)

**Behavior:** `agent.py` exits 2 with “run make train” (same spirit as `generate.py`).

### EDGE-03 — Invalid / missing JSON tool call (P1)

**Behavior:** Parse failure produces an error observation; after 3 consecutive failures, `--task` aborts non-zero. Fail closed — do not execute prose as shell.

### EDGE-04 — Command not allowlisted (P0)

**Behavior:** `run` with `rm`, `curl`, `npm install`, or free-form bash is rejected; nothing executed.

### EDGE-05 — `run` confirmation (P1)

**Behavior:** Without `--yes`, operator must confirm; declining skips the command and returns an observation. With `--yes`, runs proceed (eval path).

### EDGE-06 — Turn limit (P1)

**Behavior:** At `max_turns`, loop stops; if `done` never seen, `--task` exits 1.

### EDGE-07 — Oversized write (P1)

**Behavior:** Content > 64 KiB rejected with error observation.

### EDGE-08 — Offline agent (P0)

**Behavior:** With local checkpoint/tokenizer, `agent.py --task ... --yes` needs no network.

### EDGE-09 — Nano quality honesty (P0 product)

**Behavior:** Docs state v1 is for small taught scaffolds, not Spring/AWS/production apps.

### EDGE-10 — generate.py unchanged for text eval (P1)

**Behavior:** Existing `make eval-structural` / latency still target `generate.py` + checkpoint; agent is additive.

## Acceptance criteria

### AC-01 — Agent CLI runs a toy task end-to-end

**Given** a tool-trained `checkpoints/local-coder.pt` and tokenizer  
**When** `python agent.py --task "Create hello/main.py that prints Hello" --yes`  
**Then** `workspace/hello/main.py` exists with expected content (or eval fixture equivalent under a temp root)  
**And** the process reaches `done` within 8 turns  

Links: DEC-01, DEC-03, DEC-04, DEC-07, EDGE-08

### AC-02 — Sandbox confinement

**Given** the tool runtime  
**When** a tool call uses `../outside.txt` or an absolute path  
**Then** no file is created outside `workspace/`  
**And** the observation reports an escape error  

Links: DEC-04, EDGE-01

### AC-03 — Allowlist enforcement

**Given** the `run` tool  
**When** argv is not in the allowlist  
**Then** the command is not executed  
**And** an error observation is returned  

Links: DEC-06, EDGE-04

### AC-04 — JSON protocol parse

**Given** model output with a valid fenced JSON tool object  
**When** the parser runs  
**Then** the correct tool + args are returned  
**And** missing/invalid JSON does not execute tools (EDGE-03)  

Links: DEC-05, EDGE-03

### AC-05 — Tool-trace data + retrain path

**Given** `data/style/tools.jsonl` and `SYSTEM_TOOLS.md`  
**When** `make data` (and train per README) runs  
**Then** tool rows are included in `data/processed/train.jsonl`  
**And** docs instruct retrain so the checkpoint learns the protocol  

Links: DEC-08, EDGE-09

### AC-06 — `make eval-agent` gate

**Given** checkpoint after tool training  
**When** `make eval-agent` runs  
**Then** unit tests for parse/sandbox/allowlist pass  
**And** at least one automated toy agent task passes with `--yes`  

Links: DEC-10, AC-01, AC-02, AC-03, AC-04

### AC-07 — Confirmation default

**Given** interactive agent without `--yes`  
**When** the model requests `run`  
**Then** the CLI prompts before execution  

Links: DEC-12, EDGE-05

### AC-08 — Docs + generate coexistence

**Given** root README and AGENTS.md  
**When** an operator follows the happy path  
**Then** agent CLI is documented as the app-building surface  
**And** `generate.py` remains documented for text-only  
**And** honesty note covers nano limits (EDGE-09, EDGE-10)  

Links: DEC-02, DEC-11, EDGE-09, EDGE-10

## Traceability matrix

| AC | Test layer | Test target | Evidence command or method |
|----|------------|-------------|----------------------------|
| AC-01 | Script / eval | `agent.py` | `make eval-agent` toy case |
| AC-02 | Unit | `agent/sandbox.py` | `pytest tests/test_agent_sandbox.py` |
| AC-03 | Unit | `agent/allowlist.py` | `pytest tests/test_agent_allowlist.py` |
| AC-04 | Unit | `agent/parse.py` | `pytest tests/test_agent_parse.py` |
| AC-05 | Data smoke | `data/processed/train.jsonl` | `make data` + grep tool rows |
| AC-06 | Make | eval-agent | `make eval-agent` |
| AC-07 | Unit or scripted stdin | confirm path | pytest with mocked input |
| AC-08 | Docs review | README, AGENTS.md | review in implement evidence |
