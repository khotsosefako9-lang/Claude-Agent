# Config

- Claude Code settings live in their native location: `.claude/settings.json` (committed:
  plugins, hooks, permissions) and `.claude/settings.local.json` (personal, gitignored).
- Project MCP servers, if ever added, go in the native `.mcp.json` at the repo root, with secrets
  referenced as `${ENV_VAR}`, never literals. See `config/MCP.md` for the integration map.
- `.env.example` documents secret *names* only.
