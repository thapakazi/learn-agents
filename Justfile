# srebudo.ai — top-level commands
set shell := ["bash", "-cu"]

default:
    @just --list

# Bring up the entire lab (kind + shop + observability + ollama models) — Ch0
lab-up:
    just -f labs/ch00-dojo/Justfile up

# Tear the lab down
lab-down:
    just -f labs/ch00-dojo/Justfile down

# Verify local tool-calling works end to end
smoke:
    just -f labs/ch00-dojo/Justfile smoke

# Serve the course site locally
site:
    cd site && bun install && bun run dev

# Build the course site (static HTML in site/dist)
site-build:
    cd site && bun install && bun run build

# Run the budo CLI (from Ch1 onward)
budo *ARGS:
    cd budo && python -m budo {{ARGS}}

# Ch1 lab commands: just ch1 <recipe> [args]   (e.g. just ch1 break, just ch1 check 1)
ch1 *ARGS:
    @just -f labs/ch01-naked-loop/Justfile {{ARGS}}

# Ch2 lab commands: just ch2 <recipe> [args]
ch2 *ARGS:
    @just -f labs/ch02-skills/Justfile {{ARGS}}
