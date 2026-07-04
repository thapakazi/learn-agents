---
name: env-typo
description: Errors of the form "lookup <hostname>: no such host" for ONE hostname between services in one cluster — misspelled service address, symptom appears two hops from cause
---

## When to use

Load this skill when **any** of these are true:

- A log line contains `lookup <hostname>: no such host` or `dial tcp: lookup ... no such host`
- A service is failing RPC calls to a sibling service in the same namespace
- DNS resolution works for *some* hostnames but not others

Do not load this skill if the failing hostname looks external (has dots, no namespace
match), or if MANY different hostnames are failing at once (that's dns-failure).

## Procedure

1. Identify the **operation** that's failing from the log line (e.g. "failed to charge
   card" → checkoutservice owns `Charge`, not the service emitting the log).
2. Find the **caller** — the service that initiates that operation. The error often
   surfaces in the *consumer* of the failing call, not the owner. **Walk one hop
   upstream.** (Caller unknown? Load `service-topology` first.)
3. `describe deployment <caller>` and inspect the `Env:` block.
4. Look for hostnames that look *close* to a real service name but aren't
   (`paymetnservce` vs `paymentservice`). Typos in env-var values are the #1 cause.
5. The describe output is usually confirmation enough; the typo'd hostname will not
   match any Service in the namespace.

## Verdict shape

ROOT CAUSE: env var <NAME> on deployment/<workload> is misspelled: <typo> → should be <correct>
EVIDENCE:
  - <log line showing dial-tcp lookup error from the caller>
  - <describe output showing the env var>
FIX:
  kubectl -n <ns> set env deployment/<workload> <NAME>=<correct-value>
