from unittest.mock import MagicMock

import pytest
from perplexity.types.response_create_response import ResponseCreateResponse

from claude_agent.web_answer import WebAnswerError, ask, ask_structured


def _response(text: str, status: str = "completed") -> ResponseCreateResponse:
    return ResponseCreateResponse.model_validate(
        {
            "id": "resp_1",
            "created_at": 0,
            "model": "openai/gpt-5.6-sol",
            "object": "response",
            "status": status,
            "output": [
                {
                    "type": "search_results",
                    "results": [{"id": 1, "title": "Ex", "url": "https://ex.com", "snippet": "s"}],
                },
                {
                    "type": "message",
                    "id": "m1",
                    "role": "assistant",
                    "status": "completed",
                    "content": [
                        {
                            "type": "output_text",
                            "text": text,
                            "annotations": [{"type": "url_citation", "url": "https://ex.com"}],
                        }
                    ],
                },
            ],
        }
    )


def _client(resp: ResponseCreateResponse) -> MagicMock:
    client = MagicMock()
    client.responses.create.return_value = resp
    return client


def test_ask_uses_preset_and_web_search():
    client = _client(_response("Answer"))
    answer = ask("q?", client=client)
    client.responses.create.assert_called_once_with(
        input="q?", tools=[{"type": "web_search"}], preset="low"
    )
    assert answer.text == "Answer"
    assert answer.citations == ["https://ex.com"]
    assert answer.sources[0].title == "Ex"
    assert answer.response_id == "resp_1"


def test_ask_with_model_and_followup():
    client = _client(_response("A"))
    ask("q", model="openai/gpt-5.6-sol", previous_response_id="resp_0", client=client)
    kwargs = client.responses.create.call_args.kwargs
    assert kwargs["model"] == "openai/gpt-5.6-sol"
    assert "preset" not in kwargs
    assert kwargs["previous_response_id"] == "resp_0"


def test_ask_structured_parses_json():
    client = _client(_response('{"capital": "Paris"}'))
    data, _ = ask_structured("capital?", {"type": "object"}, client=client)
    assert data == {"capital": "Paris"}
    fmt = client.responses.create.call_args.kwargs["response_format"]
    assert fmt["type"] == "json_schema"
    assert fmt["json_schema"]["name"] == "answer"


def test_failed_status_raises():
    with pytest.raises(WebAnswerError):
        ask("q", client=_client(_response("", status="failed")))


def test_missing_key_raises(monkeypatch):
    monkeypatch.delenv("PERPLEXITY_API_KEY", raising=False)
    with pytest.raises(WebAnswerError, match="PERPLEXITY_API_KEY"):
        ask("q")
