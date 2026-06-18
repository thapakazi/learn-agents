"""The naked agent loop. ~80 lines. This is the whole secret.

model -> (tool calls?) -> execute -> feed results back -> repeat -> final answer.

Everything else in agent engineering is managing what goes INTO this loop
(context) and what the loop is ALLOWED to do (tools, gates).
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
        return {"type": "function", "function": {
            "name": self.name, "description": self.description, "parameters": self.parameters}}


@dataclass
class Agent:
    system: str
    tools: list[Tool]
    audit: Audit
    approve: Callable[[str], bool] = lambda _: False  # mutating-tool gate; default deny
    messages: list[dict] = field(default_factory=list)

    def run(self, user_msg: str) -> str:
        toolmap = {t.name: t for t in self.tools}
        specs = [t.spec() for t in self.tools]
        if not self.messages:
            self.messages.append({"role": "system", "content": self.system})
        self.messages.append({"role": "user", "content": user_msg})
        self.audit.log("user", content=user_msg)

        for turn in range(1, MAX_TURNS + 1):
            log.debug(f"turn {turn}: → chat ({len(self.messages)} msgs, {len(specs)} tools)")
            log.trace(f"turn {turn} request", {"messages": self.messages})
            msg = chat(self.messages, specs)
            log.trace(f"turn {turn} response", msg)
            self.messages.append(msg)
            calls = msg.get("tool_calls") or []
            if not calls:
                answer = msg.get("content") or ""
                self.audit.log("answer", content=answer)
                log.debug(f"turn {turn}: ← final answer ({len(answer)} chars)")
                return answer

            log.debug(f"turn {turn}: ← {len(calls)} tool call(s)")
            for call in calls:
                name = call["function"]["name"]
                raw_args = call["function"]["arguments"]
                log.info(f"tool → {name}({log.preview(raw_args, 120)})")
                result = self._execute(toolmap, name, raw_args)
                log.debug(f"tool ← {name}: {log.preview(result)}")
                log.trace(f"tool {name} full result", result)
                self.audit.log("tool", name=name, args=raw_args, result=result[:2000])
                self.messages.append(
                    {"role": "tool", "tool_call_id": call["id"], "content": result})

        return "⚠️ budo: hit MAX_TURNS without an answer — investigation truncated. Audit trail has everything so far."

    def _execute(self, toolmap: dict[str, Tool], name: str, raw_args: str) -> str:
        tool = toolmap.get(name)
        if tool is None:
            return f"error: no such tool '{name}'. Available: {sorted(toolmap)}"
        try:
            args = parse_tool_args(raw_args)
        except json.JSONDecodeError as e:
            return f"error: arguments were not valid JSON ({e}). Re-emit the call with valid JSON."
        if tool.mutating and not self.approve(f"{name}({args})"):
            return "denied: human declined this mutating action. Propose an alternative or explain what you would have done."
        try:
            return tool.fn(**args)
        except TypeError as e:
            return f"error: bad arguments for {name}: {e}"
        except Exception as e:  # tool errors go BACK to the model — it often self-corrects
            return f"error: {type(e).__name__}: {e}"
