# Technical — Local Coder CLI Agent (tools for small apps)

## Current system

| Evidence | Finding |
|----------|---------|
| Path A | `train.py` / `generate.py` / `model/` / `eval/run_eval.py` ship VERIFIED nano toolkit |
| Infer API | `model/generate_utils.py` — `load_checkpoint`, `generate_text`, chat serialization |
| Data | `data/style/*.jsonl` + `prepare_data.py` → `data/processed/` |
| Acceptance today | Checkpoint via `generate.py` only — **no tools** |
| Production data | None |

### Reuse

- Checkpoint + tokenizer load path
- Chat serialization / special tokens
- Style JSONL packing into `prepare_data.py`
- Makefile / AGENTS.md / README identity (extend, do not revive Ollama)

### Extend

- Agent loop + tool runtime
- Tool-trace training rows
- Eval target `eval-agent`

### Delete / do not keep

- Nothing Path A to delete
- Do not add MCP servers, LangChain, Ollama wrappers, or dual “cloud agent” paths

## Final architecture (one path)

```text
checkpoints/local-coder.pt + tokenizer
        │
        ▼
   agent.py  (REPL | --task)
        │
        ├── build prompt (SYSTEM_TOOLS + history + observations)
        ├── generate_text (same Path A model)
        ├── parse one JSON tool call
        ├── tools.execute (sandbox workspace/)
        └── loop until done | max_turns | fatal error
```

| Concern | Single implementation |
|---------|----------------------|
| Model | Existing Path A GPT + `.pt` |
| Agent host | `agent.py` + `agent/` package |
| Tools | Fixed registry in `agent/tools.py` |
| FS root | `workspace/` |
| Protocol | JSON object per turn |
| Train signal | `data/style/tools.jsonl` via existing prepare/train |
| Eval | `tests/test_agent_*.py` + `eval/run_agent_eval.py` |
| Orchestration | Makefile `eval-agent`, docs in README |

## Repository layout (target additions)

```text
agent.py
agent/
  __init__.py
  loop.py          # turn loop
  parse.py         # extract/validate JSON tool call
  tools.py         # mkdir, write_file, read_file, run, done
  sandbox.py       # path resolve + escape checks
  allowlist.py     # run argv policy
data/style/
  SYSTEM_TOOLS.md
  tools.jsonl
workspace/         # gitignore contents; keep .gitkeep
eval/
  run_agent_eval.py
  agent_cases.yaml
tests/
  test_agent_parse.py
  test_agent_sandbox.py
  test_agent_allowlist.py
```

## Tool contract

### Request (model → host)

```json
{"tool":"mkdir","path":"hello"}
{"tool":"write_file","path":"hello/main.py","content":"print('Hello')\n"}
{"tool":"read_file","path":"hello/main.py"}
{"tool":"run","argv":["python3","-m","py_compile","hello/main.py"]}
{"tool":"done","summary":"Created hello app"}
```

`run` may accept `"cmd":"python3 -m py_compile hello/main.py"` as alternate; host normalizes via `shlex.split` then allowlist check. Prefer `argv` in teaching data.

### Observation (host → model)

Plain text appended to history, e.g.:

```text
<|user|>
TOOL_RESULT
ok: wrote hello/main.py (18 bytes)
```

or

```text
TOOL_RESULT
error: path escapes workspace: ../secrets
```

Exact wrapper format locked at implement time in `agent/loop.py` and mirrored in `tools.jsonl`.

## Sandbox rules

- Root: `ROOT/workspace` (absolute).
- Resolve `path` with `Path(root, path).resolve()`; require `root` is prefix.
- Reject empty paths, absolute paths, NUL, and symlink escapes.
- `write_file` creates parents as needed (or require prior `mkdir` — **decide: create parents** for nicer UX).
- Max file size for write/read: 64 KiB (reject larger).

## Allowlist (`run`)

Exact patterns (implement as structured matchers, not regex soup):

1. `["ls"]` or `["ls", "<rel>"]` where `<rel>` is sandbox-safe
2. `["pwd"]`
3. `["python3", "-m", "py_compile", "<rel.py>"]` with file under workspace

Anything else → error observation; do not execute.

Timeout: 15s per `run`. Capture stdout/stderr truncated to 4 KiB.

## Agent loop

1. Load model once.
2. Seed messages: system = `SYSTEM_TOOLS.md`; user = task.
3. Generate with temperature ≤ 0.2 for gated/eval runs; CLI default 0.2.
4. Parse tool JSON; on failure, append parse error observation and continue (count toward turns); after 3 consecutive parse failures → abort.
5. Execute tool; on `done`, print summary and exit 0.
6. Stop at `max_turns` (default 8).

`--yes`: auto-approve `run`. Without it: stdin confirm.

## Data → train

1. Author `tools.jsonl` chat rows that serialize like existing style rows but assistant content is JSON fences + optional prose; multi-step tasks can be multiple rows or one assistant message teaching a single step (prefer **many single-step** examples for nano learning, plus a few full transcripts packed as successive user/assistant turns if the serializer supports multi-message docs — use the same `messages` schema as today).
2. `prepare_data.py` already globs `data/style/*.jsonl` — no format change required if tools.jsonl matches schema.
3. Retrain: document `make data tokenizer train` (tokenizer may grow slightly). Existing non-tool structural eval should still pass or be re-checked after retrain (implement step owns re-run `make eval-structural`).

## Security / tenancy

- Local single-user
- Sandbox + allowlist are the security boundary
- No network tools
- Do not run model-written shell scripts; only allowlisted argv
- Confirm default for `run` (DEC-12)

## Concurrency / idempotency

- One agent process; no parallel tool workers
- `write_file` overwrites idempotently
- Eval uses fresh temp workspace or cleans `workspace/eval-*`

## Performance / observability

- Print each tool name + path/argv
- Log turn index / max_turns
- Reuse one model load per process

## Deletions

None required from Path A. Do not introduce Ollama/MCP leftovers.
