---
title: Ch4 — Observability 🟩
description: The PromQL whisperer — an investigation agent over Prometheus and Loki, grounded by discovery tools.
sidebar:
  badge: { text: outline, variant: caution }
---

> *A student bragged: "My dashboard has 200 panels." Budo asked: "Which one is lying to you right now?" The student is still looking.*

**Status: outline. Lab scaffolding in `labs/ch04-observability/`.**

## The problem
"p99 on checkout doubled at 14:00, why?" — answering this means writing PromQL, correlating deploy events, restarts, saturation, and downstream latency. The skill is mechanical *given* fluency; the agent has fluency.

## What you'll build
`budo why "<symptom>"` — tools: `promql_query`, `promql_range`, `loki_query`, `list_metrics`, `label_values`, `recent_deploys`. Investigation in, evidence-ranked hypothesis out.

## Key concepts introduced
- **Grounding via discovery**: the single biggest local-model failure here is hallucinated metric names. Fix is architectural, not prompt-level: `list_metrics`/`label_values` tools + a system prompt that mandates discovery-before-query.
- Time-window discipline: agents that query `[7d]` by reflex blow context and Prometheus alike.
- Correlation method as prompt: USE/RED encoded as the investigation procedure.

## The scenario
chaos-mesh (or toxiproxy) injects 300ms latency into `productcatalogservice` → symptom surfaces as frontend/checkout p99. Agent must walk the dependency chain to the true culprit, not blame the symptom service.

## Break it
Rename a recording rule the agent learned to rely on; watch it hallucinate the old name. Then harden: discovery-first becomes mandatory, queries validated against `list_metrics` *in code* before execution.

## Belt test
3 injected scenarios (downstream latency, memory leak → OOM cascade, deploy regression): culprit service named correctly in ≥2, with PromQL evidence quoted in the verdict.
