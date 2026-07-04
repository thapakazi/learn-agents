---
name: dns-failure
description: MANY different hostnames failing to resolve across several services at once — cluster DNS (CoreDNS) trouble, not a typo in one address
---

## When to use

Load this skill when **any** of these are true:

- Two or more services log `no such host` for **different** hostnames
- Resolution fails for names you can confirm exist as Services
- Error rates jumped across the whole namespace at the same minute

Do NOT load this skill when exactly one hostname is failing — that's env-typo, and it's
the far more common case. Count first.

## Procedure

1. Count distinct failing hostnames: `logs` with `grep='no such host'` on 2–3 different
   services. **One name → stop here, load env-typo instead.** Several names → continue.
2. Check the resolver itself: `get_pods` in `kube-system` — are the `coredns` pods
   Running and ready? Restarting? `describe pod` on one if suspicious (OOMKilled
   CoreDNS is a classic under namespace-wide load).
3. `get_events` in `kube-system` for the same window.
4. Establish timeline: when did the first `no such host` appear, and does it line up
   with a CoreDNS restart or a node event?
5. If CoreDNS looks healthy and only *some* names fail, re-examine: you may be looking
   at several env-typos from one bad config push — check the callers' Env blocks.

## Verdict shape

ROOT CAUSE: cluster DNS failure — <CoreDNS state and why>, affecting <N> hostnames across <services>
EVIDENCE:
  - <failing lookups from ≥2 services, different names>
  - <coredns pod state / events>
FIX:
  <restart/rollback CoreDNS, fix its resources — MUTATING, propose for approval>
