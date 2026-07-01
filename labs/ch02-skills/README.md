# ch02-skills — Context Engineering: Findings & Skills

Unlike Ch1, this lab ships almost empty **on purpose**. Every chaos in Ch2 is a plain
`kubectl` one-liner documented in the chapter, and everything else — the findings helpers,
the skill loader, the skills themselves, even this lab's Justfile — is built by the learner.

What lands here as you work the chapter:

- `skills/` — your version-controlled masters of `~/.budo/skills/*.md` (`env-typo.md`,
  `crashloop.md`, plus the boss-fight skill you invent). The chapter's Step 5 side quest.
- `Justfile` — the Step 10 side quest: `chaos-wrong-image`, `chaos-env-typo`,
  `chaos-crashloop`, `chaos-mystery`, `heal`, `demo`. Rule of the dojo: chaos you can't
  cleanly revert is chaos you shouldn't inject.

The chaos commands, for reference (inject / heal):

| Scenario | Inject | Heal |
|---|---|---|
| wrong-image | `kubectl -n shop set image deploy/cartservice server=redis:alpine` | `kubectl -n shop rollout undo deploy/cartservice` |
| env-typo | `just -f ../ch01-naked-loop/Justfile break` | `just -f ../ch01-naked-loop/Justfile heal` |
| crashloop | `kubectl -n shop set env deploy/frontend PRODUCT_CATALOG_SERVICE_ADDR-` | `kubectl -n shop set env deploy/frontend PRODUCT_CATALOG_SERVICE_ADDR=productcatalogservice:3550` |
| mystery (no skill) | `kubectl -n shop scale deploy/paymentservice --replicas=0` | `kubectl -n shop scale deploy/paymentservice --replicas=1` |

So a skill is: content organization on disk + advertised in the system prompt + retrieved
by a normal tool call. Nothing new at the model layer.
