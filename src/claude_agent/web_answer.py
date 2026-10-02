"""Web-grounded answers via the Perplexity Agent API (POST /v1/agent, alias /v1/responses).

The API key is read by the SDK from the ``PERPLEXITY_API_KEY`` environment variable.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any

from perplexity import Perplexity
from perplexity.types.output_item import MessageOutputItem, SearchResultsOutputItem

DEFAULT_PRESET = "low"


class WebAnswerError(RuntimeError):
    """Raised when the Agent API returns a non-completed response."""


@dataclass(frozen=True)
class Source:
    title: str
    url: str
    snippet: str = ""
    date: str | None = None


@dataclass(frozen=True)
class WebAnswer:
    text: str
    response_id: str
    model: str
    citations: list[str] = field(default_factory=list)
    sources: list[Source] = field(default_factory=list)


def _client(client: Perplexity | None) -> Perplexity:
    if client is not None:
        return client
    if not os.environ.get("PERPLEXITY_API_KEY"):
        raise WebAnswerError(
            "PERPLEXITY_API_KEY is not set. Create a key at https://console.perplexity.ai "
            "and export it in your shell."
        )
    return Perplexity()


def _request_kwargs(
    question: str,
    *,
    model: str | None,
    preset: str | None,
    instructions: str | None,
    previous_response_id: str | None,
) -> dict[str, Any]:
    kwargs: dict[str, Any] = {"input": question, "tools": [{"type": "web_search"}]}
    if model:
        kwargs["model"] = model
    else:
        kwargs["preset"] = preset or os.environ.get("PERPLEXITY_PRESET", DEFAULT_PRESET)
    if instructions:
        kwargs["instructions"] = instructions
    if previous_response_id:
        kwargs["previous_response_id"] = previous_response_id
    return kwargs


def _parse(response: Any) -> WebAnswer:
    if response.status != "completed":
        detail = getattr(response.error, "message", None) if response.error else None
        raise WebAnswerError(f"Agent response status {response.status!r}: {detail or 'no detail'}")

    citations: list[str] = []
    sources: list[Source] = []
    for item in response.output:
        if isinstance(item, SearchResultsOutputItem):
            sources.extend(
                Source(title=r.title, url=r.url, snippet=r.snippet, date=r.date)
                for r in item.results
            )
        elif isinstance(item, MessageOutputItem):
            for part in item.content:
                for ann in part.annotations or []:
                    if ann.url and ann.url not in citations:
                        citations.append(ann.url)

    return WebAnswer(
        text=response.output_text,
        response_id=response.id,
        model=response.model,
        citations=citations,
        sources=sources,
    )


def ask(
    question: str,
    *,
    model: str | None = None,
    preset: str | None = None,
    instructions: str | None = None,
    previous_response_id: str | None = None,
    client: Perplexity | None = None,
) -> WebAnswer:
    """Answer ``question`` using live web search.

    Pass ``model`` (e.g. ``"openai/gpt-5.6-sol"``) to pick a model explicitly; otherwise a
    preset is used (``preset`` arg, ``PERPLEXITY_PRESET`` env var, or ``"low"``).
    Pass ``previous_response_id`` from an earlier answer to continue the conversation.
    """
    kwargs = _request_kwargs(
        question,
        model=model,
        preset=preset,
        instructions=instructions,
        previous_response_id=previous_response_id,
    )
    return _parse(_client(client).responses.create(**kwargs))


def ask_structured(
    question: str,
    schema: dict[str, Any],
    *,
    name: str = "answer",
    model: str | None = None,
    preset: str | None = None,
    client: Perplexity | None = None,
) -> tuple[Any, WebAnswer]:
    """Answer ``question`` with output constrained to a JSON ``schema``; returns (parsed, raw)."""
    kwargs = _request_kwargs(
        question, model=model, preset=preset, instructions=None, previous_response_id=None
    )
    kwargs["response_format"] = {
        "type": "json_schema",
        "json_schema": {"name": name, "schema": schema, "strict": True},
    }
    answer = _parse(_client(client).responses.create(**kwargs))
    try:
        return json.loads(answer.text), answer
    except json.JSONDecodeError as exc:
        raise WebAnswerError("Structured response was not valid JSON") from exc
