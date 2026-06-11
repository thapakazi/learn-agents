"""Ch1 skeleton — the naked agent loop. Fill in the TODOs. Target: <100 lines.

The contract:
  agent.run(question) ->
    loop up to MAX_TURNS:
      msg = chat(messages, tool_specs)
      if msg has no tool_calls: return msg.content       # the model is done
      for each tool_call:
        execute it (handle: unknown tool, bad JSON args, tool exception, mutation gate)
        append {"role": "tool", "tool_call_id": ..., "content": result}
"""
from dataclasses import dataclass, field
from typing import Any, Callable

MAX_TURNS = 15  # TODO(you): why must this exist? write the answer as a comment.


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
        raise NotImplementedError
