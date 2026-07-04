---
name: imagepullbackoff
description: Pods stuck ImagePullBackOff / ErrImagePull — the image can't be fetched; distinguish bad tag vs registry auth vs unreachable registry
---

## When to use

Load this skill when **any** of these are true:

- `get_pods` shows STATUS `ImagePullBackOff` or `ErrImagePull`
- Events contain `Failed to pull image` or `Back-off pulling image`

Do not load this skill for CrashLoopBackOff — there the image pulled fine and the
container is crashing (that's crashloop).

## Procedure

1. `get_events` (or `describe pod`) → the exact pull error string. It classifies:
   - `manifest unknown` / `not found` → the tag or image name doesn't exist
   - `unauthorized` / `authentication required` → missing or wrong imagePullSecret
   - `i/o timeout` / `no such host` / `connection refused` → registry unreachable from the node
2. `describe deployment <workload>` → the exact `Image:` ref. Compare it against sibling
   deployments' image pattern — a typo'd tag or a wrong registry prefix stands out next
   to nine correct ones.
3. Bad refs almost always arrive in fresh rollouts: `describe deployment` events show a
   recent ScalingReplicaSet — note whether old pods (with the old image) are still
   Running. If yes, users may be fine; say so in the verdict.
4. For auth cases: check whether the deployment references an `imagePullSecrets` entry
   and whether siblings pulling from the same registry name the same secret.

## Verdict shape

ROOT CAUSE: deployment/<workload> references unpullable image <ref> — <bad tag | missing auth | registry unreachable>
EVIDENCE:
  - events: <exact pull error line>
  - describe deployment: Image: <ref> (siblings use <pattern>)
FIX:
  kubectl -n <ns> set image deploy/<workload> <container>=<correct-ref>   (or rollout undo / add pull secret)
