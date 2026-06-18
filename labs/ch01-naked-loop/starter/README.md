# Ch1 starter — hints

You write the code directly in the live `budo/` tree:

- `budo/budo/core/loop.py` — skeleton with TODOs (`Tool.spec`, `Agent.run`)
- `budo/budo/tools/k8s.py` — `get_pods` is the worked example; the rest are TODOs

Two hint files live in this directory. **Open only when stuck.** Typing it
yourself is the white-belt lesson.

- `loop_hint.py` — full reference for the loop
- `k8s_hint.py`  — full reference for the kubectl tools

Need to test the chapter end-to-end without writing it yourself? `just use-hints`
copies both files into the live tree; `git checkout` resets the skeletons.

When your code runs `just demo` against the broken `shop` namespace cleanly, the
white belt is yours.
