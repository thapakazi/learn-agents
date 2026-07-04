#!/usr/bin/env python3
"""Level checkpoints for Ch1 — The Naked Loop.

Run via:  just ch1 check <level>        (or: python3 checks/check.py <level>)

    0   bench   — cluster + model reachable (the only online check)
    1   level 1 — Tool.spec() + the minimal loop, driven by a scripted fake LLM
    2   level 2 — get_events / describe / delete_pod, driven by a fake kubectl
    3   level 3 — logs: tail cap, since validation, grep, no-match message
    4   level 4 — the messy cases: unknown tool, bad JSON, approval gate, MAX_TURNS
    5   bonus   — the Harden-it clamp (expected to fail until you do Harden it)

Levels 1-5 are fully offline: no cluster, no model, no network. They test YOUR
code's behavior, not its style — there is more than one correct loop.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# Keep the checks quiet and self-contained: audit to a temp dir, no loop chatter.
os.environ.setdefault("BUDO_AUDIT_DIR", tempfile.mkdtemp(prefix="budo-check-"))
os.environ.setdefault("BUDO_LOG_LEVEL", "quiet")

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "budo"))

# Levels 1-5 never touch the network, but importing your loop imports provider.py,
# which imports httpx. If httpx isn't installed, stub it so offline checks still run.
try:
    import httpx  # noqa: F401
except ImportError:
    import types

    _stub = types.ModuleType("httpx")
    _stub.post = lambda *a, **k: (_ for _ in ()).throw(
        RuntimeError("httpx stubbed by checks — offline checks never call it"))
    sys.modules["httpx"] = _stub

GREEN, RED, DIM, RESET = "\033[32m", "\033[31m", "\033[2m", "\033[0m"
_failed: list[str] = []


def check(cond: bool, what: str, hint: str = "") -> None:
    if cond:
        print(f"  {GREEN}✓{RESET} {what}")
    else:
        print(f"  {RED}✗{RESET} {what}")
        if hint:
            print(f"    {DIM}→ {hint}{RESET}")
        _failed.append(what)


def not_written_yet(err: NotImplementedError) -> None:
    print(f"  {DIM}○ not written yet: {err}{RESET}")
    print(f"\n{DIM}Write it first, then re-run this checkpoint.{RESET}")
    sys.exit(2)


def verdict(level: int) -> None:
    if _failed:
        print(f"\n{RED}✗ {len(_failed)} check(s) failing.{RESET} Fix them before moving on — "
              "each failure names the behavior the next level depends on.")
        sys.exit(1)
    print(f"\n{GREEN}LEVEL {level} CLEAR{RESET} 🥋  On to the next.")


# ── a scripted fake LLM: the loop can't tell it from the real one ─────────────
class FakeLLM:
    """chat()-compatible. Pops one pre-written assistant message per call."""

    def __init__(self, script: list[dict]):
        self.script = list(script)
        self.calls = 0

    def __call__(self, messages, tools=None, temperature=0.0):
        self.calls += 1
        if not self.script:
            raise AssertionError(
                "your loop called chat() more times than the script allows — "
                "check your stop condition")
        return self.script.pop(0)


def tool_call(name: str, args, call_id: str = "call_check01") -> dict:
    raw = args if isinstance(args, str) else json.dumps(args)
    return {"role": "assistant", "content": "",
            "tool_calls": [{"id": call_id, "type": "function",
                            "function": {"name": name, "arguments": raw}}]}


def final(text: str) -> dict:
    return {"role": "assistant", "content": text}


def make_agent(loop_mod, tools, script, approve=lambda _: False):
    from budo.core.audit import Audit
    agent = loop_mod.Agent(system="You are a test harness. Obey the script.",
                           tools=tools, audit=Audit("check"), approve=approve)
    loop_mod.chat = FakeLLM(script)  # the loop imported chat by name — swap it here
    return agent


def tool_messages(agent) -> list[dict]:
    return [m for m in agent.messages if m.get("role") == "tool"]


# ── a fake kubectl: records argv, returns canned output ───────────────────────
class FakeRun:
    def __init__(self, output: str = "(fake kubectl output)"):
        self.output, self.argv = output, None

    def __call__(self, args: list[str]) -> str:
        self.argv = list(args)
        return self.output


# ══ check 0 — the bench ═══════════════════════════════════════════════════════
def check_0() -> None:
    print("checkpoint 0 — the bench (online)\n")
    try:
        out = subprocess.run(["kubectl", "-n", "shop", "get", "pods", "--no-headers"],
                             capture_output=True, text=True, timeout=15)
        pods = [ln for ln in out.stdout.splitlines() if ln.strip()]
        check(out.returncode == 0 and len(pods) >= 10,
              f"shop namespace answering ({len(pods)} pods)",
              "no cluster? run `just lab-up` from the repo root (Ch0)")
    except Exception as e:
        check(False, "kubectl reachable", f"{type(e).__name__}: {e} — is the kind cluster up? (Ch0)")

    try:
        import urllib.request

        from budo.core.provider import BASE_URL
        with urllib.request.urlopen(f"{BASE_URL}/models", timeout=10) as r:
            check(r.status == 200, f"model endpoint answering at {BASE_URL}",
                  "start it: `ollama serve`, then `ollama ps`")
    except Exception as e:
        check(False, "model endpoint reachable", f"{type(e).__name__}: {e} — `ollama serve`?")
    verdict(0)


# ══ check 1 — Tool.spec() + the minimal loop ══════════════════════════════════
def check_1() -> None:
    print("checkpoint 1 — the loop runs (offline, fake LLM)\n")
    import budo.core.loop as loop

    schema = {"type": "object", "properties": {"name": {"type": "string"}},
              "required": ["name"]}
    greet = loop.Tool("greet", "Say hi to someone.", schema, lambda name: f"hi {name}")

    try:
        spec = greet.spec()
    except NotImplementedError as e:
        not_written_yet(e)
    check(spec.get("type") == "function", "spec(): top-level type is 'function'")
    fn = spec.get("function", {})
    check(fn.get("name") == "greet" and fn.get("parameters") == schema,
          "spec(): name/description/parameters under the 'function' key",
          'shape: {"type": "function", "function": {"name", "description", "parameters"}}')

    # Happy path: one tool call, then a final answer.
    agent = make_agent(loop, [greet],
                       [tool_call("greet", {"name": "budo"}), final("done: hi budo")])
    try:
        answer = agent.run("greet budo for me")
    except NotImplementedError as e:
        not_written_yet(e)
    check(answer == "done: hi budo", "run(): returns the model's final content")
    roles = [m.get("role") for m in agent.messages]
    check(roles[:2] == ["system", "user"], "run(): messages seeded with system, then user")
    tmsgs = tool_messages(agent)
    check(len(tmsgs) == 1 and tmsgs[0].get("content") == "hi budo",
          "run(): tool result appended as a role='tool' message",
          "the model only ever learns what you append")
    check(tmsgs and tmsgs[0].get("tool_call_id") == "call_check01",
          "run(): tool message carries the tool_call_id that requested it",
          "the id ties result to request — the API rejects orphans")

    # The rule that lets the agent run with unwritten tools: errors bounce back.
    def kaboom(name: str) -> str:
        raise RuntimeError("kaboom")
    bomb = loop.Tool("bomb", "Always explodes.", schema, kaboom)
    agent = make_agent(loop, [bomb], [tool_call("bomb", {"name": "x"}), final("survived")])
    answer = agent.run("poke the bomb")
    tmsgs = tool_messages(agent)
    check(answer == "survived" and tmsgs and "error" in tmsgs[0]["content"].lower()
          and "kaboom" in tmsgs[0]["content"],
          "run(): a raising tool becomes an error STRING the model can read",
          "wrap tool.fn in try/except; return f'error: {type(e).__name__}: {e}'")
    verdict(1)


# ══ check 2 — the three one-liner tools ═══════════════════════════════════════
def check_2() -> None:
    print("checkpoint 2 — the one-liner tools (offline, fake kubectl)\n")
    import budo.tools.k8s as k8s

    fake = FakeRun()
    k8s._run = fake

    for fn_name, call, need in [
        ("get_events", lambda: k8s.get_events("shop"),
         ["get", "events", "shop", "--sort-by=.lastTimestamp"]),
        ("describe", lambda: k8s.describe("shop", "deployment", "cartservice"),
         ["describe", "deployment", "cartservice", "shop"]),
        ("delete_pod", lambda: k8s.delete_pod("shop", "cartservice-abc12"),
         ["delete", "pod", "cartservice-abc12", "shop"]),
    ]:
        try:
            out = call()
        except NotImplementedError as e:
            not_written_yet(e)
        missing = [t for t in need if t not in (fake.argv or [])]
        check(not missing, f"{fn_name}: kubectl argv has {need}",
              f"missing {missing} in {fake.argv}")
        check(isinstance(out, str) and out, f"{fn_name}: returns the output string")
    verdict(2)


# ══ check 3 — logs, the dangerous one ═════════════════════════════════════════
def check_3() -> None:
    print("checkpoint 3 — logs (offline, fake kubectl)\n")
    import budo.tools.k8s as k8s

    fake = FakeRun("INFO all good\nERROR payment charge failed\ninfo shipping ok\nerror again\n")
    k8s._run = fake

    try:
        k8s.logs("shop", "frontend-abc")
    except NotImplementedError as e:
        not_written_yet(e)
    check("--tail=200" in fake.argv, "default tail is 200", f"argv: {fake.argv}")

    k8s.logs("shop", "frontend-abc", tail=5000)
    check("--tail=1000" in fake.argv, "tail is HARD-capped at 1000 (asked for 5000)",
          "min(int(tail), 1000) — context flooding is how agents die")

    out = k8s.logs("shop", "frontend-abc", since="banana")
    check(isinstance(out, str) and "error" in out.lower(),
          "invalid since='banana' returns a clean error string (no exception)")

    k8s.logs("shop", "frontend-abc", since="5m", previous=True, container="server")
    for flag in ("--since=5m", "--previous"):
        check(flag in fake.argv, f"{flag} passed through", f"argv: {fake.argv}")
    check("-c" in fake.argv and "server" in fake.argv, "container → -c server")

    out = k8s.logs("shop", "frontend-abc", grep="error")
    check("ERROR payment charge failed" in out and "error again" in out,
          "grep matches case-insensitively")
    check("INFO all good" not in out, "grep drops non-matching lines")

    out = k8s.logs("shop", "frontend-abc", grep="zebra")
    check(isinstance(out, str) and out.strip() != "" and "zebra" in out,
          "zero matches returns an explicit message naming the pattern",
          "an empty result teaches the model nothing; tell it to widen")

    out = k8s.logs("shop", "frontend-abc", grep="[")
    check(isinstance(out, str) and "error" in out.lower(),
          "invalid grep regex returns a clean error string")
    verdict(3)


# ══ check 4 — the messy cases ═════════════════════════════════════════════════
def check_4() -> None:
    print("checkpoint 4 — the messy cases (offline, fake LLM)\n")
    import budo.core.loop as loop

    schema = {"type": "object", "properties": {"name": {"type": "string"}}}
    greet = loop.Tool("greet", "Say hi.", schema, lambda name="": f"hi {name}")

    # Unknown tool name → error string, not a crash.
    agent = make_agent(loop, [greet], [tool_call("time_travel", {}), final("ok")])
    try:
        agent.run("go back to before the incident")
    except NotImplementedError as e:
        not_written_yet(e)
    t = tool_messages(agent)
    check(bool(t) and "error" in t[0]["content"].lower() and "time_travel" in t[0]["content"],
          "unknown tool → error naming it (list the available ones too)")

    # Broken JSON args → error string, not a crash.
    agent = make_agent(loop, [greet], [tool_call("greet", '{"name": "budo'), final("ok")])
    agent.run("greet with mangled args")
    t = tool_messages(agent)
    check(bool(t) and "error" in t[0]["content"].lower(),
          "invalid JSON args → error asking for a re-emit")

    # The approval gate. Deny: the function must never run.
    fired = []
    nuke = loop.Tool("nuke", "MUTATING.", schema, lambda name="": fired.append(1) or "boom",
                     mutating=True)
    agent = make_agent(loop, [nuke], [tool_call("nuke", {}), final("ok")],
                       approve=lambda _: False)
    agent.run("nuke it")
    t = tool_messages(agent)
    check(not fired, "gate DENY: the mutating function never executed",
          "check tool.mutating BEFORE calling tool.fn")
    check(bool(t) and any(w in t[0]["content"].lower() for w in ("denied", "declin")),
          "gate DENY: the model is told a human declined")

    agent = make_agent(loop, [nuke], [tool_call("nuke", {}), final("ok")],
                       approve=lambda _: True)
    agent.run("nuke it, approved")
    check(bool(fired), "gate ALLOW: approval lets the function run")

    # MAX_TURNS: a model that never answers must not spin forever.
    agent = make_agent(loop, [greet],
                       [tool_call("greet", {"name": f"t{i}"}) for i in range(loop.MAX_TURNS)])
    answer = agent.run("loop forever")
    check(isinstance(answer, str) and answer.strip() != "",
          f"MAX_TURNS ({loop.MAX_TURNS}): loop stops and returns a truncation notice",
          "a stuck agent must stop, not spiral")
    verdict(4)


# ══ check 5 — bonus: the Harden-it clamp ══════════════════════════════════════
def check_5() -> None:
    print("checkpoint 5 — hardening bonus (offline). Expected to FAIL before Harden-it.\n")
    import budo.core.loop as loop

    schema = {"type": "object", "properties": {}}
    firehose = loop.Tool("firehose", "Returns 100k chars.", schema,
                         lambda: ("x" * 99) + "\n" + ("log line of noise\n" * 5000))
    agent = make_agent(loop, [firehose], [tool_call("firehose", {}), final("ok")])
    try:
        agent.run("open the firehose")
    except NotImplementedError as e:
        not_written_yet(e)
    t = tool_messages(agent)
    size = len(t[0]["content"]) if t else 0
    check(0 < size <= 20_000, f"oversized tool result clamped before append (got {size:,} chars)",
          "clamp in the LOOP, head+tail, with an '[... omitted ...]' marker — see Harden it")
    verdict(5)


if __name__ == "__main__":
    levels = {"0": check_0, "1": check_1, "2": check_2, "3": check_3,
              "4": check_4, "5": check_5}
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    if arg not in levels:
        print(__doc__)
        sys.exit(64)
    levels[arg]()
