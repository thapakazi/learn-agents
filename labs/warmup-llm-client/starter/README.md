# Warm-up starter

You write a tiny provider. The skeleton has the two function signatures and TODOs at every
real decision point. Target: ~40 lines of code, two functions, zero magic.

Files you complete:

1. `provider_skeleton.py` — fill in the TODOs in `chat()` and `parse_tool_args()`.

Order:

1. `chat()` first. Run `just test` until you see a sentence from the model.
2. `parse_tool_args()` second. Run `just parse-test` until all three cases pass.
3. (Optional) Drop the finished file into `budo/budo/core/provider.py` and run Ch1 against your code.

Before you write any Python, prove your local Ollama is reachable:

```bash
just curl-test
```

If `curl` gets a response, your endpoint is up. Any failure here is plumbing — fix it before you
touch the Python code.
