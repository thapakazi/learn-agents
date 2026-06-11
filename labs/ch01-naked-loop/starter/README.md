# Ch1 starter

You write the loop. The skeleton below mirrors `budo/core/loop.py` with the engine removed.
Copy it into `budo/core/loop.py` only if you get truly stuck — typing it is the lesson.

Files you will create/complete (in the live `budo/` tree at repo root):
1. `budo/core/provider.py` — one function: `chat(messages, tools)` against any OpenAI-compatible endpoint
2. `budo/core/loop.py`     — the agent loop (skeleton: `loop_skeleton.py` here)
3. `budo/tools/k8s.py`     — read-only kubectl tools + ONE mutating tool to learn gating
4. `budo/__main__.py`      — wire it into `budo logs "<question>"`

Order matters. Provider first (test it with a plain question), loop second, tools third.
