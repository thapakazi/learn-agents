# ch02-skills — Context Engineering: Findings & Skills

Lab scaffolding — authored when this chapter is built (see CLAUDE.md authoring flow).

What will live here when authored:

- `chaos/` — manifests for the four chaos scenarios (`wrong-image`, `env-typo`, `crashloop`, `netpol`).
- `skills/` — seed `~/.budo/skills/*.md` files (`env-typo.md`, `wrong-image.md`, `crashloop.md`) the
  learner copies into place. A 4th is the belt-test unprompted challenge.
- `starter/` — `findings_hint.py` (the `_findings_for_*` helpers) and `skills_loader_hint.py` (the
  `read_skill` tool + `render_catalog`).
- `Justfile` — `chaos-wrong-image`, `chaos-env-typo`, `chaos-crashloop`, `chaos-netpol`,
  `heal`, `demo`, `use-skills` (copy seed skills into `~/.budo/skills/`).


So a skill is: content organization on disk + advertised in the system prompt + retrieved by a normal tool call. Nothing new at the model layer.
