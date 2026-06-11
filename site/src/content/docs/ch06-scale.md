---
title: Ch6 — Scale 🟪
description: A capacity planner that reads a week of metrics and opens PRs with HPA/resource diffs.
sidebar:
  badge: { text: outline, variant: caution }
---

> *"We'll scale when we need to," they said. Budo nodded, and quietly bookmarked the postmortem template.*

**Status: outline. Lab scaffolding in `labs/ch06-scale/`.**

## The problem
Requests/limits set once at service birth, never revisited; HPAs targeting CPU on memory-bound services. Capacity review is quarterly archaeology. Make it a weekly agent run.

## What you'll build
`budo capacity --window 7d` — pulls saturation/utilization history per workload, finds: throttling, OOM-risk, over-provisioning, HPA misconfiguration → emits **YAML diffs** and opens a PR with reasoning in the description. Agent output as reviewable code change — the safest mutation channel there is.

## Key concepts introduced
- Agents that write config: diff-not-file outputs, validation in code (`kubectl apply --dry-run=server`) before proposing
- **Eval harness for recommendations**: replay historical metric windows, score recs against what actually happened (the throttling you induce with the load generator). First taste of agent evals as regression tests.
- Scheduled agents: cron-driven, unattended — what changes when no human watches the run?

## The scenario
Load generator cranked unevenly: `cartservice` starved (throttled), `recommendationservice` 10x over-provisioned, frontend HPA targeting the wrong metric. Three findings hidden in real data.

## Break it
Feed it a window containing a one-off load test. Does it size the fleet for an event that never recurs? Anomaly-vs-trend discrimination is the hardening.

## Belt test
All 3 seeded findings surfaced with correct YAML; dry-run validation passes; the eval harness scores ≥ baseline on 3 replayed windows.
