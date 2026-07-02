---
name: oomkilled
description: Containers killed with exit code 137 / OOMKilled — memory limit too low or a real leak; the restart PATTERN tells you which
---

## When to use

Load this skill when **any** of these are true:

- A findings block or log text mentions `OOMKilled` or `exit code 137`
- `describe pod` shows `Last State: Terminated, Reason: OOMKilled`
- Restarts correlate with load or with time-since-start

If events show `Evicted` and node-pressure messages instead of OOMKilled on the
container, the node ran out — different problem; report what you observe.

## Procedure

1. `describe pod` → confirm `Reason: OOMKilled` and note **Restart Count** and the
   container's **Limits: memory** value.
2. Read the restart pattern — it distinguishes the two root causes:
   - Killed at/near startup, or immediately when traffic arrives → **limit too low**
     for normal operation
   - Killed at roughly regular intervals (hours apart), memory climbing between →
     **leak**; raising the limit only lengthens the interval
3. Compare the limit against sibling services of similar shape — a 32Mi limit next to
   siblings at 256Mi is a smell on its own.
4. `logs previous=true` for the moments before the kill — allocation-heavy operations or
   an unbounded cache often name themselves.

## Verdict shape

ROOT CAUSE: <container> on deployment/<workload> OOMKilled — <limit too low (X) for normal load | leak: killed every ~N hours>
EVIDENCE:
  - describe pod: Reason OOMKilled, Restart Count N, Limits: memory X
  - <the pattern observation>
FIX:
  kubectl -n <ns> set resources deploy/<workload> --limits=memory=<new>   (limit case)
  — or file the leak with the owning team; state which case the evidence supports
