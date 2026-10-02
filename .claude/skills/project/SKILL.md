---
name: project
description: List, switch to, or create a Second Brain project context (e.g. c4, 44-strategy, career, university, trading, personal, ai-infra). Use when the user names a project, starts work in a new area, or asks which projects exist.
argument-hint: "[list | <slug> | new <slug> \"Name\" \"description\"]"
allowed-tools: Bash(python3 scripts/mem.py:*) Read
---

# /project — project discovery and switching

Arguments: $ARGUMENTS

- **No args / `list`**: `python3 scripts/mem.py projects`; show slug, status, name.
- **`<slug>`** (switch): read `projects/<slug>/CLAUDE.md` (its rules now apply), then run
  `python3 scripts/mem.py search "" --project <slug> --limit 15` and summarize the current state,
  open decisions and recent work. From now on tag memory with this slug and do **not** import
  assumptions from other projects.
- **`new <slug> "Name" "description"`**: confirm the slug is not a near-duplicate of an existing
  project, then `python3 scripts/mem.py project-new <slug> --name "Name" --description "…"`.
  Ask the user for the project's goal, key constraints and stakeholders if unknown, and fill in
  `projects/<slug>/CLAUDE.md`. Report what was created.

If the user's request is ambiguous between projects, ask which one rather than guessing.
