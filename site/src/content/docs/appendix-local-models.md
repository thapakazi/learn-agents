---
title: "Appendix: Local Models"
description: Which models actually call tools, VRAM budgets, and Ollama tuning for agents.
---

## Tool-calling tier list (for this course)

| Model | RAM/VRAM | Tool calling | Notes |
|---|---|---|---|
| `qwen2.5:14b` | ~10 GB | ✅ strong | course default; reliable JSON args, follows method prompts |
| `qwen2.5:7b` | ~5 GB | ✅ decent | fine for Ch1–3; struggles with Ch4's discovery discipline |
| `llama3.1:8b` | ~5 GB | 🟡 ok | occasional malformed args — your `parse_tool_args` earns its keep |
| `qwen2.5:32b` | ~20 GB | ✅ excellent | if you have the metal, Ch9 orchestration is much smoother |
| anything not tool-tuned | — | ❌ | if `just smoke` fails 1/3 runs, do not proceed on it |

Re-run `just smoke` whenever you change models. Three consecutive passes or it doesn't count.

## Ollama settings that matter for agents

- **Context window**: Ollama defaults to 4096 — *far* too small for agent loops. Create a course variant:
  ```bash
  cat > /tmp/Modelfile <<'EOF2'
  FROM qwen2.5:14b
  PARAMETER num_ctx 16384
  EOF2
  ollama create qwen2.5:14b-budo -f /tmp/Modelfile
  export BUDO_MODEL=qwen2.5:14b-budo
  ```
- `temperature 0` for everything in this course; agents want determinism, creativity is a liability in an evidence trail.
- Keep-alive: `OLLAMA_KEEP_ALIVE=30m` saves you the model reload between tool turns.

## Switching to cloud

Same code, two env vars:
```bash
export OPENAI_BASE_URL=https://api.openai.com/v1   # or any OpenAI-compatible endpoint
export OPENAI_API_KEY=...
export BUDO_MODEL=gpt-4o-mini                       # or whatever you're paying for
```
From Ch5, the Claude Agent SDK path uses `ANTHROPIC_API_KEY` natively; local mode remains the raw loop.
