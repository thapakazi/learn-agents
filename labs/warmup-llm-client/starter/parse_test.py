"""Tiny test harness for parse_tool_args. Run via `just parse-test`.

Three cases the warmup chapter promises to handle:

  1. clean JSON                  — the happy path
  2. single-quoted               — the local-model classic
  3. trailing comma + newline    — model dribbled extra characters at the end

All three should parse to the same dict. The first failure stops nothing —
we report all three, then exit with the failure count.
"""
from __future__ import annotations

from provider_skeleton import parse_tool_args

EXPECTED = {"namespace": "shop", "tail": 100}

CASES: list[tuple[str, str]] = [
    ("clean JSON",         '{"namespace": "shop", "tail": 100}'),
    ("single-quoted",      "{'namespace': 'shop', 'tail': 100}"),
    ("trailing comma+nl",  '{"namespace": "shop", "tail": 100},\n'),
]


def main() -> int:
    failed = 0
    for label, raw in CASES:
        try:
            got = parse_tool_args(raw)
            assert got == EXPECTED, f"got {got!r}, expected {EXPECTED!r}"
            print(f"  PASS  {label}")
        except Exception as e:
            failed += 1
            print(f"  FAIL  {label}: {type(e).__name__}: {e}")
    return failed


if __name__ == "__main__":
    raise SystemExit(main())
