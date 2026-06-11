#!/usr/bin/env python3
"""Ch0 smoke test: prove the local model can call tools, end to end.

Asks: "How many pods are running in the shop namespace?" with one tool
available. Asserts the model (a) calls the tool, (b) with valid JSON args,
(c) uses the real result in its final answer.

Env:
  OPENAI_BASE_URL  default http://localhost:11434/v1  (Ollama)
  BUDO_MODEL       default qwen2.5:14b
"""
import json
import os
import subprocess
import sys
import urllib.request

BASE = os.environ.get("OPENAI_BASE_URL", "http://localhost:11434/v1")
MODEL = os.environ.get("BUDO_MODEL", "qwen2.5:14b")

TOOLS = [{
    "type": "function",
    "function": {
        "name": "kubectl_get_pods",
        "description": "List pods in a kubernetes namespace. Returns one line per pod with its status.",
        "parameters": {
            "type": "object",
            "properties": {"namespace": {"type": "string", "description": "the namespace"}},
            "required": ["namespace"],
        },
    },
}]


def chat(messages, tools=None):
    body = {"model": MODEL, "messages": messages, "temperature": 0}
    if tools:
        body["tools"] = tools
    req = urllib.request.Request(
        f"{BASE}/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY', 'ollama')}"},
    )
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read())["choices"][0]["message"]


def kubectl_get_pods(namespace: str) -> str:
    out = subprocess.run(
        ["kubectl", "-n", namespace, "get", "pods", "--no-headers"],
        capture_output=True, text=True, timeout=30,
    )
    return out.stdout or out.stderr


def main() -> int:
    messages = [
        {"role": "system", "content": "You are a kubernetes assistant. Use tools to answer; never guess."},
        {"role": "user", "content": "How many pods are currently Running in the 'shop' namespace?"},
    ]
    msg = chat(messages, TOOLS)

    calls = msg.get("tool_calls") or []
    if not calls:
        print("❌ Model answered without calling the tool. It guessed. Unacceptable.")
        print(f"   Model said: {msg.get('content')!r}")
        return 1

    call = calls[0]
    try:
        args = json.loads(call["function"]["arguments"])
        ns = args["namespace"]
    except (json.JSONDecodeError, KeyError) as e:
        print(f"❌ Tool call arguments invalid: {call['function'].get('arguments')!r} ({e})")
        return 1
    print(f"✓ model called kubectl_get_pods(namespace={ns!r})")

    result = kubectl_get_pods(ns)
    running = result.count(" Running")
    print(f"✓ tool executed: {running} pods Running")

    messages += [msg, {"role": "tool", "tool_call_id": call["id"], "content": result}]
    final = chat(messages, TOOLS)
    answer = final.get("content") or ""
    print(f"✓ final answer: {answer.strip()[:200]}")

    if str(running) not in answer:
        print(f"⚠️  answer doesn't contain the count ({running}) — model may be ignoring tool results. Re-run; if persistent, switch models (see appendix).")
        return 1
    print("🥋 Smoke passed. The model can be trusted with a sword.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
