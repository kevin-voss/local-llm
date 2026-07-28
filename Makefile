# Local Coder LLM from scratch (Path A) — no Ollama
PYTHON ?= .venv/bin/python
PIP ?= .venv/bin/pip

.PHONY: help venv data tokenizer train generate eval eval-latency eval-structural eval-goldens eval-agent test smoke

help:
	@echo "Path A targets: data tokenizer train eval eval-agent (no Ollama)"
	@echo "  make data tokenizer train eval eval-agent"

venv:
	python3 -m venv .venv
	$(PIP) install -r requirements.txt

data:
	$(PYTHON) scripts/prepare_data.py --hf-max 0

tokenizer: data
	$(PYTHON) scripts/train_tokenizer.py

train: tokenizer
	$(PYTHON) train.py

generate:
	$(PYTHON) generate.py

eval-latency:
	$(PYTHON) eval/run_eval.py --mode latency

eval-structural:
	$(PYTHON) eval/run_eval.py --mode structural

eval-goldens:
	$(PYTHON) eval/run_eval.py --mode goldens

eval: eval-latency eval-structural eval-goldens

eval-agent:
	$(PYTHON) eval/run_agent_eval.py

test:
	$(PYTHON) -m pytest -q

# Short pipeline smoke (does not replace full train for AC)
smoke:
	$(PYTHON) scripts/prepare_data.py --hf-max 0
	$(PYTHON) scripts/train_tokenizer.py
	$(PYTHON) train.py --max-steps 50
	$(PYTHON) generate.py --prompt "Write a React button" --max-new-tokens 32
