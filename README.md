# srebudo.ai — The Way of the SRE Agent

> *"A young engineer asks the master: 'Sensei, which framework should I learn?'*
> *Budo replies: 'First, write the loop. The framework is what remains when you understand why you no longer want to write the loop.'"*

**srebudo.ai** is a hands-on dojo for SREs who want to build AI agents that solve real platform problems — IaC review, CI/CD triage, observability investigations, oncall, capacity, cost, and security.

You don't read about agents here. You **build one agent per chapter**, against a **real running system** (a kind cluster running a 12-service shop), and every agent you build becomes a skill of one evolving CLI: **`budo`** — which by the final chapter is a full interactive terminal agent in the spirit of opencode / Claude Code.

## Principles of the dojo

1. **Local-first.** Everything runs on your laptop: kind + Ollama. Cloud (AWS, Anthropic API) is opt-in per chapter.
2. **From scratch first, framework later.** Ch1–4 you write the raw loop. Ch5+ you migrate to the Claude Agent SDK and *feel* what it buys you.
3. **Real failures only.** Every scenario is a failure class you've met on call: DNS netpols, flaky tests, noisy neighbors, IAM drift, runaway bills.
4. **Break it, then harden it.** Every chapter ends by attacking your own agent.
5. **One CLI to rule them.** Each chapter ships a new `budo` subcommand. The capstone turns it into a TUI agent team.

## The path

| Belt | Chapter | You build | `budo` gains |
|---|---|---|---|
| — | [Ch0 — The Dojo](site/src/content/docs/ch00-dojo.md) | The lab: kind + shop + metrics + Ollama | `just lab-up` |
| ⬜ White | Ch1 — The Naked Loop | Log-triage agent, zero frameworks | `budo logs` |
| 🟨 Yellow | Ch2 — IaC | Terraform plan reviewer | `budo plan-review` |
| 🟧 Orange | Ch3 — CI/CD | Pipeline failure root-causer | `budo ci` |
| 🟩 Green | Ch4 — Observability | The PromQL whisperer | `budo why` |
| 🟦 Blue | Ch5 — Oncall | Incident copilot (→ Claude Agent SDK) | `budo oncall`, interactive REPL |
| 🟪 Purple | Ch6 — Scale | Capacity planner that opens PRs | `budo capacity` |
| 🟫 Brown | Ch7 — Cost | FinOps agent on AWS | `budo cost` |
| 🟥 Red | Ch8 — Security | Security agent + securing agents | `budo sec`, sandboxed tools |
| ⬛ Black | Ch9 — Capstone | Orchestrated agent team, full TUI | `budo` v1.0 |

## Quick start

```bash
# prerequisites: docker, kind, kubectl, helm, just, python3.11+, ollama, node 20+
just lab-up        # bring up the world (Ch0)
just smoke         # verify local tool-calling works
just site          # serve the course at http://localhost:4321
```

## Repo layout

```
site/        Astro Starlight site — the full course in markdown
labs/        Per-chapter working dirs: starters, chaos manifests, solutions
budo/        The evolving CLI (starts in Ch1, black belt by Ch9)
Justfile     Top-level commands
CLAUDE.md    Instructions for continuing course authoring with Claude Code
```

## Continuing with Claude Code

This repo is designed to be co-developed with Claude Code. `CLAUDE.md` carries the authoring conventions, chapter template, and the voice of Budo. Open the repo in Claude Code and say: *"Author chapter 2 following CLAUDE.md."*
