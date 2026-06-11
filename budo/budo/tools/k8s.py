"""Kubernetes read tools for the white belt. Read-only by design —
the only mutating tool (delete_pod) exists to teach the approval gate."""
from __future__ import annotations

import subprocess

from budo.core.loop import Tool

DEFAULT_TAIL = 200  # context is a budget; spend it deliberately


def _run(args: list[str]) -> str:
    out = subprocess.run(["kubectl", *args], capture_output=True, text=True, timeout=60)
    return (out.stdout + out.stderr).strip() or "(no output)"


def get_pods(namespace: str) -> str:
    return _run(["-n", namespace, "get", "pods", "-o", "wide", "--no-headers"])


def get_events(namespace: str) -> str:
    return _run(["-n", namespace, "get", "events", "--sort-by=.lastTimestamp"])


def describe(namespace: str, kind: str, name: str) -> str:
    return _run(["-n", namespace, "describe", kind, name])


def logs(namespace: str, pod: str, container: str = "", tail: int = DEFAULT_TAIL,
         previous: bool = False) -> str:
    args = ["-n", namespace, "logs", pod, f"--tail={min(int(tail), 1000)}"]
    if container:
        args += ["-c", container]
    if previous:
        args.append("--previous")
    return _run(args)


def delete_pod(namespace: str, pod: str) -> str:
    """MUTATING — gated by the approval callback in the loop."""
    return _run(["-n", namespace, "delete", "pod", pod])


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
    Tool("logs", "Tail logs of a pod. Use small tails first (50-200); drill down, don't dump.",
         {"type": "object", "properties": {**_ns_param(),
          "pod": {"type": "string"},
          "container": {"type": "string", "description": "optional container name"},
          "tail": {"type": "integer", "description": "lines, default 200, max 1000"},
          "previous": {"type": "boolean", "description": "previous container instance (after crash)"}},
          "required": ["namespace", "pod"]}, logs),
    Tool("delete_pod", "Delete a pod (it will be recreated by its controller). MUTATING.",
         {"type": "object", "properties": {**_ns_param(), "pod": {"type": "string"}},
          "required": ["namespace", "pod"]}, delete_pod, mutating=True),
]
