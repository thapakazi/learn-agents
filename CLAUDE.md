# CLAUDE.md — authoring & development guide for srebudo.ai

This repo is a hands-on course teaching SREs to build AI agents. It is co-developed
with Claude Code. Read this fully before changing anything.

## What this repo is

- `site/` — Astro Starlight site. ALL course content lives in `site/src/content/docs/` as markdown.
- `labs/chNN-*/` — runnable material per chapter: starter code, chaos manifests, Justfiles, solutions.
- `budo/` — ONE evolving Python CLI. Every chapter adds a subcommand/skill. By Ch9 it is an
  interactive terminal agent (opencode / Claude Code style). Never fork it per chapter; it evolves
  in place. Chapter starters in `labs/` may contain snapshots, but `budo/` is the living tree.

## The voice of Budo

Budo is an old, wise SRE — calm, blunt, slightly amused. Has seen every outage twice.
Each chapter opens with a short koan/anecdote from Budo (3–5 lines, never cheesy walls of text)
and may drop one-line "Budo says:" asides at hard-won lessons. Use sparingly: max 3 asides per chapter.
Never let the persona dilute technical precision.

## Chapter template (follow exactly)

Each chapter = one directory `site/src/content/docs/chNN-slug.md` (or a folder with index + sub-pages
if > ~600 lines) plus `labs/chNN-slug/`:

1. **Koan** — Budo's opening.
2. **The problem** — the real-world SRE pain, stated concretely. Real failure classes only.
3. **What you'll build** — the agent, and which `budo` subcommand it becomes.
4. **Concepts (20%)** — only the theory needed for THIS build. Link out, don't lecture.
5. **Build (70%)** — numbered, runnable steps. Every code block must actually run. Reference files
   in `labs/chNN-*/starter/`. The learner types/edits code; do not hand them a finished blob.
6. **Break it (10%)** — a concrete attack on the agent they just built (context overflow,
   hallucinated tool args, prompt injection in logs, etc.).
7. **Harden it** — fix the break. This is where the real lesson lives.
8. **Belt test** — acceptance criteria checklist + one unprompted challenge scenario.
9. **What production would additionally need** — honest gap list.

## Technical conventions

- Python 3.11+, `uv` optional. Type hints everywhere. No LangChain anywhere, ever.
- Ch1–4: raw loop. Only `httpx`/`openai` client pointed at Ollama (`OPENAI_BASE_URL=http://localhost:11434/v1`).
  Same code must run against Anthropic/OpenAI by swapping env vars — never hardcode a provider.
- Ch5+: migrate to Claude Agent SDK. Keep the raw loop in `budo/core/loop.py` for local-model mode;
  the SDK path and the raw path share the same tool definitions (`budo/tools/`).
- Models: default `qwen2.5:14b` (tool calling), fallback `llama3.1:8b`. Document VRAM expectations.
- Justfile per lab dir. NEVER Makefiles.
- All mutating tools must be gated: dry-run by default, `--yes` / human approval to apply. This rule
  is introduced in Ch1 and never relaxed.
- Secrets via env only. Read-only IAM examples in Ch7/Ch8 must be genuinely least-privilege.

## Site conventions

- Astro Starlight. Sidebar order = belt order. Don't add heavy components; content is king.
- Custom theme lives in `site/src/styles/custom.css` (ink/paper dojo palette). Don't fight Starlight.
- Diagrams: mermaid in markdown where useful.

## Current status

- [x] Ch0 — The Dojo: complete (content + lab)
- [x] Ch1 — The Naked Loop: complete (content + starter)
- [ ] Ch2–Ch9: outlined in site (`status: outline` in frontmatter). Author them one at a time,
      following the template above. When authoring a chapter: write the lab code FIRST, run it,
      then write the prose around what actually ran.

## Definition of done for a chapter

- `just -f labs/chNN-*/Justfile demo` runs the happy path end to end on a fresh lab.
- The "break it" attack reproduces.
- The hardened agent passes the belt test checklist.
- `budo` gains its new subcommand with `--help` text.
