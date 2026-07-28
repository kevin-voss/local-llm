"""Allowlisted argv patterns for the run tool."""

from __future__ import annotations

import shlex
from dataclasses import dataclass
from pathlib import Path

from agent.sandbox import SandboxError, resolve_in_sandbox


@dataclass(frozen=True)
class AllowlistDecision:
    ok: bool
    argv: list[str]
    error: str | None = None


def normalize_argv(call: dict) -> list[str]:
    """Accept argv list or cmd string; return argv list."""
    if "argv" in call and call["argv"] is not None:
        argv = call["argv"]
        if not isinstance(argv, list) or not all(isinstance(x, str) for x in argv):
            raise ValueError("argv must be a list of strings")
        return list(argv)
    if "cmd" in call and call["cmd"] is not None:
        cmd = call["cmd"]
        if not isinstance(cmd, str):
            raise ValueError("cmd must be a string")
        return shlex.split(cmd)
    raise ValueError("run requires argv or cmd")


def check_allowlist(argv: list[str], root: Path) -> AllowlistDecision:
    if not argv:
        return AllowlistDecision(False, argv, "error: command not allowlisted: empty argv")

    if argv == ["pwd"]:
        return AllowlistDecision(True, argv)

    if argv[0] == "ls":
        if len(argv) == 1:
            return AllowlistDecision(True, argv)
        if len(argv) == 2:
            try:
                resolve_in_sandbox(root, argv[1])
            except SandboxError as e:
                return AllowlistDecision(False, argv, str(e))
            return AllowlistDecision(True, argv)
        return AllowlistDecision(
            False, argv, f"error: command not allowlisted: {argv!r}"
        )

    if (
        len(argv) == 4
        and argv[0] == "python3"
        and argv[1] == "-m"
        and argv[2] == "py_compile"
    ):
        rel = argv[3]
        try:
            resolve_in_sandbox(root, rel)
        except SandboxError as e:
            return AllowlistDecision(False, argv, str(e))
        if not rel.endswith(".py"):
            return AllowlistDecision(
                False,
                argv,
                f"error: command not allowlisted: py_compile target must be .py: {rel}",
            )
        return AllowlistDecision(True, argv)

    return AllowlistDecision(False, argv, f"error: command not allowlisted: {argv!r}")
