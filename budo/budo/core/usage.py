"""Session token & cost meter. Zero dependencies, zero magic.

Every OpenAI-compatible endpoint (Ollama included) returns a `usage` block on
each response — the bill was always there; most people just never read it:

    "usage": {"prompt_tokens": 1842, "completion_tokens": 156, "total_tokens": 1998}

`prompt_tokens` on each call IS your current context size — watching it grow
turn over turn is the context budget made visible.

Cost: set what YOUR provider charges per million tokens and the footer prices
every run. Local Ollama is $0 in dollars (you pay in watts and patience), but
pricing a local run against a hosted model is a useful habit:

    export BUDO_PRICE_IN=3.00 BUDO_PRICE_OUT=15.00   # $/Mtok, e.g. a hosted mid-tier

For traces (spans per LLM call in a real UI), see core/obs.py — BUDO_OBS=logfire.
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass, field


@dataclass
class Meter:
    calls: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    llm_seconds: float = 0.0
    last_prompt_tokens: int = 0      # context size of the most recent call
    last_completion_tokens: int = 0  # output of the most recent call
    started: float = field(default_factory=time.monotonic)

    def record(self, usage: dict | None, seconds: float) -> None:
        """Feed the `usage` block from one chat response. None-safe: some
        proxies strip usage — the meter then counts calls and time only."""
        self.calls += 1
        self.llm_seconds += seconds
        if usage:
            self.last_prompt_tokens = usage.get("prompt_tokens", 0) or 0
            self.last_completion_tokens = usage.get("completion_tokens", 0) or 0
            self.prompt_tokens += self.last_prompt_tokens
            self.completion_tokens += self.last_completion_tokens

    def cost(self) -> float | None:
        """USD for this session, or None if no prices are set."""
        p_in, p_out = os.environ.get("BUDO_PRICE_IN"), os.environ.get("BUDO_PRICE_OUT")
        if p_in is None and p_out is None:
            return None
        return (self.prompt_tokens * float(p_in or 0)
                + self.completion_tokens * float(p_out or 0)) / 1_000_000

    def call_line(self, seconds: float) -> str:
        """One-liner for the debug trace, per LLM call."""
        return (f"usage: ctx {self.last_prompt_tokens:,} tok · "
                f"+{self.last_completion_tokens} out · {seconds:.1f}s")

    def summary(self) -> str:
        """Session footer. Printed once, after the verdict."""
        c = self.cost()
        money = f"${c:.4f}" if c is not None else "$0 local (BUDO_PRICE_IN/OUT to price it)"
        return (f"⏱  {self.calls} llm calls · {self.llm_seconds:.1f}s in-model · "
                f"{self.prompt_tokens:,} in / {self.completion_tokens:,} out tok · {money}")


METER = Meter()
