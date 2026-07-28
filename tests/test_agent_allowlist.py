"""Run allowlist enforcement (AC-03, EDGE-04)."""

from __future__ import annotations

from pathlib import Path

from agent.allowlist import check_allowlist, normalize_argv
from agent.sandbox import ensure_root


def test_pwd_and_ls(tmp_path: Path):
    root = ensure_root(tmp_path)
    assert check_allowlist(["pwd"], root).ok
    assert check_allowlist(["ls"], root).ok
    (root / "sub").mkdir()
    assert check_allowlist(["ls", "sub"], root).ok


def test_py_compile_ok(tmp_path: Path):
    root = ensure_root(tmp_path)
    d = check_allowlist(["python3", "-m", "py_compile", "hello/main.py"], root)
    assert d.ok


def test_reject_rm_curl_npm(tmp_path: Path):
    root = ensure_root(tmp_path)
    for argv in (
        ["rm", "-rf", "/"],
        ["curl", "https://evil.example"],
        ["npm", "install"],
        ["bash", "-c", "echo hi"],
        ["python3", "-c", "print(1)"],
    ):
        d = check_allowlist(argv, root)
        assert not d.ok
        assert "not allowlisted" in (d.error or "")


def test_ls_escape_rejected(tmp_path: Path):
    root = ensure_root(tmp_path)
    d = check_allowlist(["ls", "../.."], root)
    assert not d.ok


def test_normalize_cmd_string():
    argv = normalize_argv({"cmd": "python3 -m py_compile hello/main.py"})
    assert argv == ["python3", "-m", "py_compile", "hello/main.py"]
