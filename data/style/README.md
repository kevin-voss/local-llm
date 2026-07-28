# Style training data

Committed chat JSONL used by `scripts/prepare_data.py`. Teaches house style to the **from-scratch** model. Train must not call cloud LLM APIs.

Eval **golden compile** (`make eval-goldens`) checks that assistant targets are real, lintable/compilable code. Model generations are graded structurally in v1 (nano models struggle at full `tsc`/`javac` quality).

## Schema

Each line is one JSON object:

```json
{
  "messages": [
    {"role": "system", "content": "<from SYSTEM.md>"},
    {"role": "user", "content": "<instruction>"},
    {"role": "assistant", "content": "<fenced code + brief prose OK>"}
  ]
}
```

## Files

| File | Stack |
|------|-------|
| `react-ts.jsonl` | React + TypeScript (function components, `interface` Props, Hooks) |
| `java.jsonl` | Java 17+ (records, services, single-file units) |
| `SYSTEM.md` | Shared system prompt (packed into train sequences) |

## Contribution rules

- Assistant targets must not contain `any` or `React.FC` in TS/React examples.
- Prefer quality over bulk; keep examples self-contained and compilable.
- Regenerate via `python scripts/generate_style_data.py` only when intentionally refreshing committed files.
