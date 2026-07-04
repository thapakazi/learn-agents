"""The naked agent loop. You write this.

The whole secret:
  model -> (tool calls?) -> execute -> feed results back -> repeat -> final answer.

Everything else in agent engineering is managing what goes INTO this loop
(context) and what the loop is ALLOWED to do (tools, gates).

Stuck? Open `labs/ch01-naked-loop/starter/loop_hint.py` — a working reference.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable

from . import log
from .audit import Audit
from .provider import chat, parse_tool_args

MAX_TURNS = 15  # a stuck agent must stop, not spiral


@dataclass
class Tool:
    name: str
    description: str
    parameters: dict          # JSON schema
    fn: Callable[..., str]    # returns a string the model will read
    mutating: bool = False    # mutating tools are gated (dojo rule)

    def spec(self) -> dict:
        # TODO(you): return the OpenAI function-calling spec for this tool.
        # Shape: {"type": "function", "function": {"name", "description", "parameters"}}
        raise NotImplementedError("write Tool.spec() — Ch1 level 1")


@dataclass
class Agent:
    system: str
    tools: list[Tool]
    audit: Audit
    approve: Callable[[str], bool] = lambda _: False  # mutating-tool gate; default deny
    messages: list[dict] = field(default_factory=list)

    def run(self, user_msg: str) -> str:
        # TODO(you) — built in two passes:
        #
        # LEVEL 1 — the minimum that runs:
        #   1. seed messages with system + user
        #   2. up to MAX_TURNS, call chat(messages, [t.spec() for t in self.tools])
        #   3. no tool_calls -> return the reply's content (done)
        #   4. otherwise run each tool_call, wrap tool.fn in try/except, and append
        #      the result (or "error: <type>: <msg>") as a role="tool" message
        #
        # LEVEL 4 — the messy cases:
        #   - unknown tool name? return "error: ..." AS the tool result
        #   - parse_tool_args raised? return "error: ..." AS the tool result
        #   - tool.mutating? gate through self.approve(...) BEFORE calling tool.fn
        #   - hit MAX_TURNS without an answer? return a "truncated" notice (don't raise)
        #
        # Every tool call should be appended to self.audit so the run is replayable.
        # Checkpoints: `just ch1 check 1` and `just ch1 check 4` (offline, no cluster).
        # Stuck? Open labs/ch01-naked-loop/starter/loop_hint.py.
        raise NotImplementedError("write Agent.run() — Ch1 levels 1 and 4")
