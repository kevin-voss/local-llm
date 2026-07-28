# A/B checklist (AC-07, non-gating)

Compare the **same prompt** on:

1. Trained checkpoint: `checkpoints/local-coder.pt` via `generate.py`
2. Freshly initialized same architecture (random weights, same `model/config.yaml`)

`make eval` does **not** use this checklist for its exit code.

## Prompt

```text
Write a React TypeScript Button with label and onClick props.
```

## Commands

```bash
python generate.py --prompt "Write a React TypeScript Button with label and onClick props."
python -c "
from model.generate_utils import fresh_untrained, pick_device
from model.transformer import gpt_config_from_dict, load_config
from tokenizers import Tokenizer
from model.generate_utils import generate_text
from pathlib import Path
cfg = gpt_config_from_dict(load_config())
# vocab must match tokenizer
tok = Tokenizer.from_file('checkpoints/tokenizer.json')
cfg.vocab_size = tok.get_vocab_size()
m = fresh_untrained(cfg)
system = Path('data/style/SYSTEM.md').read_text().strip()
print(generate_text(m, tok, 'Write a React TypeScript Button with label and onClick props.', system=system, temperature=0.2, seed=42)['text'])
"
```

## Record

| Check | Trained | Untrained | Notes |
|-------|---------|-----------|-------|
| Produces fenced code? | | | |
| Looks more code-like? | | | |
| Closer to house style (function + interface)? | | | |

Operator: _______________ Date: _______________
