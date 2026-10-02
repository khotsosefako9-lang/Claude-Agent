#!/usr/bin/env bash
# Read-only environment audit for the Second Brain. Changes nothing.
set -u
echo "== Claude Code: $(claude --version 2>/dev/null || echo 'not found')"
echo "== OS: $(. /etc/os-release 2>/dev/null; echo "${PRETTY_NAME:-$(uname -s)}") ($(uname -m))"
for t in python3 uv node npm git jq; do printf '%-8s %s\n' "$t" "$(command -v $t >/dev/null && $t --version 2>&1 | head -1 || echo MISSING)"; done
echo "== Plugins"; claude plugin list 2>&1 | sed 's/^/  /'
echo "== MCP (local)"; claude mcp list 2>&1 | sed 's/^/  /'
echo "== Project agents"; ls .claude/agents 2>/dev/null | sed 's/^/  /'
echo "== Project skills"; ls .claude/skills 2>/dev/null | sed 's/^/  /'
echo "== Memory"; python3 scripts/mem.py lint 2>&1 | tail -1 | sed 's/^/  /'
echo "== Secret scan"; python3 .claude/hooks/guard.py --scan . 2>&1 | tail -1 | sed 's/^/  /'
