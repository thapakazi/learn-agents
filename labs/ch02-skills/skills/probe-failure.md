---
name: probe-failure
description: Pod Running but 0/1 ready, or a healthy-looking app being restarted — readiness/liveness probes failing or misconfigured; app health vs probe config
---

## When to use

Load this skill when **any** of these are true:

- `get_pods` shows `0/1 Running` (running, never becoming ready)
- Events contain `Unhealthy: Readiness probe failed` or `Liveness probe failed`
- An app whose logs look normal keeps getting restarted

Do not load this skill for CrashLoopBackOff where the container exits on its own
(that's crashloop) — here the *kubelet* is the one killing or quarantining it.

## Procedure

1. `get_events` → the exact probe failure text. It classifies:
   - `connection refused` → probe targets the wrong port, or the app binds late
   - `context deadline exceeded` / timeout → timing too tight (slow startup, load)
   - `exec: ... no such file or directory` → the probe binary isn't in the image —
     strong hint the *wrong image* is running; check the findings block on describe
   - HTTP 500 from the probe endpoint → the app genuinely reports unhealthy — pivot
     to its logs; this skill's job ends there
2. `describe deployment` → the probe spec (port, path, initialDelay, period, timeout)
   and the container's actual listening port (env/args). Compare.
3. Name the blast radius: **readiness** failing = pod removed from Service endpoints —
   traffic blackhole, zero restarts. **Liveness** failing = kubelet restarts a healthy
   app. They look similar in `get_pods` but the fix differs; say which you see.

## Verdict shape

ROOT CAUSE: <readiness|liveness> probe on deployment/<workload> fails: <mismatch, e.g. probes :8080 but app listens :7070>
EVIDENCE:
  - events: <verbatim probe error>
  - describe: probe spec vs actual port/behavior
FIX:
  <patch the probe or fix the app's config — concrete command or change>
