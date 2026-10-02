---
type: decision
title: Select minimal third-party components (no ECC wholesale install)
project: ai-infra
created: 2026-10-02
updated: 2026-10-02
status: active
tags: [architecture, plugins]
revisitable: true
---

## Decision
Do not install ECC (affaan-m/ECC v2.2.3) or Anthropic bundle plugins wholesale. Install only
wshobson `python-development` (project scope), vendor Anthropic `mcp-builder`, use the account-synced
Anthropic `skill-creator`, and write six focused custom agents plus five small system skills.

## Reason
ECC is a single plugin with 68 agents + 293 skills + hooks; its research/memory/learning skills
depend on Firecrawl/Exa MCPs, the ECC Memory Vault, and session-observing hooks. Installing it
would add heavy routing noise and uncontrolled self-modification. wshobson plugins are granular
(python-development ≈1.6k always-on tokens). Anthropic bundles include many irrelevant skills.

## Alternatives considered
- ECC full plugin — rejected (size, overlap, external deps).
- ECC `--profile minimal` installer — rejected (targets `~/.claude`, wiped in cloud).
- wshobson comprehensive-review / conductor / context-management — rejected (overlap with custom
  reviewer, project registry and memory).
- wshobson quantitative-trading, startup-business-analyst — deferred until Trading / C4 needs are concrete.

## Status
active — revisit when a capability gap is observed in real tasks (record it as a `learning`).
