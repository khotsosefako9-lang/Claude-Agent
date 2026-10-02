# Phase 0 — Environment Audit (2026-10-02)

Read-only audit performed before any change. Re-run the checks with `scripts/audit_env.sh`.

## Runtime

| Item | Found |
|---|---|
| Claude Code | 2.1.287 |
| OS | Ubuntu 24.04.4 LTS (Linux 6.18, x86_64), cloud container |
| Shell | bash |
| Python | 3.11.15 (stdlib + PyYAML only; **no pandas/numpy/duckdb/pytest**) |
| uv | 0.8.17 — `uv run --with pandas ...` works (≈4 s cold) |
| Node / npm / pnpm / bun | 22.22.0 / 10.9.4 / 10.28.0 / 1.3.14 |
| Git | 2.43.0, commit signing configured by the platform |
| jq | present; sqlite3 CLI absent (Python `sqlite3` module available) |

## Claude Code configuration found

| Area | State |
|---|---|
| Repository | Empty except a 1-line `README.md` |
| Project `CLAUDE.md` / `.claude/` | None |
| `~/.claude/settings.json` | None (platform `launcher-settings.json` adds a Stop git-check hook) |
| `~/.claude/CLAUDE.md`, agents, commands | None |
| Plugins | None installed |
| Skills | 28 synced from the claude.ai account (incl. Anthropic **skill-creator**, docx/xlsx/pptx/pdf, llm-council, devil's-advocate, research-analyst…) + platform `session-start-hook` |
| MCP (local `claude mcp`) | None |
| MCP (claude.ai connectors) | Gmail, Google Calendar, Google Drive, GitHub, Lucid, Make, Clay, Bitly, Descript, Higgsfield, Supermetrics, Indeed, Claude Docs. **Need auth:** Canva, Notion, PayPal |

## Critical finding: the container is ephemeral

`~/.claude` is rebuilt every session. Anything installed at **user scope** (plugins, agents,
skills, auto-memory at `~/.claude/projects/<p>/memory/`) is lost when the container is reclaimed.

**Consequence for the design:** the entire Second Brain lives *in this repository*:
project-scope `.claude/` (agents, skills, hooks, settings, plugin declarations) and
committed memory files. Plugins are declared in `.claude/settings.json`, so they reinstall
automatically in each new session or on any machine where you clone the repo.

## Candidate repositories inspected (shallow clones, 2026-10-02)

| Repo | Shape | Notes |
|---|---|---|
| `affaan-m/ECC` v2.2.3 | **One monolithic plugin**: 68 agents, 293 skills, 94 commands, hooks | `--profile minimal` installer targets `~/.claude` (wiped here). `deep-research` requires Firecrawl/Exa MCPs (not configured). `unified-memory` requires the external "ECC Memory Vault". `continuous-learning-v2` auto-observes sessions via hooks (uncontrolled self-modification). Every agent carries a ~10-line boilerplate preamble. |
| `anthropics/skills` | 18 skills in 5 bundle plugins | `skill-creator`, docx/xlsx/pptx/pdf already synced to this account. `mcp-builder` (Apache-2.0) not present. Bundles are coarse (`example-skills` = 12 skills, mostly irrelevant). |
| `wshobson/agents` | 92 **granular** plugins (marketplace `claude-code-workflows`) | Selective install is practical. Candidates evaluated: python-development, comprehensive-review, conductor, context-management, business-analytics, quantitative-trading, startup-business-analyst, security-scanning. |

## Docs consulted (current)

- Subagents: https://code.claude.com/docs/en/sub-agents — frontmatter fields, nesting (depth 3; `disallowedTools: Agent` prevents it), `memory:` scopes.
- Memory: https://code.claude.com/docs/en/memory — nested `CLAUDE.md` loads on demand; auto memory is machine-local.
- Skills: https://code.claude.com/docs/en/skills — `.claude/skills/<name>/SKILL.md`, `disable-model-invocation`, `allowed-tools`.
- Hooks: https://code.claude.com/docs/en/hooks — PreToolUse `permissionDecision: ask|deny`.
