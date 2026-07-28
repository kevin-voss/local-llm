#!/usr/bin/env python3
"""Agent eval: unit tests + live toy task via agent.py --yes."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "eval" / "agent_cases.yaml"
DEFAULT_CKPT = ROOT / "checkpoints" / "local-coder.pt"
PYTHON = sys.executable


def run_units() -> int:
    print("==> agent parser/sandbox unit")
    proc = subprocess.run(
        [
            PYTHON,
            "-m",
            "pytest",
            "tests/test_agent_parse.py",
            "tests/test_agent_sandbox.py",
            "tests/test_agent_allowlist.py",
            "tests/test_agent_tools.py",
            "tests/test_agent_loop.py",
            "-q",
        ],
        cwd=ROOT,
    )
    if proc.returncode != 0:
        print("==> agent parser/sandbox unit FAIL")
        return proc.returncode
    print("==> agent parser/sandbox unit PASS")
    return 0


def run_toy_cases(checkpoint: Path, cases_path: Path) -> int:
    if not checkpoint.is_file():
        print(f"missing checkpoint: {checkpoint}\nrun make train", file=sys.stderr)
        return 2
    data = yaml.safe_load(cases_path.read_text(encoding="utf-8"))
    cases = data.get("cases") or []
    if not cases:
        print("no agent cases", file=sys.stderr)
        return 1

    print("==> agent toy tasks")
    for case in cases:
        case_id = case["id"]
        ws = ROOT / "workspace" / f"eval-{case_id}"
        if ws.exists():
            shutil.rmtree(ws)
        ws.mkdir(parents=True, exist_ok=True)
        task = case["task"]
        max_turns = int(case.get("max_turns", 8))
        cmd = [
            PYTHON,
            str(ROOT / "agent.py"),
            "--checkpoint",
            str(checkpoint),
            "--workspace",
            str(ws),
            "--task",
            task,
            "--yes",
            "--max-turns",
            str(max_turns),
            "--temperature",
            "0.2",
            "--seed",
            "42",
        ]
        print(f"-- case {case_id}: {task}")
        proc = subprocess.run(cmd, cwd=ROOT)
        if proc.returncode != 0:
            print(f"==> agent toy tasks FAIL ({case_id} exit {proc.returncode})")
            return proc.returncode
        for spec in case.get("expect_files") or []:
            path = ws / spec["path"]
            if not path.is_file():
                print(f"missing expected file: {path}", file=sys.stderr)
                print(f"==> agent toy tasks FAIL ({case_id})")
                return 1
            text = path.read_text(encoding="utf-8")
            needle = spec.get("contains")
            if needle and needle not in text:
                print(
                    f"file {path} missing expected content {needle!r}",
                    file=sys.stderr,
                )
                print(f"==> agent toy tasks FAIL ({case_id})")
                return 1
        print(f"   ok {case_id}")
    print("==> agent toy tasks PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CKPT)
    parser.add_argument("--cases", type=Path, default=CASES)
    parser.add_argument("--units-only", action="store_true")
    parser.add_argument("--toys-only", action="store_true")
    args = parser.parse_args()

    if not args.toys_only:
        code = run_units()
        if code != 0:
            return code
    if not args.units_only:
        code = run_toy_cases(args.checkpoint, args.cases)
        if code != 0:
            return code
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
