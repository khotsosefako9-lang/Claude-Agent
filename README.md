# Claude-Agent


## Web-grounded answers (Perplexity Agent API)

`claude_agent.web_answer` calls the Perplexity Agent API (`POST /v1/agent`, via the
official `perplexityai` SDK) with the `web_search` tool and returns the answer text,
URL citations, search-result sources, and a response id for follow-ups.

### Setup

```bash
python -m venv .venv && .venv/bin/pip install -e '.[dev]'
export PERPLEXITY_API_KEY=...   # create one at https://console.perplexity.ai
# optional: export PERPLEXITY_PRESET=medium   (default: low)
```

### Usage

```bash
.venv/bin/claude-agent-ask "What changed in the latest Python release?"
.venv/bin/claude-agent-ask --model openai/gpt-5.6-sol "..."
.venv/bin/claude-agent-ask --continue-from <response id> "And what about 3.13?"
```

```python
from claude_agent.web_answer import ask, ask_structured

answer = ask("Who won the 2026 World Cup?")
print(answer.text, answer.citations)
followup = ask("Who was top scorer?", previous_response_id=answer.response_id)

data, _ = ask_structured(
    "Capital of France?",
    {"type": "object", "properties": {"capital": {"type": "string"}},
     "required": ["capital"], "additionalProperties": False},
)
```

### Checks

```bash
.venv/bin/ruff check src tests && .venv/bin/ruff format --check src tests && .venv/bin/pytest -q
```
