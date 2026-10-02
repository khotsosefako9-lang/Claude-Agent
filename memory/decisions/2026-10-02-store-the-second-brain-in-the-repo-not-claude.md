---
type: decision
title: Store the Second Brain in the repo, not ~/.claude
project: ai-infra
created: 2026-10-02
updated: 2026-10-02
status: active
tags: [architecture, memory, cloud]
revisitable: true
---

## Decision
The Second Brain lives entirely in this git repository: project-scope `.claude/` (agents, skills,
hooks, settings with plugin declarations) plus committed `memory/` and `projects/`.

## Reason
The Claude Code cloud container is ephemeral: `~/.claude` (user agents/skills/plugins and native
auto-memory at `~/.claude/projects/<p>/memory/`) is rebuilt every session. Docs confirm auto memory
is machine-local and not shared across cloud environments.

## Alternatives considered
- User-scope install (`~/.claude`) — rejected: wiped each cloud session.
- Native auto memory only — rejected: machine-local, unstructured, not project-isolated.
- External memory service (e.g. ECC Memory Vault) — rejected: extra dependency, not needed yet.

## Status
active — revisit if a persistent local machine becomes the primary environment (user-scope
install could then hold cross-repo preferences).
