---
name: service-topology
description: Map which service calls which before chasing a cross-service error — derive the call graph from *_SERVICE_ADDR env vars; use when the caller/owner of a failing operation is unclear
---

## When to use

Load this skill when **any** of these are true:

- An error crosses service boundaries and you don't know who calls whom
- You need to "walk one hop upstream" but the upstream is unknown
- A hostname appears in an error and you need to know which deployments reference it

This is a capability skill, not a failure class — it feeds other skills, it doesn't
produce a root cause by itself.

## Procedure

1. The call graph is written down in the cluster already: every deployment's `Env:` block
   lists its downstream dependencies as `*_SERVICE_ADDR`-style values (`host:port`).
   `describe deployment <name>` and record each as an edge: `<name> → <host>`.
2. To find **who calls X**: describe the deployments implicated in the error chain and
   look for `X` in their env *values*. The deployment holding `X_SERVICE_ADDR` is X's caller.
3. The edge of user-facing flows is `frontend` — user symptoms enter there and errors
   bubble back up to it, which is why frontend's logs report failures it doesn't own.
4. Attribute by **operation**: the service whose env var points at the failing host owns
   the call; the service logging the error is usually just the reporter.
5. Hand off: with caller and owner named, load the skill matching the symptom
   (env-typo, endpoints-empty, ...) and continue there.

## Verdict shape

This skill ends in a handoff, not a root cause:

TOPOLOGY: <caller> → <callee> edges you established, each cited to a describe Env: line
SUSPECT: <deployment> — owns the failing operation
NEXT: <the skill or tool call you proceed with>
