---
title: Ch5 — Oncall 🟦
description: The incident copilot — and the migration from your loop to the Claude Agent SDK.
sidebar:
  badge: { text: outline, variant: caution }
---

> *"Sensei, I've automated the runbook!" — "Good. Who approved step four?" — "...step four?" — "The one your agent just ran."*

**Status: outline. Lab scaffolding in `labs/ch05-oncall/`.**

## The problem
A page is a context-assembly problem under stress: what fired, what changed, what does the runbook say, what's safe to try. The copilot does the assembly; the human keeps the judgment.

## What you'll build
Alertmanager webhook → `budo oncall`: parse alert → retrieve matching runbook (your markdown runbooks, RAG-lite: embed + search, no vector-DB ceremony) → gather evidence with Ch4's tools → propose remediation → **human approves** → execute gated kubectl → afterwards, draft the postmortem timeline *from the audit trail* (which you've been writing since Ch1 — this is why).

## The migration
This chapter is where multi-step state, interrupts (human approval mid-graph), retries, and streaming make the raw loop genuinely painful. You migrate to the **Claude Agent SDK**:
- `budo/core/loop.py` survives as **local-model mode** — same tool definitions, two execution paths
- The SDK path gets you: sessions, hooks for the approval gate, subagents (used hard in Ch9)
- You'll write a 1-page "what the SDK replaced" doc mapping each SDK feature to the code you delete. From-scratch-first pays off here, in one afternoon.

Also in this chapter: `budo` gains its first **interactive REPL** (`budo oncall --interactive`) — the seed of the Ch9 TUI.

## Break it
Two alerts fire simultaneously (cascading failure). Does the copilot conflate evidence between incidents? Session/state isolation is the lesson.

## Belt test
A page you didn't script (instructor scenario) handled end-to-end: evidence, proposal, gated fix, postmortem draft with accurate timeline — local model only.
