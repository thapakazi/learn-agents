"""Warm-up skeleton — your tiny provider. Fill in the TODOs. Target: ~40 lines.

Two functions. Zero magic.

  chat(messages, tools=None) -> dict
      One round-trip to an OpenAI-compatible chat-completion endpoint.
      Returns the assistant message dict (has 'content' and, when tools fire,
      'tool_calls'). Defaults point at local Ollama; swap env vars to talk to
      Anthropic, OpenAI, or anything else that speaks the same JSON.

  parse_tool_args(raw) -> dict
      The model hands you a JSON *string* of arguments. Parse it. Local 14B
      models occasionally emit single quotes or trailing commas — be liberal
      on the second try, then let it fail loudly.

When both pass `just test` and `just parse-test`, drop this file into
`budo/budo/core/provider.py` (back up the existing one first) and Ch1's loop
will run against your code.
"""

from __future__ import annotations

import json
import os
from typing import Any

import httpx

# TODO(you): read these three from the environment with sensible defaults.
# Defaults should target local Ollama. The whole point: swap providers by
# changing env vars, never by editing code.
BASE_URL = os.environ.get("OPENAI_BASE_URL", "http://localhost:11434/v1")
MODEL = os.environ.get("BUDO_MODEL", "qwen2.5:14b")
API_KEY = os.environ.get(
    "OPENAI_API_KEY", "ollama"
)  # Ollama ignores it, sends nothing back angry


def chat(
    messages: list[dict[str, Any]],
    tools: list[dict] | None = None,
    temperature: float = 0.0,
) -> dict[str, Any]:
    """One chat-completion call. Returns the assistant message dict.

    Why temperature=0? Agents pick tools. Tools must be deterministic-ish or
    debugging becomes a séance.
    """
    # TODO(you): build the request body.
    #   - always: model, messages, temperature
    #   - only when non-empty: tools
    body: dict[str, Any] = {
        "model": MODEL,
        "messages": messages,
        "temperature": temperature,
    }
    # TODO(you): only attach 'tools' if the caller gave you a non-empty list.
    raise NotImplementedError("attach the tools field, then remove this line")

    # TODO(you): POST to f"{BASE_URL}/chat/completions".
    #   - send the Authorization: Bearer <API_KEY> header (Ollama ignores it; paid APIs require it)
    #   - timeout=300 (local models are slow; this is generous, not magical)
    #   - r.raise_for_status() so a 4xx/5xx becomes a real exception, not silent garbage
    # r = httpx.post(...)
    # r.raise_for_status()

    # TODO(you): the OpenAI shape is r.json()["choices"][0]["message"]. Return that dict.
    # The dict has "content" (string) and, when the model decided to call a tool,
    # a "tool_calls" list. The caller deals with both shapes.


def parse_tool_args(raw: str) -> dict[str, Any]:
    """Local models sometimes emit slightly-broken JSON args. Be liberal, fail loudly.

    Strategy:
      1. json.loads(raw) — the happy path. Most calls land here.
      2. On JSONDecodeError, clean two known sins and try again:
           - single quotes instead of double quotes
           - a trailing comma (or trailing whitespace) at the end
      3. If the cleaned parse also fails, let the exception propagate.
         Ch1's loop catches it and feeds the error back to the model so it
         can re-emit. Don't swallow exceptions here.
    """
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # TODO(you): clean the two known local-model sins, then re-parse.
        # cleaned = raw.replace(...).rstrip(...)
        # return json.loads(cleaned)
        raise NotImplementedError("clean and re-parse, then remove this line")


if __name__ == "__main__":
    # Smallest possible smoke test. As soon as chat() works, this prints a sentence.
    msg = chat([{"role": "user", "content": "Say hello in one short sentence."}])
    print(msg.get("content", "<no content>"))
