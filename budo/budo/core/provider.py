"""Provider-agnostic chat completion. One function, zero lock-in.

Local (default):  OPENAI_BASE_URL=http://localhost:11434/v1  BUDO_MODEL=qwen2.5:14b
Anthropic:        OPENAI_BASE_URL=https://api.anthropic.com/v1 ... (or use the SDK path from Ch5)
OpenAI:           OPENAI_BASE_URL=https://api.openai.com/v1 OPENAI_API_KEY=sk-...
"""
from __future__ import annotations

import json
import os
from typing import Any

import httpx

BASE_URL = os.environ.get("OPENAI_BASE_URL", "http://localhost:11434/v1")
MODEL = os.environ.get("BUDO_MODEL", "qwen2.5:14b")
API_KEY = os.environ.get("OPENAI_API_KEY", "ollama")


def chat(messages: list[dict[str, Any]], tools: list[dict] | None = None,
         temperature: float = 0.0) -> dict[str, Any]:
    """One chat-completion call. Returns the assistant message dict."""
    body: dict[str, Any] = {"model": MODEL, "messages": messages, "temperature": temperature}
    if tools:
        body["tools"] = tools
    r = httpx.post(
        f"{BASE_URL}/chat/completions",
        json=body,
        headers={"Authorization": f"Bearer {API_KEY}"},
        timeout=300,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]


def parse_tool_args(raw: str) -> dict[str, Any]:
    """Local models sometimes emit slightly-broken JSON args. Be liberal, fail loudly."""
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # common local-model sin: single quotes / trailing commas
        cleaned = raw.replace("'", '"').rstrip(", \n")
        return json.loads(cleaned)  # if this raises, the loop surfaces it to the model
