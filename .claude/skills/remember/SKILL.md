---
name: remember
description: Save durable knowledge to the Second Brain memory (decisions, facts, procedures, lessons, preferences, significant events) with project tagging, duplicate checks and lint. Use after substantial tasks, when the user says "remember", states a preference, or makes a decision worth keeping.
argument-hint: "[what to remember]"
allowed-tools: Bash(python3 scripts/mem.py:*) Read Edit Write
---

# /remember — selective memory write

Input (optional): $ARGUMENTS

## 1. Decide whether it is worth storing
Store only if it will change future work. **Yes:** decisions + rationale, stable facts with
sources, procedures that worked, mistakes with prevention, explicit user preferences, completed
milestones. **No:** chat transcripts, temporary task state, things derivable from code/git,
unverified claims, secrets/credentials/personal identifiers of third parties.

**Gate for `semantic` facts from research:** the `reviewer` agent must have checked the cited
sources first (ACCEPT / ACCEPT WITH NOTES). Facts that were only seen in search snippets, recalled
from training, or single-sourced are stored only if marked as such in the body (e.g.
"single-source", "unverified: …"), never as plain fact. Volatile facts (versions, prices) get a
"as of YYYY-MM-DD" in the title.

## 2. Classify
| Type | Use for | Required sections |
|---|---|---|
| `decision` | a choice made, with reason & alternatives | Decision, Reason, Alternatives considered (+ `revisitable`) |
| `learning` | a mistake and how to prevent it | Mistake, Cause, Correction, Prevention |
| `semantic` | stable fact / research finding / reference | Fact (+ `--sources url1,url2`) |
| `procedural` | how to do something repeatable | When to use, Steps |
| `episodic` | significant event / completed project | What happened, Outcome |
| `preference` | how the user likes things done | Preference |

Project: the active project slug (`python3 scripts/mem.py projects`) or `global` only if it truly
applies everywhere. Never put project-specific facts in `global`.

## 3. Check for existing knowledge first
`python3 scripts/mem.py search "<key terms>" --project <slug> --all`
- Same topic exists and is still true → **edit that file** (update body + `updated:` date).
- Exists but is now wrong/changed → create the new entry, then
  `python3 scripts/mem.py supersede <old-path> <new-path>`.

## 4. Write
Write the body to a temp file in the scratchpad, then:
`python3 scripts/mem.py new <type> --title "<specific title>" --project <slug> --tags a,b --body-file <file>`
(exit code 3 = near-duplicate found: update the existing entry instead, use `--force` only if it is
genuinely distinct). Titles must be specific: "Use DuckDB for local CSV analysis", not "Database".

Decision body template:
```
## Decision
…
## Reason
…
## Alternatives considered
- … (rejected because …)
## Status
active — revisit when …
```

## 5. Validate
`python3 scripts/mem.py lint && python3 scripts/mem.py index` — fix any ERROR. Report which entries
were written/updated. In the cloud environment, commit memory changes so they persist.
