"""Sandbox path confinement (AC-02, EDGE-01, EDGE-07)."""

from __future__ import annotations

from pathlib import Path

import pytest

from agent.sandbox import MAX_FILE_BYTES, SandboxError, ensure_root, resolve_in_sandbox


def test_resolve_relative_ok(tmp_path: Path):
    root = ensure_root(tmp_path / "workspace")
    p = resolve_in_sandbox(root, "hello/main.py")
    assert p == (root / "hello" / "main.py").resolve()
    assert root.resolve() in p.parents or p.parent == root.resolve()


def test_reject_parent_escape(tmp_path: Path):
    root = ensure_root(tmp_path / "workspace")
    with pytest.raises(SandboxError, match="escapes workspace"):
        resolve_in_sandbox(root, "../outside.txt")


def test_reject_absolute(tmp_path: Path):
    root = ensure_root(tmp_path / "workspace")
    with pytest.raises(SandboxError, match="escapes workspace"):
        resolve_in_sandbox(root, "/etc/passwd")


def test_reject_empty(tmp_path: Path):
    root = ensure_root(tmp_path / "workspace")
    with pytest.raises(SandboxError):
        resolve_in_sandbox(root, "")
    with pytest.raises(SandboxError):
        resolve_in_sandbox(root, "   ")


def test_symlink_escape(tmp_path: Path):
    root = ensure_root(tmp_path / "workspace")
    outside = tmp_path / "secret.txt"
    outside.write_text("nope", encoding="utf-8")
    link = root / "leak"
    link.symlink_to(outside)
    with pytest.raises(SandboxError, match="escapes workspace"):
        resolve_in_sandbox(root, "leak")


def test_max_file_constant():
    assert MAX_FILE_BYTES == 64 * 1024
