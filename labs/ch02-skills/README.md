# ch02-skills — Context Engineering: Findings & Skills

Unlike Ch1, this lab ships almost empty **on purpose**. Every chaos in Ch2 is a plain
`kubectl` one-liner documented in the chapter, and everything else — the findings helpers,
the skill loader, the skills themselves, the chaos recipes in this lab's Justfile — is
built by the learner.

What's here:

- `checks/check.py` — the level checkpoints (`just ch2 check 1..4`). All offline: they
  test the learner's findings/loader/router code against canned fixtures, no cluster or
  model needed.
- `Justfile` — ships with `check` and `ask`; the chaos/heal recipes are a chapter side
  quest the learner fills in. Rule of the dojo: chaos you can't cleanly revert is chaos
  you shouldn't inject.
- `skills/` — the reference library: the top-10 SRE runbooks in SKILL.md form, plus a
  README on routing design. **Spoiler warnings apply** — `crashloop.md` is the level-5
  answer key and `endpoints-empty.md` defuses Attack 1's no-skill test; see
  `skills/README.md` before copying wholesale.

The chaos commands, for reference (inject / heal):

| Scenario | Inject | Heal |
|---|---|---|
| wrong-image | `kubectl -n shop set image deploy/cartservice server=redis:alpine` | `kubectl -n shop rollout undo deploy/cartservice` |
| env-typo | `just ch1 break` | `just ch1 heal` |
| crashloop | `kubectl -n shop set env deploy/frontend PRODUCT_CATALOG_SERVICE_ADDR-` | `kubectl -n shop set env deploy/frontend PRODUCT_CATALOG_SERVICE_ADDR=productcatalogservice:3550` |
| mystery (no skill) | `kubectl -n shop scale deploy/paymentservice --replicas=0` | `kubectl -n shop scale deploy/paymentservice --replicas=1` |

So a skill is: content organization on disk + advertised in the system prompt + retrieved
by a normal tool call. Nothing new at the model layer.
