"""Kubernetes tools for the white belt. You write most of this.

`get_pods` is the worked example — read it, then mirror its shape for the others.
Tool schemas at the bottom of the file are provided (they're prose, not programming).

Read-only by design. The only mutating tool (`delete_pod`) exists to teach the
approval gate in the loop — the flag is the lesson, not the function body.

Stuck? Full reference at labs/ch01-naked-loop/starter/k8s_hint.py.
"""
from __future__ import annotations

import re
import subprocess

from budo.core.loop import Tool

DEFAULT_TAIL = 200  # context is a budget; spend it deliberately
SINCE_RE = re.compile(r"^\d+(s|m|h)$")  # 30s, 5m, 2h — kubectl --since format


def _run(args: list[str]) -> str:
    """Thin subprocess wrapper around kubectl. Provided — you don't touch it."""
    out = subprocess.run(["kubectl", *args], capture_output=True, text=True, timeout=60)
    return (out.stdout + out.stderr).strip() or "(no output)"


# ─── worked example ───────────────────────────────────────────────────
# Read this carefully. Every other tool below mirrors this shape:
#   1. A Python function that does the work and returns a string.
#   2. An entry in K8S_TOOLS (further down) pairing the function with a JSON schema.
def get_pods(namespace: str) -> str:
    return _run(["-n", namespace, "get", "pods", "-o", "wide", "--no-headers"])


# ─── you write these ──────────────────────────────────────────────────
def get_events(namespace: str) -> str:
    # TODO(you): kubectl get events -n <namespace> --sort-by=.lastTimestamp
    raise NotImplementedError("write get_events() — Ch1 step 5")


def describe(namespace: str, kind: str, name: str) -> str:
    # TODO(you): kubectl describe <kind> <name> -n <namespace>
    raise NotImplementedError("write describe() — Ch1 step 5")


def delete_pod(namespace: str, pod: str) -> str:
    """MUTATING — gated by the approval callback in the loop. The flag is the lesson."""
    # TODO(you): kubectl delete pod <pod> -n <namespace>
    raise NotImplementedError("write delete_pod() — Ch1 step 5")


def logs(namespace: str, pod: str, container: str = "", tail: int = DEFAULT_TAIL,
         previous: bool = False, since: str = "", grep: str = "") -> str:
    """Tail logs from a pod, with hard caps and an optional server-side grep."""
    # TODO(you): the dangerous one. Steps:
    #   1. base args: ["-n", namespace, "logs", pod, f"--tail={min(int(tail), 1000)}"]
    #      The min(..., 1000) is non-negotiable — context flooding is the #1 way agents die.
    #   2. optional flags: container (-c), previous (--previous), since (--since=<dur>)
    #   3. VALIDATE since against SINCE_RE first. If bad, return a clean error string —
    #      do not raise. The loop turns raised exceptions into errors too, but a clean
    #      message is a better prompt for the model.
    #   4. run _run(args), capture the raw output
    #   5. if grep is empty: return raw
    #   6. else: compile re.compile(grep, re.IGNORECASE) (return clean error on re.error),
    #      filter lines, return matched lines with a one-line header like
    #      "# matched N of M lines (grep=...)". If 0 matched, say so explicitly so the
    #      model knows to widen the pattern.
    raise NotImplementedError("write logs() — Ch1 step 6")


# ─── tool specs (provided — the descriptions ARE prompts the model reads) ───
def _ns_param():
    return {"namespace": {"type": "string", "description": "kubernetes namespace, e.g. 'shop'"}}


K8S_TOOLS: list[Tool] = [
    Tool("get_pods", "List pods in a namespace with status, restarts, node.",
         {"type": "object", "properties": _ns_param(), "required": ["namespace"]}, get_pods),
    Tool("get_events", "Recent kubernetes events in a namespace, oldest first.",
         {"type": "object", "properties": _ns_param(), "required": ["namespace"]}, get_events),
    Tool("describe", "kubectl describe a resource (pod, deployment, service, networkpolicy...).",
         {"type": "object", "properties": {**_ns_param(),
          "kind": {"type": "string"}, "name": {"type": "string"}},
          "required": ["namespace", "kind", "name"]}, describe),
    Tool("logs", "Tail logs of a pod. Use small tails first (50-200); drill down, don't dump. "
         "For noisy services (frontend, loadgenerator) FILTER: set grep='error|rpc' and since='2m' "
         "to extract signal. If grep returns nothing, widen the pattern or drop it.",
         {"type": "object", "properties": {**_ns_param(),
          "pod": {"type": "string"},
          "container": {"type": "string", "description": "optional container name"},
          "tail": {"type": "integer", "description": "lines, default 200, max 1000"},
          "previous": {"type": "boolean", "description": "previous container instance (after crash)"},
          "since": {"type": "string",
           "description": "only logs newer than this duration: '30s', '5m', '2h'. Use to zoom on a time window."},
          "grep": {"type": "string",
           "description": "case-insensitive regex filter applied server-side after fetch. "
                          "Examples: 'error', 'rpc error', 'error|fail|timeout'. Cuts noise dramatically."}},
          "required": ["namespace", "pod"]}, logs),
    Tool("delete_pod", "Delete a pod (it will be recreated by its controller). MUTATING.",
         {"type": "object", "properties": {**_ns_param(), "pod": {"type": "string"}},
          "required": ["namespace", "pod"]}, delete_pod, mutating=True),
]
