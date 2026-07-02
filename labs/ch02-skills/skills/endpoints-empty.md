---
name: endpoints-empty
description: A service NAME resolves fine but connections are refused / Unavailable — the Service has no ready endpoints; zero replicas, selector mismatch, or all pods unready
---

## When to use

Load this skill when **any** of these are true:

- Errors say `connection refused` or gRPC `Unavailable` to a service whose name resolves
  (no `no such host` anywhere)
- A Service exists but `describe service` shows `Endpoints: <none>`

Do not load this skill for lookup/`no such host` failures — those are env-typo or
dns-failure. DNS working + nobody answering is this skill's signature.

## Procedure

1. `get_pods` → do any pods for the target app exist, and are they `1/1` ready?
   Three cases, in order of frequency:
2. **Zero pods** → scaled to zero or deleted. `describe deployment <app>` → `Replicas: 0`?
   Recent `ScalingReplicaSet ... to 0` event? Someone or something (HPA, a bad script,
   a human at 14:07) scaled it down.
3. **Pods exist but 0/1** → readiness is gating them out of the endpoints list — load
   `probe-failure` and continue there.
4. **Pods 1/1 yet still refused** → selector mismatch: `describe service <name>` and
   compare its `Selector:` against the pods' labels (`describe deployment` → Labels).
   `Endpoints: <none>` on the service is the smoking gun.
5. Name which of the three cases the evidence supports — the fixes are entirely
   different.

## Verdict shape

ROOT CAUSE: service/<name> has no ready endpoints — <scaled to 0 | pods unready | selector mismatch>
EVIDENCE:
  - <caller error line: connection refused / Unavailable>
  - get_pods / describe service output for the case
FIX:
  kubectl -n <ns> scale deploy/<app> --replicas=<n>   (scale case — MUTATING, propose it)
  — or the probe fix / selector fix per the case found
