"""Tiny level-based logger for the loop. No Python `logging` ceremony.

Levels (lowest → loudest):
    QUIET   only the final answer
    INFO    one line per tool call + turn boundaries (default)
    DEBUG   + truncated tool result previews + http response shape
    TRACE   + full request/response/result bodies

Set with BUDO_LOG_LEVEL=info|debug|trace (or pass --log-level to budo).
BUDO_DEBUG=1 is kept as a shortcut for TRACE so old habits still work.
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any

QUIET, INFO, DEBUG, TRACE = 0, 1, 2, 3
_NAMES = {"quiet": QUIET, "info": INFO, "debug": DEBUG, "trace": TRACE}


def _initial_level() -> int:
    if os.environ.get("BUDO_DEBUG", "").lower() in ("1", "true", "yes"):
        return TRACE
    return _NAMES.get(os.environ.get("BUDO_LOG_LEVEL", "info").lower(), INFO)


LEVEL: int = _initial_level()


def set_level(name_or_int: str | int) -> None:
    global LEVEL
    LEVEL = name_or_int if isinstance(name_or_int, int) else _NAMES.get(name_or_int.lower(), INFO)


def enabled(level: int) -> bool:
    return LEVEL >= level


def _emit(prefix: str, msg: str) -> None:
    print(f"{prefix} {msg}", file=sys.stderr)


def info(msg: str) -> None:
    if LEVEL >= INFO:
        _emit("·", msg)


def debug(msg: str) -> None:
    if LEVEL >= DEBUG:
        _emit("»", msg)


def trace(label: str, payload: Any = "") -> None:
    if LEVEL < TRACE:
        return
    bar = "─" * 8
    print(f"\n{bar} {label} {bar}", file=sys.stderr)
    if isinstance(payload, (dict, list)):
        print(json.dumps(payload, indent=2, default=str), file=sys.stderr)
    elif payload != "":
        print(payload, file=sys.stderr)


def preview(s: str, n: int = 240) -> str:
    """One-line preview of a tool result for INFO/DEBUG output."""
    flat = " ".join(s.split())
    return flat if len(flat) <= n else flat[:n] + f"… (+{len(flat) - n} chars)"
