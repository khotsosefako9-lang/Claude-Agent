---
type: semantic
title: wshobson/agents install commands and marketplace plugin count
project: ai-infra
created: 2026-10-02
updated: 2026-10-02
status: active
tags: [claude-code, plugins, wshobson]
sources: [https://raw.githubusercontent.com/wshobson/agents/main/README.md, https://raw.githubusercontent.com/wshobson/agents/main/.claude-plugin/marketplace.json]
---

## Fact

FACT (checked 2026-10-02, main branch via raw.githubusercontent.com; independently re-verified by reviewer): README lines 21-22 install into Claude Code with:
/plugin marketplace add wshobson/agents
/plugin install python-development   (any plugin name works)
Marketplace name is claude-code-workflows (manifest v1.7.1). .claude-plugin/marketplace.json 'plugins' array has 94 unique entries; README also says 94 (92 local + 2 external git-subdir). Manifest metadata.description still says '92 marketplace plugins' (likely local-only count) - use the array length. Count is volatile: recount with jq '.plugins|length'. Commit SHA not recorded (GitHub API was 403 in session).
