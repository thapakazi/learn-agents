# The skills library — top 10 runbooks for a k8s triage agent

Version-controlled masters for `~/.budo/skills/`. Each file is one failure class (or one
capability) in the Ch2 SKILL.md shape: a one-line `description` the router sees, a body the
model loads on demand via `read_skill(name)`.

Install (all of them):

```bash
mkdir -p ~/.budo/skills && cp labs/ch02-skills/skills/*.md ~/.budo/skills/
rm ~/.budo/skills/README.md   # this file is for humans, not the catalog
```

⚠️ **Spoiler warnings before you copy blindly:**

- `crashloop.md` is a reference solution to **Ch2 level 5** — write your own first, then diff.
- `endpoints-empty.md` covers the exact failure Ch2's **Attack 1** uses as its "no matching
  skill" honesty test. Install it *after* running that attack, and watch the same chaos go
  from "VERDICT: no procedure matched" to a routed diagnosis. That before/after is the whole
  argument for the pattern.

## The ten

| Skill | One-line router description (the discriminator) |
|---|---|
| `service-topology` | Map who-calls-whom from `*_SERVICE_ADDR` env vars — a capability, not a failure class |
| `env-typo` | ONE hostname fails with "no such host" — misspelled service address, symptom hops upstream |
| `crashloop` | CrashLoopBackOff / climbing restarts — classify by exit code before reading logs |
| `imagepullbackoff` | ImagePullBackOff / ErrImagePull — bad tag vs auth vs unreachable registry |
| `oomkilled` | Exit 137 / OOMKilled — limit too low vs real leak, and how to tell |
| `pending-pod` | Pending/FailedScheduling — resources, taints, affinity, unbound PVCs |
| `probe-failure` | Running but 0/1 ready, or healthy apps restarting — probe config vs app health |
| `dns-failure` | MANY names failing to resolve cluster-wide — CoreDNS, not a typo |
| `rollout-stuck` | Deployment not progressing — new ReplicaSet wedged, old pods still serving |
| `endpoints-empty` | Name resolves but connection refused — Service with no ready endpoints |

Notably absent: **wrong-image**. That's a *finding* (`_findings_for_describe`), not a skill —
a one-expression deterministic check belongs in code. If you're tempted to write a skill
whose procedure is one regex, write a finding instead. (Ch2, rule one.)

## Routing design notes

The catalog line is the entire routing surface (~25 tokens per skill, resident in every
call), so descriptions must **partition the symptom space**, not just describe the topic.
The three "connection-ish" classes are deliberately disjoint:

| Symptom | Route |
|---|---|
| `lookup X: no such host`, one name | `env-typo` |
| `no such host`, many different names, several services | `dns-failure` |
| name resolves, `connection refused` / Unavailable | `endpoints-empty` |

Same idea for the "pod won't run" classes: `Pending` (never scheduled) → `pending-pod`;
pulled-then-crashing → `crashloop`; can't even pull → `imagepullbackoff`; running but
unready / restarting-though-healthy → `probe-failure`.

When you add skill #11, ask: which existing description could this symptom be mistaken
for, and does my new description exclude it?
