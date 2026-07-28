# Product — Local Coder CLI Agent (tools for small apps)

## Problem

`generate.py` only prints tokens. To build **small apps locally**, the operator needs the model to **create folders/files and run a few safe commands** through a simple, trustworthy CLI — without cloud agents, Ollama, or a full IDE plugin.

## Actors

| Actor | Role |
|-------|------|
| Solo developer (operator) | Runs `agent.py`, reviews `run` prompts, inspects `workspace/` |

## Goals

1. Nice daily CLI: describe a small app task → files appear under `workspace/`.
2. Fixed, readable tool protocol the nano model can be taught.
3. Hard sandbox: no writes outside `workspace/`; no arbitrary shell.
4. Same Path A checkpoint (`checkpoints/local-coder.pt`); offline after train.
5. Honest v1: toy apps / scaffolding habits, not Spring Boot or AWS CDK.

## Non-goals

- MCP, LangChain, CrewAI, Continue.dev, IDE plugins
- Ollama / GGUF / pretrained base swap
- Spring Boot, AWS (CDK/S3/DynamoDB/SQS), production app generators
- Unrestricted shell, network-fetch tools, package installers as default tools
- Multi-agent orchestration, RAG, browser tools
- Replacing `generate.py` (text-only stays)

## Scope

### In

- `agent.py` (REPL + `--task`)
- Tool runtime: `mkdir`, `write_file`, `read_file`, `run`, `done`
- Sandbox root `workspace/`
- Tool-trace style data + system prompt; prepare_data + retrain path
- `make eval-agent` + unit tests for parser/sandbox
- README / AGENTS updates for the agent happy path

### Out

See Non-goals.

## Decisions

### DEC-01 — Primary surface is `agent.py`

**Decision:** Daily “build a small app” UX is `python agent.py` (REPL) and `python agent.py --task "..."`.

**Rejected:** HTTP server; IDE agent; folding tools into `generate.py` flags as the only surface.

### DEC-02 — Keep `generate.py` for text-only

**Decision:** Pure generation remains `generate.py`. Agent imports shared load/generate helpers; does not remove or break existing eval that shells `generate.py`.

**Rejected:** Merge everything into one CLI with confusing modes as the sole entrypoint.

### DEC-03 — Fixed five tools

**Decision:** Exactly these tools in v1:

| Tool | Purpose |
|------|---------|
| `mkdir` | Create directory under workspace |
| `write_file` | Create/overwrite a text file |
| `read_file` | Read a text file (for follow-up turns) |
| `run` | Execute one allowlisted command |
| `done` | End the task with a short summary |

**Rejected:** Open-ended “bash”; dozens of tools; MCP tool discovery.

### DEC-04 — Sandbox root `workspace/`

**Decision:** All relative paths resolve under repo `workspace/` (created on demand). Absolute paths, `..` escape, and symlinks that leave the root are rejected.

**Rejected:** Writing into the repo root / `model/` / home directory.

### DEC-05 — One JSON tool call per turn

**Decision:** Each model response that acts must contain a single fenced JSON object:

```json
{"tool":"write_file","path":"app/main.py","content":"..."}
```

or `done`:

```json
{"tool":"done","summary":"..."}
```

Parser fails closed if no valid object. Optional brief prose outside the fence is ignored for execution.

**Rejected:** XML tool tags; free-form “I’ll run mkdir…” without JSON; parallel multi-tool arrays in v1.

### DEC-06 — Allowlisted `run` only

**Decision:** `run` accepts a string argv list (or a single string that is split with shlex) matched against a fixed allowlist, e.g.:

- `ls`, `pwd`
- `python3` with only `-m py_compile <path>` (path under workspace)
- `npx tsc --noEmit` only when `package.json`/`tsconfig` exist under the task dir (optional; if too heavy, drop and keep python compile + `ls`)

**Locked minimal allowlist for v1:** `ls`, `pwd`, `python3 -m py_compile <workspace-relative-file>`.

**Rejected:** `rm -rf`, `curl`, `npm install`, `pip install`, arbitrary `bash -c`.

### DEC-07 — Max 8 turns

**Decision:** Default `max_turns=8`. Exceeding prints a clear stop message and non-zero exit for `--task` if `done` never called.

**Rejected:** Unbounded loops.

### DEC-08 — Teach tools with committed JSONL + retrain

**Decision:** Add `data/style/tools.jsonl` (≥30 multi-turn or single-step tool traces) and `data/style/SYSTEM_TOOLS.md`. `prepare_data.py` includes them. Operator runs tokenizer if needed + `make train` (or documented short retrain) so the checkpoint learns the JSON habit.

**Rejected:** Hoping the current non-tool checkpoint invents the protocol; runtime-only prompt engineering as the sole teaching signal (prompt still used, but data+train is required for AC).

### DEC-09 — Pure Python agent loop

**Decision:** Implement loop in-repo (`agent.py` + `agent/` package). No third-party agent framework.

**Rejected:** LangChain, LlamaIndex agents, MCP host.

### DEC-10 — Eval is loop + toys, not app quality

**Decision:** Automated gates: unit tests (sandbox, parser, allowlist) + `make eval-agent` tasks that assert expected files/content after a full agent run with `--yes`.

**Rejected:** Requiring the nano model to scaffold Spring/AWS; LLM-as-judge.

### DEC-11 — Quality honesty

**Decision:** README states clearly: v1 agent is for **small taught scaffolds** (e.g. one Python file + folder). Complex apps remain out of reach for this nano from-scratch model.

**Rejected:** Marketing the agent as a general app builder.

### DEC-12 — Confirm `run` by default

**Decision:** Interactive REPL/`--task` without `--yes` prompts `Run? [y/N]` before each `run`. Eval and automation pass `--yes`.

**Rejected:** Silent shell execution as the default.

## Business rules

1. After checkpoint + tokenizer exist (post tool-data retrain), `agent.py` works offline.
2. Tools never write outside `workspace/`.
3. `generate.py` remains the text-only Path A surface; agent is additive.
4. No Ollama in the agent happy path.
5. Do not execute model output as unrestricted shell.

## Journeys

### Happy path — one-shot

1. `make data tokenizer train` (after tool JSONL lands) if weights are stale.
2. `python agent.py --task "Create a Python hello app under hello/ with main.py that prints Hello" --yes`
3. Inspect `workspace/hello/main.py`.
4. Agent prints `done` summary.

### Daily REPL

```text
python agent.py
>>> Create a folder demo and write demo/app.py that prints hi
[tool] mkdir demo
[tool] write_file demo/app.py
[tool] done
```

### Eval

```text
make eval-agent
==> agent parser/sandbox unit PASS
==> agent toy tasks PASS
```

## UX states (CLI)

| State | Behavior |
|-------|----------|
| Primary | Task in → tool lines + final summary |
| Loading | Prints device + checkpoint while loading |
| Confirm | `Run allowlisted command: … ? [y/N]` |
| Empty / missing ckpt | Exit 2: run make train |
| Parse error | Print error, feed observation back or fail closed on `--task` after N parse fails |
| Sandbox deny | Observation: `error: path escapes workspace` |
| Allowlist deny | Observation: `error: command not allowlisted` |
| Turn limit | Stop with message; `--task` exit 1 if not `done` |
| Unavailable | No MPS → CPU warning (same as generate) |

## Mock views

```text
$ python agent.py --task "Create hello/main.py that prints Hello" --yes
Loading checkpoints/local-coder.pt on mps...
→ mkdir {"path":"hello"}
→ write_file {"path":"hello/main.py"}
→ run ["python3","-m","py_compile","hello/main.py"]  (ok)
→ done Create hello/main.py
```

```text
$ python agent.py
>>> make a tiny demo folder with readme
→ mkdir demo
→ write_file demo/README.md
→ done
```
