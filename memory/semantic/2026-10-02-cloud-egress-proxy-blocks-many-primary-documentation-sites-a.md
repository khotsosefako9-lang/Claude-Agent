---
type: semantic
title: Cloud egress proxy blocks many primary documentation sites (as of 2026-10-02)
project: ai-infra
created: 2026-10-02
updated: 2026-10-02
status: active
tags: [environment, network, research]
sources: [observed:systest-t1/t1b/t4-2026-10-02]
---

## Fact
OBSERVED (2026-10-02, this cloud environment's network policy): HTTPS fetches to python.org,
peps.python.org, devguide.python.org, vendor pricing pages and the GitHub REST API returned
403 "organization policy" from the egress proxy; github.com git clones and
raw.githubusercontent.com worked. Research needing blocked primary sources can only use search
snippets → results must be labelled unverified and not stored as fact. Fix: widen the
environment's network policy (claude.ai/code environment settings) or provide the pages manually.
