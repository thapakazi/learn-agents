---
name: rollout-stuck
description: Deployment not progressing — new ReplicaSet wedged below desired ready count, old pods still serving; ProgressDeadlineExceeded
---

## When to use

Load this skill when **any** of these are true:

- `describe deployment` shows condition `Progressing=False` or `ProgressDeadlineExceeded`
- Two ReplicaSets exist and the newer one isn't reaching ready
- "We deployed a fix but behavior didn't change" — the fix may never have rolled out

## Procedure

1. `describe deployment <workload>` → Conditions, and the Replicas line
   (`desired | updated | total | available | unavailable`). Note both ReplicaSets and
   their ready counts — the story is usually "new RS stuck at 0/N ready".
2. The new RS's **pods** carry the real error. `get_pods`, find the youngest pods for
   this app, and route by *their* symptom — this skill is a dispatcher:
   - `ImagePullBackOff` → load `imagepullbackoff`
   - `CrashLoopBackOff` → load `crashloop`
   - `Pending` → load `pending-pod`
   - `0/1 Running` → load `probe-failure` (a new readiness probe that never passes is
     the classic silent rollout-wedger)
3. Note the rollout strategy (`maxUnavailable`/`maxSurge`) — it explains *why* the fleet
   is frozen mid-state and how much serving capacity remains.
4. Mitigation usually precedes diagnosis in production: `kubectl rollout undo` restores
   the old RS (MUTATING — propose it for approval), then diagnose the new revision calmly.

## Verdict shape

ROOT CAUSE: rollout of deployment/<workload> revision <n> is stuck — new pods <symptom>, root cause per <sub-skill> analysis
EVIDENCE:
  - describe deployment: Conditions / Replicas line
  - <the new pods' failure evidence>
FIX:
  kubectl -n <ns> rollout undo deploy/<workload>   (mitigate)  +  <the sub-skill's fix>  (cure)
