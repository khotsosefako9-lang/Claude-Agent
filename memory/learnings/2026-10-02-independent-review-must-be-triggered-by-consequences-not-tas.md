---
type: learning
title: Independent review must be triggered by consequences, not task tier
project: ai-infra
created: 2026-10-02
updated: 2026-10-02
status: active
tags: [verification, routing, reviewer]
---

## Mistake
In system tests T1/T2 the orchestrator classified research and coding tasks as "medium", did them
itself, and reported/stored results with no independent check. T1 wrote snippet-based facts to
long-term memory unreviewed.

## Cause
The original spec tied review to delegation tier ("complex → critic → reviewer"), so a medium task
could skip review entirely even when its output was persisted or acted on.

## Correction
CLAUDE.md now requires `reviewer` before (a) research-derived facts go to memory, (b) >~30 lines of
code are reported done, (c) numbers the user will act on are handed over. `/remember` gates
semantic facts on reviewer acceptance. Re-tests: T2b reviewer rejected a real overflow bug, then
accepted the fix; T1c ran researcher → reviewer → memory with a correct result; T3b reviewer
reproduced every figure.

## Prevention
Gate verification on consequences (persisted, executed, acted on), not on who produced the work.
Re-run `tests/system` after any change to CLAUDE.md routing rules.
