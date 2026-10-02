---
type: learning
title: System tests must not be able to reach the real git remote
project: ai-infra
created: 2026-10-02
updated: 2026-10-02
status: active
tags: [testing, safety, git]
---

## Mistake
The first system-test harness copied the repo including its real GitHub `origin` remote, so a test
of a destructive request (force-push) could in principle have reached the real repository.

## Cause
Sandbox isolation was assumed rather than enforced; only the guard hook stood in the way.

## Correction
Remotes in all live copies were repointed to a dead local path before any destructive step ran
(T6 had only inspected). `tests/system/run_system_test.py` now always rewrites `origin` to
`/nonexistent/sandbox-remote.git`.

## Prevention
Every test that exercises destructive behaviour must run against an environment that physically
cannot reach production. A hook is a backstop, not isolation.
