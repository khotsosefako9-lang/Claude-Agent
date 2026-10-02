# Architecture

```
                              YOU
                               │  task (+ project)
                               ▼
        ┌──────────────────────────────────────────────┐
        │  ORCHESTRATOR = main Claude Code session      │  CLAUDE.md
        │  understand → classify (simple/medium/complex)│  SessionStart hook: mem.py brief
        │  → plan → delegate → … → store → report       │  /project /recall /remember /retro /verify
        └───────┬──────────────┬──────────────┬─────────┘
                ▼              ▼              ▼            (parallel when independent)
          researcher        builder        analyst         .claude/agents/*.md
          web, sources      code, APIs,    Python/SQL/     (cannot delegate further:
          FACT/SOURCE/      MCP, automation Excel, stats,  disallowedTools: Agent)
          INFERENCE/        tests what it   CALCULATED vs
          UNCERTAINTY       builds          ASSUMED
                └──────────────┼──────────────┘
                               ▼
                 critic (read-only) — right problem? assumptions? simpler?
                               ▼
                 reviewer (read-only, runs checks) — ACCEPT / REJECT
                 security-reviewer (when secrets/shell/integrations) — PASS / BLOCK
                               ▼
                 MEMORY  memory/<type>/*.md  ← scripts/mem.py (dedupe, supersede, lint, index)
                         projects/<slug>/CLAUDE.md (project context, loads on demand)
                               └──────► recalled at the start of future work
        guard.py (PreToolUse) mechanically gates destructive commands and secret writes.
```

## Design choices
| Choice | Why |
|---|---|
| Orchestrator is the main session, not an agent | You talk to it directly; it holds task state; subagents cannot see the chat. |
| Six specialists, no Memory/Skill-creator *agents* | Memory and skill creation are procedures, not personas → skills (`/remember`, `/recall`, `/retro`, Anthropic `skill-creator`). Fewer agents = better routing. |
| Specialists can't delegate | Prevents delegation sprawl and runaway cost. Only the orchestrator fans out. |
| Critic and reviewer are read-only | They judge; producers fix. A reviewer that can edit tends to "fix and pass". |
| Memory in git, not `~/.claude` | Cloud container is ephemeral; git gives history, diffs, and review of what Claude "learned". |
| One file per memory, typed, project-tagged | Searchable, dedupe-able, supersede-able; isolation by `project:` filter. |
| Project context via nested `CLAUDE.md` | Native Claude Code feature: loads only when working in that folder. |
| Hooks only for hard safety | Instructions are guidance; `guard.py` is enforcement for the few things that must never happen silently. |
| Plugins declared at project scope | Re-installed automatically in every fresh container / clone. |

## Component map
| Role | Implementation | Source |
|---|---|---|
| Orchestrator | `CLAUDE.md` | custom |
| Researcher | `.claude/agents/researcher.md` | custom (evidence format inspired by ECC `research-ops`/`deep-research`) |
| Builder | `.claude/agents/builder.md` + python-* skills + `mcp-builder` skill | custom + wshobson `python-development` + Anthropic `mcp-builder` |
| Analyst | `.claude/agents/analyst.md` + synced `xlsx`, `dataviz` skills; `uv run --with` data stack | custom + Anthropic |
| Critic | `.claude/agents/critic.md`; `llm-council` / devil's-advocate (synced) for big decisions | custom + synced |
| Reviewer | `.claude/agents/reviewer.md`, `/verify`; built-in `/code-review` | custom (ECC `verification-loop` ideas) + built-in |
| Security | `.claude/agents/security-reviewer.md`, `guard.py`, built-in `/security-review` | custom (ECC `safety-guard` ideas) + built-in |
| Memory | `scripts/mem.py`, `memory/`, `/remember`, `/recall`, SessionStart brief | custom |
| Skill creator | `/retro` (detects) → Anthropic `skill-creator` (builds) | custom + Anthropic (synced) |
| Projects | `projects/REGISTRY.md`, `projects/<slug>/CLAUDE.md`, `/project` | custom |

## Directory layout
```
CLAUDE.md                 orchestrator spec (always loaded)
.claude/agents/           6 specialists            (native location)
.claude/skills/           system skills + mcp-builder (native location)
.claude/hooks/guard.py    safety backstop
.claude/settings.json     plugins, hooks, permissions
memory/                   long-term memory (+ generated INDEX.md)
projects/<slug>/          per-project context + working files
workflows/                executable automations (n8n/Make exports, pipelines)
research/                 research reports (evidence)
scripts/                  mem.py, secret_patterns.py, audit_env.sh
config/                   MCP map, .env.example (names only)
docs/                     AUDIT, ARCHITECTURE, OPERATING_MANUAL, TEST_REPORT
tests/                    unit tests + tests/system (end-to-end harness)
```
There is no top-level `/agents` or `/skills`: Claude Code's native locations are
`.claude/agents/` and `.claude/skills/`, and duplicating them would split the source of truth.
