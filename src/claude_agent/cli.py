"""Command-line entry point: ``python -m claude_agent.cli "your question"``."""

from __future__ import annotations

import argparse
import sys

from perplexity import APIStatusError, AuthenticationError, RateLimitError

from .web_answer import WebAnswerError, ask


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Web-grounded answer via Perplexity Agent API")
    parser.add_argument("question")
    parser.add_argument("--model", help='e.g. "openai/gpt-5.6-sol" (overrides preset)')
    parser.add_argument("--preset", help="preset name (default: $PERPLEXITY_PRESET or 'low')")
    parser.add_argument("--continue-from", dest="previous_response_id", help="prior response id")
    args = parser.parse_args(argv)

    try:
        answer = ask(
            args.question,
            model=args.model,
            preset=args.preset,
            previous_response_id=args.previous_response_id,
        )
    except AuthenticationError:
        print("error: 401 — check PERPLEXITY_API_KEY", file=sys.stderr)
        return 1
    except RateLimitError:
        print("error: 429 — rate limited after SDK retries; try again later", file=sys.stderr)
        return 1
    except APIStatusError as exc:
        print(f"error: HTTP {exc.status_code}", file=sys.stderr)
        return 1
    except WebAnswerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(answer.text)
    links = answer.citations or [s.url for s in answer.sources]
    if links:
        print("\nSources:")
        for i, url in enumerate(links, 1):
            print(f"  [{i}] {url}")
    print(f"\n(response id: {answer.response_id})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
