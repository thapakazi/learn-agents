---
title: Ch3 — CI/CD 🟧
description: An event-driven agent that root-causes pipeline failures and comments on PRs.
sidebar:
  badge: { text: outline, variant: caution }
---

> *"It works on my machine," said the student. "Then we shall ship your machine," said Budo, inventing containers. The tests were still flaky.*

**Status: outline. Lab scaffolding in `labs/ch03-cicd/`.**

## The problem
Pipeline fails. Someone reruns it. It passes. Forty engineer-minutes evaporate, the flake survives to kill again. Classification — flaky / dependency break / infra / real regression — is exactly the judgment-over-evidence task agents are good at.

## What you'll build
`budo ci <run-url-or-id>` plus a webhook-driven service (TS/Node glue, Python agent core): on workflow failure → pull job logs via GitHub API → diff against last green run (deps lockfile, base SHA, runner image) → classify with evidence → comment on the PR. This is your first **agent-as-a-service**, not agent-as-REPL.

## Key concepts introduced
- Event-driven agents: webhooks, queueing, idempotency (Actions redelivers; your agent must not double-comment)
- Log-diff as a tool: give the model *differences*, not 20k-line logs
- The flaky-test corpus: we seed the shipd repo with the real kinds — port collision, time-dependence, test-order dependence, OOM-on-shared-runner

## Break it
A failure whose log contains a contributor-controlled string (test names are attacker-controlled!) that tries to make the agent approve the PR.

## Belt test
10 historical failures (provided), ≥8 correctly classified; zero duplicate comments under webhook redelivery.
