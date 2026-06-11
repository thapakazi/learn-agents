---
title: Ch9 — Black Belt — the budo CLI ⬛
description: One terminal, an orchestrator, your eight specialists. A compound failure. Go.
sidebar:
  badge: { text: outline, variant: caution }
---

> *On the day of the test, Budo unplugged the network cable to the cloud. "Your team," he said, "is already in the room."*

**Status: outline. Lab scaffolding in `labs/ch09-capstone/`.**

## What you'll build

`budo` v1.0 — an interactive terminal agent in the spirit of opencode and Claude Code:

- **TUI** (Textual): streaming agent reasoning, live tool-call panes, approval prompts inline, audit trail viewer
- **Orchestrator + specialists**: Ch1–8 agents become subagents (Claude Agent SDK subagents on the SDK path; your own dispatch on the local path). The orchestrator routes, parallelizes independent investigations, synthesizes one verdict
- **Fully local mode**: the whole team on Ollama. You will feel every architectural decision in latency — and learn which subagent calls are parallelizable for free
- **Skills as files**: each specialist defined declaratively (markdown prompt + tool allow-list + model pick) — your own miniature of the skills pattern the big CLIs use

## The final exam

Three compound scenarios, designed to require multiple specialists, run live:

1. *"Checkout is slow and the AWS bill jumped 30%."* (Ch4 latency chain + Ch7 cost dig — independent, should parallelize)
2. *A deploy went out, p99 doubled, the rollback pipeline itself is failing.* (Ch3 + Ch4 + Ch5, sequential dependencies)
3. *Undisclosed.* Budo applies chaos. The team — and you — find out together.

## Belt test
All three scenarios: correct synthesis, mutations gated, full audit replay, scenario 1 demonstrably parallelized, everything on local models. Then: write the postmortem of your own course — what `budo` still cannot do, and why. That document is your black belt.
