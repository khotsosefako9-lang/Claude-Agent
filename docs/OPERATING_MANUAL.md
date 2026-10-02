# Second Brain — Operating Manual

## 1. Giving Claude tasks
Just talk normally. Three things make results markedly better:
1. **Name the project**: "Project: trading — …" or run `/project trading` first.
2. **State the outcome, not only the action**: "I need to decide X by Friday" beats "research X".
3. **Say the stakes**: add "deep" or "high stakes" to get the full critic + reviewer chain;
   "quick" to keep it light.

Useful commands:
| Command | What it does |
|---|---|
| `/project` · `/project trading` · `/project new slug "Name" "desc"` | list / switch / create a project |
| `/recall <topic>` | what do we already know/decide about this (project-isolated) |
| `/remember <thing>` | save a decision, fact, procedure, lesson or preference |
| `/verify` | force an evidence-based check of the last piece of work |
| `/retro` | after a big task: what should be learned, what should become a skill |
| `/code-review`, `/security-review` | built-in review of the current diff |
| "use the critic on this" / "council this" | challenge a plan / multi-advisor debate |

## 2. How Claude decides whether to delegate
- **Simple** (a fact, a small edit): answers directly. No agents.
- **Medium** (one domain): does it itself or uses one specialist, then checks.
- **Complex** (multi-domain / high stakes): writes a plan, runs specialists in parallel where
  independent, then critic → reviewer, then synthesizes.
An agent is used only when its separate context or specialist instructions add value.

## 3. How agents communicate
Specialists can't see your chat and can't call each other. The orchestrator writes each one a
self-contained brief and receives a structured report (fixed output formats in each agent file).
Files are the shared medium: `research/`, `projects/<slug>/`, `workflows/`. The orchestrator
passes one agent's output to the next (e.g. builder's paths + evidence → reviewer).

## 4. How memory works
- Stored in `memory/` as one markdown file per item, typed (episodic, semantic, procedural,
  decision, learning, preference) and tagged with a project. See `memory/README.md`.
- Each session starts with a short brief (projects, your preferences, recent memories).
- Before project work Claude searches memory for that project **plus global** only.
- Claude writes memory selectively after substantial work; duplicates are refused, outdated
  entries are superseded (history kept), `mem.py lint` checks everything incl. secrets.
- **You are the editor**: memory is plain markdown in git. Read `memory/INDEX.md`, edit or delete
  files freely, and review memory changes in diffs like code.
- Cloud sessions: memory persists only once committed and pushed.

## 5. How verification works
Every significant answer ends with REQUESTED / DONE / EVIDENCE / ASSUMPTIONS / UNCERTAIN /
COULD FAIL / REMEMBERED. Evidence means things actually run or opened in this session. The
reviewer agent can reject work; Claude must fix it or tell you what remains open.

## 6. How new skills are created
`/retro` notices a workflow done ≥3 times → Claude **proposes** a skill (name, trigger, steps,
overlap check). On your OK it builds it with Anthropic's `skill-creator` into
`.claude/skills/<name>/SKILL.md`. Nothing structural is changed without your approval.

## 7. Adding a project
`/project new acme "Acme Ltd" "Consulting client, retainer"` (or
`python3 scripts/mem.py project-new acme --name "Acme Ltd" --description "…"`), then fill in
`projects/acme/CLAUDE.md`: goals, stakeholders, constraints, sources of truth, conventions.
**The seven starter projects have placeholder context: filling in their `CLAUDE.md` is the
highest-value next step.**

## 8. Extending safely
| To add | Do | Check |
|---|---|---|
| A preference | `/remember` (type preference) | appears in session brief |
| A rule for every session | edit `CLAUDE.md` (keep < 200 lines) | `/context` shows it |
| A specialist | new `.claude/agents/<name>.md`; add it to the table in `CLAUDE.md` | run a system test |
| A plugin | `claude plugin install <p>@<marketplace> --scope project` | `claude plugin details <p>` for token cost; avoid overlap |
| An MCP server | `.mcp.json` with `${ENV_VAR}` secrets | `security-reviewer` first; see `config/MCP.md` |
| A guard rule | edit `.claude/hooks/guard.py` + a case in `tests/test_guard.py` | `python3 -m unittest discover -s tests` |

Health checks: `bash scripts/audit_env.sh` · `python3 -m unittest discover -s tests -v` ·
`python3 tests/system/run_system_test.py <name> "<prompt>"` (end-to-end, in a sandbox copy).
