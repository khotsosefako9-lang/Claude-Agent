---
name: retro
description: Controlled self-improvement checklist to run after substantial tasks - detects repeated workflows, failures, workarounds and better procedures, decides what becomes memory or a proposed skill, and reconciles contradictory memory. Proposes structural changes instead of applying them.
allowed-tools: Bash(python3 scripts/mem.py:*) Read Grep Glob
---

# /retro — post-task learning loop

Answer each briefly (internally unless something is found):
1. **Repeated workflow?** Search `memory/procedural/` and `workflows/`. If this is the ≥2nd time we
   did essentially the same multi-step procedure → write/update a `procedural` entry. If ≥3rd time
   and stable → **propose** a skill (name, trigger description, steps) — check `.claude/skills/`,
   plugin skills and synced skills for overlap first. Create it only after the user agrees, using
   the `skill-creator` skill.
2. **Failure?** → `learning` entry (Mistake / Cause / Correction / Prevention).
3. **Workaround or better procedure?** → update the existing `procedural` entry rather than adding one.
4. **Decision made?** → `decision` entry with alternatives and whether it can be revisited.
5. **Should an agent/skill/hook/CLAUDE.md rule change?** → write a proposal (what, why, evidence,
   how to revert) in the report. **Do not apply** structural changes automatically.
6. **Contradictions?** `python3 scripts/mem.py lint` — resolve duplicate/contradiction warnings by
   superseding the outdated entry.

Safe to do automatically: memory entries, procedural notes, doc fixes. Everything else: propose.
Output a short "LEARNED / PROPOSED / NOTHING NEW" line for the final report.
