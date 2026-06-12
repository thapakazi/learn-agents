"""Ch1 skeleton — the naked agent loop. Fill in the TODOs. Target: <100 lines.

The contract:
  agent.run(question) ->
    loop up to MAX_TURNS:
      msg = chat(messages, tool_specs)
      if msg has no tool_calls: return msg.content       # the model is done
      for each tool_call:
        execute it (handle: unknown tool, bad JSON args, tool exception, mutation gate)
        append {"role": "tool", "tool_call_id": ..., "content": result}

Logging:
  The live tree at budo/budo/core/log.py defines four levels — quiet, info,
  debug, trace. Drive them with `--log-level` on the CLI or BUDO_LOG_LEVEL=...
  (BUDO_DEBUG=1 is the trace shortcut). Suggested seams:
    log.info(f"tool → {name}({preview(args)})")     # one line per tool call
    log.debug(f"turn {n}: ← {len(calls)} call(s)")  # turn boundary + result preview
    log.trace("request", body)                      # full payloads
  In this skeleton we keep a local dbg() so you can develop standalone.
"""
import json
import os
from dataclasses import dataclass, field
from typing import Any, Callable

MAX_TURNS = 15  # TODO(you): why must this exist? write the answer as a comment.

# Local dev fallback: when the loop graduates into budo/core/loop.py, swap these
# for `from budo.core import log` and use log.info / log.debug / log.trace.
DEBUG = os.environ.get("BUDO_DEBUG", "").lower() in ("1", "true", "yes")


def dbg(label: str, payload: Any = "") -> None:
    """Print a labeled blob when BUDO_DEBUG is on. Cheap, ugly, indispensable."""
    if not DEBUG:
        return
    bar = "─" * 8
    print(f"\n{bar} {label} {bar}")
    if isinstance(payload, (dict, list)):
        print(json.dumps(payload, indent=2, default=str))
    elif payload != "":
        print(payload)


@dataclass
class Tool:
    name: str
    description: str
    parameters: dict
    fn: Callable[..., str]
    mutating: bool = False

    def spec(self) -> dict:
        # TODO: return the OpenAI function-calling spec for this tool
        raise NotImplementedError


@dataclass
class Agent:
    system: str
    tools: list[Tool]
    approve: Callable[[str], bool] = lambda _: False
    messages: list[dict] = field(default_factory=list)

    def run(self, user_msg: str) -> str:
        # TODO: the loop. Decisions you must make (there are no wrong answers, only owned ones):
        #  - what goes back to the model when a tool errors? (hint: the error. models self-correct)
        #  - what happens when the model calls a tool that doesn't exist?
        #  - what happens at MAX_TURNS?
        #  - where does the mutation gate live?
        #
        # TODO(debug): once the loop runs, drop dbg() calls at these seams:
        #   dbg(f"turn {n} → chat", {"messages": self.messages})
        #   dbg(f"turn {n} ← msg",  msg)
        #   dbg(f"tool {name}",     {"args": args, "result": result})
        # Run with BUDO_DEBUG=1 the first time the agent does something weird.
        raise NotImplementedError
