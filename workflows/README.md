# Workflows

Executable automation artefacts: n8n / Make scenario exports (JSON), pipeline scripts, scheduled
jobs. One folder per workflow: `workflows/<project>-<name>/` with `README.md` (purpose, trigger,
inputs/outputs, credentials *by env-var name only*, how to test, how to disable).

Knowledge about *how to do* something belongs in `memory/procedural/`; a workflow repeated ≥3×
and stable becomes a skill (`/retro` proposes, `skill-creator` builds). Any workflow that sends,
publishes, spends or deletes must have a human-approval step and a `security-reviewer` pass.
