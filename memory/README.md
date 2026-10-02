# Memory

Selective, structured, version-controlled long-term memory. Managed by `scripts/mem.py`
(stdlib only). `INDEX.md` is generated; never edit it by hand.

## Types → folders
| Type | Folder | What | Required sections |
|---|---|---|---|
| episodic | `episodic/` | significant events, completed projects | What happened, Outcome |
| semantic | `semantic/` | stable facts, research findings, references (`sources:` URLs) | Fact |
| procedural | `procedural/` | how-tos, SOPs that worked | When to use, Steps |
| decision | `decisions/` | decision, date, project, reason, alternatives, status, `revisitable` | Decision, Reason, Alternatives considered |
| learning | `learnings/` | mistake → cause → correction → prevention | Mistake, Cause, Correction, Prevention |
| preference | `preferences/` | how the user wants things done | Preference |

Project memory = any entry whose `project:` is a project slug (see `projects/REGISTRY.md`).
Living project context (goals, stakeholders, conventions) is in `projects/<slug>/CLAUDE.md`.

## Entry format
```
---
type: decision
title: Specific, searchable title
project: ai-infra          # slug or global
created: 2026-10-02
updated: 2026-10-02
status: active             # active | superseded | archived
tags: [memory, architecture]
revisitable: true          # decision only
sources: [https://…]       # semantic only
superseded_by: memory/…    # only when status: superseded
---

## Decision
…
```

## Rules
1. **Selective**: store what changes future work; never transcripts, temp state, secrets.
2. **No duplicates**: `mem.py new` refuses near-duplicate titles (exit 3) → update the existing file.
3. **No silent contradictions**: when knowledge changes, `mem.py supersede OLD NEW` (history kept).
4. **Isolation**: search with `--project <slug>` → returns that project + `global` only.
5. **Validate**: `mem.py lint` (fields, sections, registry, duplicates, contradictions, secrets).

## Commands
```
python3 scripts/mem.py search "duckdb csv" --project trading
python3 scripts/mem.py new decision --title "…" --project c4 --tags pricing --body-file /tmp/body.md
python3 scripts/mem.py supersede memory/decisions/OLD.md memory/decisions/NEW.md
python3 scripts/mem.py lint && python3 scripts/mem.py index
python3 scripts/mem.py brief      # what the SessionStart hook prints
```
