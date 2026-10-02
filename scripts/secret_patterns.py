"""Shared secret-detection patterns used by scripts/mem.py and .claude/hooks/guard.py.

Patterns are deliberately specific (low false-positive) rather than exhaustive.
"""
import re

SECRET_PATTERNS = [
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("Anthropic API key", re.compile(r"\bsk-ant-[A-Za-z0-9_\-]{20,}")),
    ("OpenAI-style API key", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9]{32,}")),
    ("GitHub token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36}\b")),
    ("GitHub fine-grained token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{50,}")),
    ("Slack token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("Stripe live key", re.compile(r"\b[sr]k_live_[0-9A-Za-z]{20,}")),
    ("Private key block", re.compile(r"-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----")),
    ("JWT", re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}")),
    ("Credential assignment", re.compile(
        r"(?i)\b(?:password|passwd|secret|api[_-]?key|access[_-]?token|auth[_-]?token)\s*[:=]\s*"
        r"['\"][^'\"\s$<>{}]{12,}['\"]")),
]

# File paths that must never be written or committed.
SENSITIVE_PATH = re.compile(
    r"(?:^|/)(?:\.env(?:\.[^/]*)?|id_(?:rsa|dsa|ecdsa|ed25519)|[^/]*\.pem|[^/]*\.p12|[^/]*\.pfx|"
    r"[^/]*\.key|credentials(?:\.json)?|\.netrc|\.pgpass)$"
)
# Allowed templates that look sensitive by name.
SAFE_PATH = re.compile(r"(?:^|/)\.env\.(?:example|sample|template)$")


def find_secrets(text):
    """Return a list of (label, redacted_match) for secrets found in text."""
    hits = []
    for label, pat in SECRET_PATTERNS:
        for m in pat.finditer(text or ""):
            s = m.group(0)
            hits.append((label, s[:6] + "…" if len(s) > 6 else "…"))
    return hits


def is_sensitive_path(path):
    path = (path or "").replace("\\", "/")
    return bool(SENSITIVE_PATH.search(path)) and not SAFE_PATH.search(path)
