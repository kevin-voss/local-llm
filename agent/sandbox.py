"""Resolve paths under workspace/ and reject escapes."""

from __future__ import annotations

from pathlib import Path

MAX_FILE_BYTES = 64 * 1024


class SandboxError(ValueError):
    """Path is empty, absolute, or escapes the workspace root."""


def ensure_root(root: Path) -> Path:
    root = Path(root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


def resolve_in_sandbox(root: Path, rel: str) -> Path:
    """Return absolute path under root, or raise SandboxError."""
    if rel is None or not str(rel).strip():
        raise SandboxError("error: path escapes workspace: (empty path)")
    raw = str(rel)
    if "\x00" in raw:
        raise SandboxError("error: path escapes workspace: NUL in path")
    p = Path(raw)
    if p.is_absolute():
        raise SandboxError(f"error: path escapes workspace: {raw}")
    root_resolved = Path(root).resolve()
    candidate = (root_resolved / p).resolve()
    try:
        candidate.relative_to(root_resolved)
    except ValueError as e:
        raise SandboxError(f"error: path escapes workspace: {raw}") from e
    return candidate
