# Project Registry

Source of truth for project slugs (parsed by `scripts/mem.py`). Add projects with
`python3 scripts/mem.py project-new <slug> --name "Name" --description "…"` or `/project new`.

| slug | name | status | description |
|---|---|---|---|
| `c4` | C4 / Corefourcorp | active | Business: Corefourcorp (C4). Context to be filled in by the user. |
| `44-strategy` | 44 Strategy | active | Business: 44 Strategy. Kept separate from C4 decisions. Context to be filled in by the user. |
| `career` | Career | active | Career planning, applications, CV, professional development. |
| `university` | University | active | Coursework, research and study. Never mix with business information. |
| `trading` | Trading | active | Trading research, journals and strategies. Analysis is informational, not financial advice; assumptions stay inside this project. |
| `personal` | Personal Projects | active | Personal side projects. |
| `ai-infra` | AI / Claude infrastructure | active | This Second Brain system itself: agents, skills, memory, MCP, automation. |
