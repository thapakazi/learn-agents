#!/usr/bin/env python3
"""Level checkpoints for Ch2 — Findings & Skills.

Run via:  just ch2 check <level>        (or: python3 checks/check.py <level>)

    1   level 1 — the wrong-image finding on describe, against fixture text
    2   level 2 — restart-burst and OOM findings, against fixture text
    3   level 3 — the skill loader: parse, list, read, refuse path tricks
    4   level 4 — the router: tiny base + auto-generated catalog

Everything here is offline — no cluster, no model. This is the chapter's own
lesson eating its dog food: findings and loaders are CODE, so they're testable
at zero temperature, which is exactly why they beat prompt rules.
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("BUDO_AUDIT_DIR", tempfile.mkdtemp(prefix="budo-check-"))
os.environ.setdefault("BUDO_LOG_LEVEL", "quiet")

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "budo"))

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


def not_built_yet(what: str, level: str) -> None:
    print(f"  {DIM}○ not built yet: {what} — see Ch2 {level}{RESET}")
    print(f"\n{DIM}Build it first, then re-run this checkpoint.{RESET}")
    sys.exit(2)


def verdict(level: int) -> None:
    if _failed:
        print(f"\n{RED}✗ {len(_failed)} check(s) failing.{RESET}")
        sys.exit(1)
    print(f"\n{GREEN}LEVEL {level} CLEAR{RESET} 🥋  On to the next.")


# ── fixture text: what kubectl really returns, canned ─────────────────────────
DESCRIBE_WRONG_IMAGE = """\
Name:                   cartservice
Namespace:              shop
Selector:               app=cartservice
  Containers:
   server:
    Image:      redis:alpine
    Port:       7070/TCP
Events:
  Warning  Unhealthy  2m  kubelet  Readiness probe errored
"""

DESCRIBE_OK = DESCRIBE_WRONG_IMAGE.replace(
    "redis:alpine",
    "us-central1-docker.pkg.dev/google-samples/microservices-demo/cartservice:v0.10.2")

DESCRIBE_BENIGN = DESCRIBE_WRONG_IMAGE.replace("redis:alpine", "busybox:1.36")

GET_PODS_BURST = """\
cartservice-7f47c98499-mv6kw            0/1   Running   7 (41s ago)   6m    10.244.1.9   srebudo-worker    <none>   <none>
frontend-7d78855dd9-kbsw7               1/1   Running   0             2d    10.244.2.4   srebudo-worker2   <none>   <none>
"""

LOGS_OOM = """\
2026-07-01T14:22:07Z starting worker
Last State: Terminated, Reason: OOMKilled, exit code 137
"""


# ══ check 1 — the wrong-image finding ═════════════════════════════════════════
def check_1() -> None:
    print("checkpoint 1 — wrong-image finding (offline, fixture text)\n")
    import budo.tools.k8s as k8s

    helper = getattr(k8s, "_findings_for_describe", None)
    if helper is None:
        not_built_yet("_findings_for_describe in tools/k8s.py", "level 1")

    out = helper(DESCRIBE_WRONG_IMAGE, "deployment", "cartservice")
    check("findings" in out and "redis" in out and "cartservice" in out,
          "redis:alpine on cartservice → a finding naming both")
    check("⚠️" in out or "warning" in out.lower(),
          "the finding block is visually loud (the model reads style too)")

    check(helper(DESCRIBE_OK, "deployment", "cartservice") == "",
          "correct image → NO finding (false positives poison trust)")
    check(helper(DESCRIBE_BENIGN, "deployment", "cartservice") == "",
          "benign base image (busybox) → NO finding")
    check(helper(DESCRIBE_WRONG_IMAGE, "service", "cartservice") == "",
          "non-workload kinds are skipped")

    # And the tool itself must append it.
    class FakeRun:
        def __call__(self, args):
            return DESCRIBE_WRONG_IMAGE
    k8s._run = FakeRun()
    out = k8s.describe("shop", "deployment", "cartservice")
    check(out.startswith("Name:") and "findings" in out,
          "describe() returns raw output WITH the findings footer appended",
          "raw + _findings_for_describe(raw, kind, name)")
    verdict(1)


# ══ check 2 — restart-burst and OOM findings ══════════════════════════════════
def check_2() -> None:
    print("checkpoint 2 — restart & OOM findings (offline, fixture text)\n")
    import budo.tools.k8s as k8s

    pods = getattr(k8s, "_findings_for_get_pods", None)
    if pods is None:
        not_built_yet("_findings_for_get_pods in tools/k8s.py", "level 2")
    out = pods(GET_PODS_BURST)
    check("findings" in out and "cartservice-7f47c98499-mv6kw" in out and "7" in out,
          "7 restarts → a finding naming the pod and the count")
    check("frontend" not in out, "0 restarts → no finding for the healthy pod")

    logs_f = getattr(k8s, "_findings_for_logs", None)
    if logs_f is None:
        not_built_yet("_findings_for_logs in tools/k8s.py", "level 2")
    out = logs_f(LOGS_OOM)
    check("findings" in out and ("oom" in out.lower() or "137" in out),
          "OOMKilled / exit 137 in log text → a finding")
    check(logs_f("2026-07-01 all quiet, nothing to see") == "",
          "quiet logs → no finding")
    verdict(2)


# ══ check 3 — the skill loader ════════════════════════════════════════════════
def check_3() -> None:
    print("checkpoint 3 — skill loader (offline, temp skills dir)\n")
    try:
        import budo.tools.skills as skills
    except ImportError:
        not_built_yet("budo/budo/tools/skills.py", "level 3")

    tmp = Path(tempfile.mkdtemp(prefix="budo-skills-"))
    (tmp / "env-typo.md").write_text(
        "---\nname: env-typo\ndescription: lookup <hostname> no such host, one cluster\n---\n\n"
        "## When to use\n- dial tcp lookup errors\n\n## Procedure\n1. walk upstream\n")
    (tmp / "broken.md").write_text("no frontmatter here at all\n")
    skills.SKILLS_DIR = tmp

    listed = skills.list_skills()
    check(listed == [("env-typo", "lookup <hostname> no such host, one cluster")],
          "list_skills(): (name, description) from frontmatter, malformed file skipped",
          f"got: {listed!r}")

    body = skills.read_skill("env-typo")
    check("## Procedure" in body and "---" not in body.split("## When")[0],
          "read_skill(): returns the body, not the frontmatter")

    missing = skills.read_skill("netpol")
    check("error" in missing.lower() and "env-typo" in missing,
          "unknown skill → error LISTING what exists (errors are prompts)")

    sneaky = skills.read_skill("../../etc/passwd")
    check("error" in sneaky.lower() and "root:" not in sneaky,
          "path traversal in the name is refused",
          "resolve names only inside SKILLS_DIR; strip '/' and '..'")
    verdict(3)


# ══ check 4 — the router ══════════════════════════════════════════════════════
def check_4() -> None:
    print("checkpoint 4 — the router (offline)\n")
    import budo.__main__ as m

    base = getattr(m, "LOGS_SYSTEM_BASE", None)
    if base is None:
        not_built_yet("LOGS_SYSTEM_BASE in budo/__main__.py", "level 4")
    lines = len(base.strip().splitlines())
    check(lines < 20, f"LOGS_SYSTEM_BASE is under 20 lines (got {lines})",
          "everything class-specific moves to a finding or a skill")
    check("fabricate" in base.lower() or "no procedure matched" in base.lower(),
          "the base mandates the honest no-skill verdict")

    render = getattr(m, "render_catalog", None)
    if render is None:
        not_built_yet("render_catalog() in budo/__main__.py", "level 4")

    import budo.tools.skills as skills
    tmp = Path(tempfile.mkdtemp(prefix="budo-skills-"))
    (tmp / "crashloop.md").write_text(
        "---\nname: crashloop\ndescription: pods restarting, CrashLoopBackOff\n---\nbody\n")
    skills.SKILLS_DIR = tmp
    cat = render()
    check("crashloop" in cat and "CrashLoopBackOff" in cat,
          "render_catalog(): one line per skill on disk — drop a file, gain a route")

    skills.SKILLS_DIR = Path(tempfile.mkdtemp(prefix="budo-empty-"))
    cat = render()
    check("no skills" in cat.lower() or "(none" in cat.lower(),
          "empty skills dir → catalog says so instead of vanishing")

    check(getattr(m, "LOGS_SYSTEM", "").startswith(base[:40]),
          "LOGS_SYSTEM = base + catalog (the prompt is now GENERATED)")
    verdict(4)


if __name__ == "__main__":
    levels = {"1": check_1, "2": check_2, "3": check_3, "4": check_4}
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    if arg not in levels:
        print(__doc__)
        sys.exit(64)
    levels[arg]()
