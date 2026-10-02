---
name: recall
description: Retrieve relevant Second Brain memory (decisions, facts, procedures, lessons, preferences) for the active project before starting work. Use at the start of non-trivial tasks on a known project, or when the user asks "what did we decide/learn about X".
argument-hint: "<topic> [--project slug]"
allowed-tools: Bash(python3 scripts/mem.py:*) Read
---

# /recall — project-scoped memory retrieval

Query: $ARGUMENTS

1. Identify the active project (`python3 scripts/mem.py projects`); if unclear, search `global` +
   ask/assume and say which.
2. `python3 scripts/mem.py search "<terms>" --project <slug>` — returns that project **plus global**
   entries only (isolation). Try 2–3 phrasings/synonyms if results are thin. Add `--type decision`
   etc. to narrow; `--all` to include superseded history.
3. Read the top matches in full. Read `projects/<slug>/CLAUDE.md` for project context.
4. Report concisely: relevant decisions (with status / revisitable), facts (with sources and dates —
   flag anything that may be stale), procedures, lessons. Say explicitly if nothing relevant exists.
5. If two active entries contradict each other, flag it and propose which to supersede.
