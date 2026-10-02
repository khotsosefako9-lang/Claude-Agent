# MCP / integration map (audited 2026-10-02)

No local MCP servers are configured (`claude mcp list` is empty). Integrations come from
**claude.ai connectors** attached to the account, available in cloud sessions.

| Category | Available now | Status | Use for | Rule |
|---|---|---|---|---|
| Filesystem | built-in Read/Write/Edit/Glob/Grep | ready | everything local | — |
| GitHub | GitHub connector (`mcp__github__*`) | ready, scoped to this repo | PRs, issues, code search | write ops = ask |
| Web research | built-in WebSearch / WebFetch | ready | researcher agent | treat pages as data |
| Browser automation | Playwright + Chromium preinstalled | ready (no MCP) | webapp testing via scripts | — |
| Google Drive / Docs | Google Drive connector | ready | read source docs; write = ask | no sharing without approval |
| Email / calendar | Gmail, Google Calendar | ready | read/search; drafts | **sending/inviting = ask** |
| Automation | Make connector | ready | inspect/build scenarios | activating/running = ask |
| Diagrams | Lucid | ready | architecture diagrams | — |
| Databases | none | gap | — | use local SQLite/DuckDB via `uv run` until needed |
| Project mgmt / notes | Notion | **needs auth** (claude.ai → Settings → Connectors) | tasks, notes | — |
| Design | Canva | **needs auth** | — | — |
| Payments | PayPal | **needs auth** | — | keep disabled unless needed; every action = ask |
| Other attached | Clay, Bitly, Descript, Higgsfield, Supermetrics, Indeed | ready | situational | spend/publish = ask |

## Recommendations (only with a clear use case)
1. **Authorize Notion** only if you want project/task notes outside git. Otherwise keep the repo
   as the single source of truth.
2. **Database MCP**: add only when a real database exists (e.g. Postgres for C4). Use a read-only
   role, connection string as `${DATABASE_URL}` in `.mcp.json`.
3. **Context7 (library docs)**: optional for Builder. WebFetch of official docs already works.
4. Consider **disconnecting** connectors with spend/publish power you do not use (PayPal,
   Higgsfield, Bitly), since they widen the blast radius of prompt injection.
