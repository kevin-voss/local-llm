#!/usr/bin/env python3
"""Eval harness: latency + structural + style golden compile (Path A)."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from model.generate_utils import generate_text, load_checkpoint, pick_device  # noqa: E402
from scripts.extract_code import require_fence  # noqa: E402

CKPT = ROOT / "checkpoints" / "local-coder.pt"
TOK = ROOT / "checkpoints" / "tokenizer.json"
CASES = ROOT / "eval" / "cases.yaml"
STYLE = ROOT / "data" / "style"
FIXTURES = ROOT / "eval" / "fixtures"
SYSTEM = (STYLE / "SYSTEM.md").read_text(encoding="utf-8").strip()
FIXED_PROMPT = "Write a React TypeScript Button with label and onClick props."


def fail_missing() -> int:
    if not CKPT.is_file() or not TOK.is_file():
        print(
            "FAIL EDGE-02: missing checkpoints/local-coder.pt or tokenizer.json "
            "(acceptance subject is generate.py + local-coder.pt; no Ollama)",
            file=sys.stderr,
        )
        return 2
    return 0


def median(xs: list[float]) -> float:
    return float(statistics.median(xs))


def run_latency(args: argparse.Namespace) -> int:
    code = fail_missing()
    if code:
        return code
    device = pick_device()
    if device.type != "mps" and not args.allow_cpu:
        print(
            "FAIL AC-01: MPS required for latency gate (pass --allow-cpu to measure only)",
            file=sys.stderr,
        )
        return 1
    model, tokenizer, _, device = load_checkpoint(CKPT, device=device)
    # warm-up discard (EDGE-06)
    generate_text(
        model,
        tokenizer,
        FIXED_PROMPT,
        system=SYSTEM,
        max_new_tokens=args.max_new_tokens,
        temperature=0.2,
        seed=42,
        device=device,
    )
    ttfts: list[float] = []
    tps: list[float] = []
    for i in range(5):
        r = generate_text(
            model,
            tokenizer,
            FIXED_PROMPT,
            system=SYSTEM,
            max_new_tokens=args.max_new_tokens,
            temperature=0.2,
            seed=42 + i,
            device=device,
        )
        ttfts.append(r["ttft_s"])
        tps.append(r["tok_per_s"])
        print(f"  run{i+1}: ttft={r['ttft_s']:.3f}s tok/s={r['tok_per_s']:.1f}")
    m_ttft = median(ttfts)
    m_tps = median(tps)
    summary = {
        "mode": "latency",
        "device": str(device),
        "median_ttft_s": m_ttft,
        "median_tok_per_s": m_tps,
        "pass_ttft": m_ttft < 2.0,
        "pass_tps": m_tps >= 15.0,
    }
    print("SUMMARY", json.dumps(summary))
    if device.type == "mps" and (not summary["pass_ttft"] or not summary["pass_tps"]):
        print("FAIL AC-01 latency thresholds", file=sys.stderr)
        return 1
    if device.type != "mps":
        print("NOTE: CPU latency not gated (DEC-14 gate device is MPS)")
    print("==> latency (warm n=5) PASS")
    return 0


def run_structural(_args: argparse.Namespace) -> int:
    code = fail_missing()
    if code:
        return code
    with CASES.open(encoding="utf-8") as f:
        spec = yaml.safe_load(f)
    defaults = spec.get("defaults", {})
    device = pick_device()
    model, tokenizer, _, device = load_checkpoint(CKPT, device=device)
    failures: list[str] = []
    for case in spec["cases"]:
        cid = case["id"]
        prompt = case["prompt"]
        temp = float(case.get("temperature", defaults.get("temperature", 0.2)))
        if temp > 0.2:
            failures.append(f"{cid}: temperature {temp} > 0.2 (EDGE-04)")
            continue
        seed = int(case.get("seed", defaults.get("seed", 42)))
        max_new = int(case.get("max_new_tokens", defaults.get("max_new_tokens", 256)))
        r = generate_text(
            model,
            tokenizer,
            prompt,
            system=SYSTEM,
            max_new_tokens=max_new,
            temperature=temp,
            seed=seed,
            device=device,
        )
        text = r["text"]
        langs = set(case.get("require_fence_langs") or [])
        try:
            lang, _code = require_fence(text, langs if langs else None)
        except ValueError as e:
            failures.append(f"{cid}: {e} (EDGE-03)\n---\n{text[:500]}")
            continue
        for needle in case.get("must_include") or []:
            if needle not in text:
                failures.append(f"{cid}: missing {needle!r}")
        for needle in case.get("must_not_include") or []:
            if needle in text:
                failures.append(f"{cid}: banned {needle!r}")
        print(f"  {cid}: fence={lang} ok")
    summary = {"mode": "structural", "failures": len(failures)}
    print("SUMMARY", json.dumps(summary))
    if failures:
        for f in failures:
            print(f"FAIL {f}", file=sys.stderr)
        return 1
    print("==> structural cases PASS")
    return 0


def _public_java_name(code: str) -> str | None:
    m = re.search(r"public\s+(?:final\s+)?(?:class|record|interface|enum)\s+(\w+)", code)
    return m.group(1) if m else None


def ensure_fixtures_npm() -> None:
    if (FIXTURES / "node_modules").is_dir():
        return
    subprocess.run(["npm", "install"], cwd=FIXTURES, check=True)


def run_goldens(_args: argparse.Namespace) -> int:
    ensure_fixtures_npm()
    tmp = Path(tempfile.mkdtemp(prefix="local-coder-goldens-"))
    ts_dir = FIXTURES / "golden_ts"
    java_dir = tmp / "java"
    ts_dir.mkdir(parents=True, exist_ok=True)
    java_dir.mkdir(parents=True, exist_ok=True)
    # clean prior ts goldens
    for p in ts_dir.glob("*"):
        if p.is_file():
            p.unlink()

    n_ts = n_java = 0
    errors: list[str] = []
    for path in sorted(STYLE.glob("*.jsonl")):
        with path.open(encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                assistant = next(
                    m["content"] for m in obj["messages"] if m["role"] == "assistant"
                )
                try:
                    lang, code = require_fence(assistant)
                except ValueError as e:
                    errors.append(f"{path.name}:{i}: {e}")
                    continue
                if lang in {"ts", "tsx", "typescript"}:
                    ext = "tsx" if lang == "tsx" or "jsx" in code or "<" in code else "ts"
                    out = ts_dir / f"{path.stem}_{i}.{ext}"
                    out.write_text(code, encoding="utf-8")
                    n_ts += 1
                elif lang == "java":
                    name = _public_java_name(code) or f"Snippet{i}"
                    out = java_dir / f"{name}.java"
                    # avoid collisions
                    if out.exists():
                        out = java_dir / f"{name}_{path.stem}_{i}.java"
                        # if public type name mismatches filename, strip public
                        if _public_java_name(code) and _public_java_name(code) != out.stem:
                            code = re.sub(
                                r"public\s+(final\s+)?(class|record|interface|enum)",
                                r"\1\2",
                                code,
                                count=1,
                            )
                            out = java_dir / f"{name}_{path.stem}_{i}.java"
                    out.write_text(code, encoding="utf-8")
                    n_java += 1
                else:
                    # ignore other langs in style packs
                    continue

    print(f"extracted ts={n_ts} java={n_java}")

    # tsc
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "-p", "tsconfig.json"],
        cwd=FIXTURES,
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        errors.append("tsc:\n" + (r.stdout + r.stderr)[:4000])
    else:
        print("tsc PASS")

    # eslint
    r = subprocess.run(
        ["npx", "eslint", "golden_ts"],
        cwd=FIXTURES,
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        errors.append("eslint:\n" + (r.stdout + r.stderr)[:4000])
    else:
        print("eslint PASS")

    # javac each file (single compilation unit — EDGE-07)
    javac = shutil.which("javac")
    if not javac:
        errors.append("javac not found on PATH")
    else:
        for jp in sorted(java_dir.glob("*.java")):
            rr = subprocess.run(
                [javac, "-d", str(tmp / "classes"), str(jp)],
                capture_output=True,
                text=True,
            )
            if rr.returncode != 0:
                errors.append(f"javac {jp.name}:\n{(rr.stdout + rr.stderr)[:800]}")
        if not any(e.startswith("javac ") for e in errors):
            print("javac PASS")

    summary = {"mode": "goldens", "errors": len(errors), "n_ts": n_ts, "n_java": n_java}
    print("SUMMARY", json.dumps(summary))
    # cleanup java tmp; keep golden_ts for inspection
    shutil.rmtree(tmp, ignore_errors=True)
    if errors:
        for e in errors[:20]:
            print("FAIL", e, file=sys.stderr)
        if len(errors) > 20:
            print(f"... and {len(errors) - 20} more", file=sys.stderr)
        return 1
    print("==> style golden compile PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=["all", "latency", "structural", "goldens"],
        default="all",
    )
    parser.add_argument("--max-new-tokens", type=int, default=64)
    parser.add_argument(
        "--allow-cpu",
        action="store_true",
        help="allow latency mode without MPS (does not pass AC-01)",
    )
    args = parser.parse_args()
    # offline-friendly: do not require network
    os.environ.setdefault("HF_HUB_OFFLINE", "1")

    modes = {
        "latency": run_latency,
        "structural": run_structural,
        "goldens": run_goldens,
    }
    if args.mode == "all":
        rc = 0
        for name, fn in modes.items():
            print(f"==> {name}")
            r = fn(args)
            if r != 0:
                rc = r
        return rc
    return modes[args.mode](args)


if __name__ == "__main__":
    raise SystemExit(main())
