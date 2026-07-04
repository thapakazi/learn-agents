"""Kubernetes read tools + Ch2 findings. Solved reference for labs/ch02-skills."""
from __future__ import annotations

import re
import subprocess

from budo.core.loop import Tool

DEFAULT_TAIL = 200  # context is a budget; spend it deliberately
SINCE_RE = re.compile(r"^\d+(s|m|h)$")  # 30s, 5m, 2h — kubectl --since format


def _run(args: list[str]) -> str:
    out = subprocess.run(["kubectl", *args], capture_output=True, text=True, timeout=60)
    return (out.stdout + out.stderr).strip() or "(no output)"


def get_pods(namespace: str) -> str:
    raw = _run(["-n", namespace, "get", "pods", "-o", "wide", "--no-headers"])
    return raw + _findings_for_get_pods(raw)


def get_events(namespace: str) -> str:
    return _run(["-n", namespace, "get", "events", "--sort-by=.lastTimestamp"])


def describe(namespace: str, kind: str, name: str) -> str:
    raw = _run(["-n", namespace, "describe", kind, name])
    return raw + _findings_for_describe(raw, kind, name)


def logs(namespace: str, pod: str, container: str = "", tail: int = DEFAULT_TAIL,
         previous: bool = False, since: str = "", grep: str = "") -> str:
    args = ["-n", namespace, "logs", pod, f"--tail={min(int(tail), 1000)}"]
    if container:
        args += ["-c", container]
    if previous:
        args.append("--previous")
    if since:
        if not SINCE_RE.match(since):
            return f"error: 'since' must look like '30s', '5m', '2h' (got {since!r})"
        args.append(f"--since={since}")
    raw = _run(args)
    if not grep:
        return raw + _findings_for_logs(raw)
    try:
        pat = re.compile(grep, re.IGNORECASE)
    except re.error as e:
        return f"error: invalid grep regex {grep!r}: {e}"
    lines = raw.splitlines()
    matched = [ln for ln in lines if pat.search(ln)]
    if not matched:
        return f"(no lines matched grep={grep!r} in {len(lines)} lines; widen grep or drop it)"
    head = f"# matched {len(matched)} of {len(lines)} lines (grep={grep!r})"
    return "\n".join([head, *matched]) + _findings_for_logs(raw)


def delete_pod(namespace: str, pod: str) -> str:
    """MUTATING — gated by the approval callback in the loop."""
    return _run(["-n", namespace, "delete", "pod", pod])


# ─── Ch2: findings — deterministic invariants surfaced in tool output ────────
# Base images that legitimately don't match a workload's name.
_BENIGN_BASE_IMAGES = {"busybox", "alpine"}


def _findings_for_describe(text: str, kind: str, name: str) -> str:
    findings = []
    if kind.lower() in ("deployment", "deploy", "statefulset", "daemonset", "pod"):
        for m in re.finditer(r"^\s*Image:\s*(\S+)", text, re.MULTILINE):
            image = m.group(1)
            image_short = image.split("/")[-1].split(":")[0]
            if image_short in _BENIGN_BASE_IMAGES:
                continue
            if image_short.lower() not in name.lower() and name.lower() not in image_short.lower():
                findings.append(
                    f"image {image!r} does not match workload name {name!r} — possible wrong-image deploy"
                )
                break  # one finding per describe is enough
    return "\n\n⚠️ findings:\n" + "\n".join(f"- {f}" for f in findings) if findings else ""


def _findings_for_get_pods(text: str) -> str:
    findings = []
    for line in text.splitlines():
        cols = line.split()
        if len(cols) >= 4 and cols[3].isdigit() and int(cols[3]) > 5:
            findings.append(f"pod {cols[0]} has {cols[3]} restarts — crash-looping or flapping")
    return "\n\n⚠️ findings:\n" + "\n".join(f"- {f}" for f in findings) if findings else ""


def _findings_for_logs(text: str) -> str:
    findings = []
    if re.search(r"OOMKilled|SIGKILL|exit code 137", text, re.IGNORECASE):
        findings.append("OOM signature in log text — check memory limits (exit 137 = SIGKILL)")
    return "\n\n⚠️ findings:\n" + "\n".join(f"- {f}" for f in findings) if findings else ""


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
