---
title: The Way of Budo
description: The principles behind the dojo.
---

> *Budo has carried a pager since pagers were pagers. He does not fear the 3am alert; the 3am alert fears being misdiagnosed in front of him.*

Five principles govern everything in this course. When in doubt, return here.

## 1. Local-first

Everything runs on your laptop: a kind cluster as our production, Ollama as our model host. The same agent code runs against Anthropic or OpenAI by swapping two environment variables — provider lock-in is a choice we refuse in chapter one and never revisit. AWS appears only where the problem genuinely lives there (cost, IAM).

## 2. The loop before the framework

You cannot evaluate a framework for a job you have never done by hand. Chapters 1–4 you write the agent loop yourself: model call, tool dispatch, context management, retries, stop conditions. It is ~150 lines and it will teach you more than any documentation. In chapter 5 you migrate to the Claude Agent SDK — and because you wrote the loop, you will know precisely what the SDK is doing for you and where its edges are.

## 3. Real failures only

Every scenario in this course is a failure class with a postmortem somewhere behind it: a typo'd env var that quietly breaks one call path, a test that is flaky because of a port collision, latency injected two hops downstream of where it surfaces, an instance family nobody remembers resizing. No toy weather-API agents. The lab gives you a 12-service shop with real traffic so failures present the way they present at work: as symptoms, far from causes.

## 4. Break it, then harden it

An agent that has not been attacked is a demo. Every chapter ends by breaking the thing you built — context overflow, hallucinated metric names, prompt injection hiding inside log lines your agent reads — and then hardening it. The fix is the curriculum. The "break it" sections are also where agent *security* lives long before the dedicated security chapter.

## 5. One CLI, evolving

You do not build nine throwaway scripts. You build one tool — `budo` — and each chapter grafts a new skill onto it. White belt: `budo logs` answers "why is checkout failing?" from raw pod logs. Black belt: `budo` opens a terminal UI, routes your question to a team of specialist agents, shows you their reasoning live, and asks permission before touching anything. Like the tools you use daily — opencode, Claude Code — except you will know every line, because you wrote it.

## Rules of the dojo

- **Mutating tools are gated.** Dry-run by default. `--yes` or interactive approval to apply. Introduced in Ch1, never relaxed.
- **The agent shows its work.** Every tool call and result is logged to an audit trail. If you can't replay it, it didn't happen.
- **Code parses, models reason.** Deterministic extraction in code; judgment in the model. An LLM asked to parse JSON is a waste of a perfectly good jq.
- **Budget the tokens.** Local models make this visceral; cloud models make it expensive. Either way you'll count.
