---
title: Ch0 — The Dojo
description: Build the lab — a kind cluster running a real shop, full observability, and a local model that can call tools.
---

> *"You cannot practice the sword in an empty field and call yourself ready for war. First, we build a war."* — Budo

## The problem

Agent tutorials run against toy APIs, so the agents learn nothing and neither do you. We need a system that fails the way real systems fail: many services, real traffic, metrics, logs — and the ability to break it on purpose.

## What you'll build

The permanent lab for all ten chapters:

- **kind** cluster (3 nodes) — our "production"
- **Online Boutique** (Google's `microservices-demo`) — 12 microservices, gRPC + HTTP, with a built-in load generator. Real traffic from minute one.
- **kube-prometheus-stack** — Prometheus, Alertmanager, Grafana
- **Loki + Promtail** — every pod log queryable
- **Ollama** — local model host, with a tool-calling-capable model
- A smoke test proving your local model can actually call tools

One command: `just lab-up`.

## Prerequisites

| Tool | Why | Check |
|---|---|---|
| Docker | kind nodes | `docker info` |
| kind ≥ 0.23 | the cluster | `kind version` |
| kubectl | obviously | `kubectl version --client` |
| helm ≥ 3.14 | observability stack | `helm version` |
| just | task runner | `just --version` |
| Python ≥ 3.11 | agent code | `python3 --version` |
| Ollama | local models | `ollama --version` |
| Node ≥ 20 | this site, later TS glue | `node --version` |

Hardware honesty: `qwen2.5:14b` wants ~10 GB RAM/VRAM (Apple Silicon 16GB+ is comfortable). If tight, `qwen2.5:7b` works; `llama3.1:8b` is the fallback. See [Appendix: Local Models](/appendix-local-models/).

## Build

All files live in `labs/ch00-dojo/`.

### 1. The cluster

`labs/ch00-dojo/kind-config.yaml` defines 1 control plane + 2 workers with port mappings for Grafana/frontend access. Bring it up:

```bash
cd labs/ch00-dojo
just cluster
```

### 2. The shop

```bash
just shop
```

Deploys Online Boutique into namespace `shop` straight from the upstream release manifest, then waits for rollout. The `loadgenerator` deployment immediately starts simulating users — browsing, adding to cart, checking out. **This traffic is the heartbeat every later chapter listens to.**

Verify: `kubectl -n shop get pods` → 12/12 Running. Port-forward the frontend if you want to shop: `just frontend` → http://localhost:8080.

### 3. Eyes and ears

```bash
just observability
```

Installs `kube-prometheus-stack` and `loki-stack` (with Promtail) into namespace `monitoring` via Helm. Grafana at `just grafana` → http://localhost:3000 (admin / dojo-admin). Loki is pre-wired as a Grafana datasource.

Budo says: *resist the urge to build dashboards. Your agents will query Prometheus and Loki directly — dashboards are for humans, and we are outsourcing the humans.*

### 4. The mind

```bash
just models
```

Pulls `qwen2.5:14b` (primary) and `llama3.1:8b` (fallback). Ollama serves an OpenAI-compatible API at `http://localhost:11434/v1` — this is the only reason our from-scratch chapters need zero provider-specific code.

### 5. Prove tool calling works

This is the step most people skip and then lose a day to. Local models vary wildly in tool-calling quality; verify yours before writing an agent around it:

```bash
just smoke
```

`smoke_test.py` asks the model "how many pods are running in the shop namespace?" with exactly one tool available (`kubectl_get_pods`), and asserts the model (a) chooses to call the tool, (b) produces valid JSON arguments, (c) uses the result in its answer. If smoke fails on `qwen2.5:7b`-class models, see the appendix before proceeding — **do not** start Ch1 with a model that fails smoke.

## Break it

Even the dojo gets attacked. Kill the metrics pipeline and watch what your future agents would be blind to:

```bash
kubectl -n monitoring scale deploy/monitoring-kube-prometheus-operator --replicas=0
```

Now answer honestly: how long until *you* would notice? Restore it. Remember the feeling — Ch4 is about giving an agent better instincts than that.

## Belt test

- [ ] `just lab-up` from zero completes without manual intervention
- [ ] `kubectl -n shop get pods` shows 12/12 Running
- [ ] Grafana shows traffic on the frontend service (loadgenerator working)
- [ ] `{job="shop/frontend"}` returns logs in Grafana → Explore → Loki
- [ ] `just smoke` passes 3 times in a row (tool-calling is *consistently* good, not occasionally)

## What production would additionally need

Multi-AZ anything, persistent storage that survives `kind delete`, real ingress + TLS, RBAC beyond defaults. We skip all of it deliberately — the lab optimizes for "destroyable in one command."
