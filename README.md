# Claude-Agent — personal Second Brain / Agent OS for Claude Code

Open this repo in Claude Code and it becomes an orchestrator with six specialists
(researcher, builder, analyst, critic, reviewer, security-reviewer), project-isolated memory,
and safety hooks.

- How to use it: [`docs/OPERATING_MANUAL.md`](docs/OPERATING_MANUAL.md)
- How it works: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) · core spec: [`CLAUDE.md`](CLAUDE.md)
- Evidence: [`docs/AUDIT.md`](docs/AUDIT.md) · [`docs/TEST_REPORT.md`](docs/TEST_REPORT.md)
- Health check: `bash scripts/audit_env.sh && python3 -m unittest discover -s tests`
