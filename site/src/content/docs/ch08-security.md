---
title: Ch8 — Security 🟥
description: Both edges of the sword — a security agent for your platform, and security for your agents.
sidebar:
  badge: { text: outline, variant: caution }
---

> *"My agent has cluster-admin," said the student proudly. Budo bowed to the agent: "Then it is YOUR sensei now."*

**Status: outline. Lab scaffolding in `labs/ch08-security/`.**

This chapter has two halves because the red belt cuts both ways.

## Half 1 — the security agent

`budo sec` — three skills against the dojo:
- **Image triage**: trivy scan output (deterministic) → agent prioritizes by *reachability and context* (is the vulnerable pkg in a internet-facing service? is there an exploit path?) — the judgment layer CVE scanners lack
- **RBAC review**: dump bindings → flag escalation paths (wildcard verbs, `pods/exec` on broad subjects, secrets read in default SAs)
- **K8s audit-log anomalies**: enable kind's audit log; agent baselines normal API patterns, then you exfiltrate a secret via an unusual path and see if it's caught

## Half 2 — securing your agents (the reckoning)

Every "break it" since Ch1 was a deposit; this is the withdrawal. Formalized:
- **Prompt injection**: the Ch1 log attack and Ch3 PR attack, systematized. Untrusted-data delimiting, instruction/data separation, and the honest truth about why mitigations ≠ fixes
- **Privilege separation**: the pattern that actually works — quarantined reader (sees untrusted data, has NO tools) + privileged executor (has tools, sees only the reader's structured findings)
- **Tool sandboxing**: kubectl behind a scoped ServiceAccount per agent skill (read-only role for `budo logs`, etc.); subprocess tools in a container jail; egress allow-lists
- **Approval gates as security boundary**: audit of your own gate — can the model talk you into a `y`? (Yes. We measure how.)
- A **threat model worksheet** for every agent you've built: capabilities × data sources × blast radius

## Break it (meta)
Red-team day: 5 injection payloads (provided) against your full `budo` CLI. Score it honestly.

## Belt test
Both seeded escalation paths + the audit-log exfil caught; the privilege-separation refactor applied to `budo logs`; red-team score documented with mitigations for every hit.
