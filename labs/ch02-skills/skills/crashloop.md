---
name: crashloop
description: Pods in CrashLoopBackOff or restart count climbing — the container exits shortly after start; classify by exit code BEFORE reading logs
---

## When to use

Load this skill when **any** of these are true:

- `get_pods` shows STATUS `CrashLoopBackOff`, or a restart-burst finding fired
- A container exits within seconds of starting, repeatedly
- Events show `Back-off restarting failed container`

Do not load this skill for pods that are Running-but-not-ready with **zero** restarts
(that's probe-failure) or stuck Pending (that's pending-pod).

## Procedure

1. `describe pod <pod>` → read the `Last State: Terminated` block: **Exit Code** and
   **Reason**. This classifies the crash before you read a single log line:
   - `137` → SIGKILL: OOM or eviction — hand off to `oomkilled`
   - `2` → Go panic, very often a missing/invalid env var at startup
   - `1` → app threw an exception — the traceback is in the previous logs
   - `0` → clean exit?! Check command/args; something told it to stop
2. `logs` with `previous=true` — the **current** container may have died before logging
   anything; only the previous instance holds the crash output.
3. If the panic/exception names an env var or config key: `describe deployment <workload>`
   and compare its `Env:` block against what the code demanded. Missing-at-startup vars
   are the most common cause of instant crashloops after a config change.
4. Check *when* it started: restarts on a days-old pod = something changed around it;
   restarts on a minutes-old pod = the last rollout broke it (`describe deployment` →
   recent ScalingReplicaSet events).

## Verdict shape

ROOT CAUSE: deployment/<workload> crashes at startup: <reason, e.g. env var X removed — mustMapEnv panics>
EVIDENCE:
  - describe pod: Last State Terminated, Exit Code <n>
  - logs --previous: <the panic/exception line>
  - describe deployment: <the missing/wrong config>
FIX:
  kubectl -n <ns> set env deployment/<workload> <NAME>=<value>   (or rollout undo)
