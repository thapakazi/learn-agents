---
name: pending-pod
description: Pods stuck Pending with FailedScheduling events — insufficient resources, taints, affinity, or unbound PVCs; nothing crashed, nothing ever started
---

## When to use

Load this skill when **any** of these are true:

- `get_pods` shows STATUS `Pending` for more than ~1 minute
- Events contain `FailedScheduling`

Do not load this skill for `ContainerCreating` (scheduled fine — likely image pull or
volume mount in progress) or any status where a container has already run.

## Procedure

1. `describe pod` → the `FailedScheduling` event text states the reason verbatim.
   Classify:
   - `Insufficient cpu` / `Insufficient memory` → requests don't fit any node
   - `node(s) had untolerated taint` → taint/toleration mismatch
   - `didn't match Pod's node affinity/selector` → affinity rules exclude every node
   - `unbound immediate PersistentVolumeClaims` → storage, not compute
2. For resource cases: note the pod's **requests** (in describe) and sanity-check
   against node size — a request typo (memory: `10Gi` instead of `10Mi`) is a classic.
3. For PVC cases: `describe pvc <name>` — Pending PVC means no StorageClass, wrong
   class name, or no capacity.
4. Scheduling messages chain (`0/3 nodes are available: ...`) — report the **counts per
   reason**; the dominant reason is the real one.

## Verdict shape

ROOT CAUSE: pod/<name> unschedulable — <reason class, with the specific value that can't be satisfied>
EVIDENCE:
  - FailedScheduling: <verbatim event line>
  - describe: <the request/taint/claim detail>
FIX:
  <lower the request | add toleration/fix affinity | fix the PVC/StorageClass> — concrete command
