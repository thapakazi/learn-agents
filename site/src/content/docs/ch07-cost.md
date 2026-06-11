---
title: Ch7 — Cost 🟫
description: The FinOps agent — anomalies, idle hunting, rightsizing with dollar impact, on a least-privilege AWS role.
sidebar:
  badge: { text: outline, variant: caution }
---

> *"The bill went up 30%." — "What changed?" — "Nothing." — Budo smiled. Something always changed.*

**Status: outline. Lab scaffolding in `labs/ch07-cost/`. Requires an AWS account; everything is read-only + tagged-and-destroyable.**

## The problem
Cloud cost questions are investigation problems wearing a spreadsheet costume: *what* jumped, *which* dimension (service/account/usage-type), *what changed* around then, *what's idle*. Cost Explorer answers none of this unattended.

## What you'll build
`budo cost` — tools over Cost Explorer (`GetCostAndUsage`, `GetCostForecast`), EC2/EBS/EIP describe calls, CloudWatch utilization. Capabilities: week-over-week anomaly narration, idle-resource hunt (unattached EBS/EIPs, <5% CPU instances, empty NAT-heavy subnets), rightsizing recs **with dollar impact**, weekly digest (markdown → Slack webhook).

## Key concepts introduced
- **Least-privilege IAM for agents** — the chapter ships a real read-only policy (Cost Explorer + Describe* + CloudWatch read, explicit deny on mutations). You'll assume-role into it; your agent never sees admin creds. This is the pattern, forever.
- The agent's own cost: token budgeting, caching tool results, and when a $0 local model beats a smarter cloud one
- Seeded waste: Terraform in the lab creates deliberately wasteful, tagged resources (oversized gp3, unattached EIP, idle t3.large) so findings are real and `terraform destroy` cleans up

## Break it
Cost allocation tags lie (untagged resources, shared accounts). Does the agent present confident numbers over an unallocated 40%? Hardening: uncertainty must surface in the verdict.

## Belt test
All seeded waste found with correct $/month impact; zero mutating API calls in CloudTrail for the agent's role; digest renders in Slack.
