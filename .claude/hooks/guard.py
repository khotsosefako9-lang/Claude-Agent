#!/usr/bin/env python3
"""PreToolUse safety guard (mechanical backstop for the autonomy rules in CLAUDE.md).

- Bash: destructive / irreversible / outward-facing commands -> "ask" (user must approve).
- Write/Edit/MultiEdit/NotebookEdit: writing secret files (.env, keys) or content containing
  secrets -> "deny".
Fails open (exit 0, no decision) on malformed input so it never bricks a session.

CLI: guard.py --scan PATH...   scan files for secrets (used by security-reviewer); exit 1 on hits.
"""
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR", HERE.parent.parent.parent))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(HERE.parent.parent.parent / "scripts"))
from secret_patterns import find_secrets, is_sensitive_path  # noqa: E402

ASK_RULES = [
    (r"\brm\s+(?:-[a-zA-Z]*[rR][a-zA-Z]*|--recursive)\b", "recursive delete"),
    (r"\bgit\s+push\b[^|;&]*(?:\s--force(?:-with-lease)?\b|\s-f\b|\s\+\S)", "force push (rewrites remote history)"),
    (r"\bgit\s+reset\s+--hard\b", "git reset --hard discards work"),
    (r"\bgit\s+clean\s+-[a-zA-Z]*f", "git clean deletes untracked files"),
    (r"\bgit\s+branch\s+-D\b", "force-deleting a branch"),
    (r"\bgit\s+(?:filter-branch|filter-repo)\b", "history rewrite"),
    (r"(?i)\b(?:drop\s+(?:table|database|schema)|truncate\s+table)\b", "destructive SQL"),
    (r"(?i)\bdelete\s+from\s+\w+\s*(?:;|$|\")", "DELETE without WHERE"),
    (r"\bmkfs(?:\.\w+)?\b|\bdd\s+[^|;&]*of=/dev/|\bshred\b", "disk-level destructive command"),
    (r"\bchmod\s+(?:-R\s+)?0?777\b|\bchown\s+-R\s+\S+\s+/(?:\s|$)", "unsafe permission change"),
    (r"\b(?:curl|wget)\b[^|;&]*\|\s*(?:sudo\s+)?(?:ba|z)?sh\b", "piping a remote script into a shell"),
    (r"\bsudo\b", "privileged command"),
    (r"\bterraform\s+(?:apply|destroy)\b|\bkubectl\s+(?:delete|apply)\b|\bhelm\s+(?:uninstall|delete)\b",
     "infrastructure change"),
    (r"\b(?:npm|pnpm|yarn)\s+publish\b|\btwine\s+upload\b|\buv\s+publish\b|\bgh\s+release\s+create\b",
     "publishing a package/release"),
    (r"\bgh\s+repo\s+(?:delete|edit\s+[^|;&]*--visibility)\b", "repository deletion/visibility change"),
    (r"\b(?:vercel\b[^|;&]*--prod|fly\s+deploy|netlify\s+deploy[^|;&]*--prod|firebase\s+deploy)\b",
     "production deploy"),
    (r"\bdocker\s+(?:system|volume)\s+prune\b", "docker prune deletes data"),
    (r"(?:cat|less|more|head|tail|bat|cp|scp|curl\s+[^|;&]*-d\s*@)\s+[^|;&]*(?:\.env\b|id_(?:rsa|ed25519|ecdsa)\b|\.pem\b|\.netrc\b)",
     "reading/sending a secret file"),
]
ASK_RULES = [(re.compile(p), why) for p, why in ASK_RULES]
TMP_ONLY = re.compile(r"^\s*rm\s+-[a-zA-Z]+\s+((?:/tmp/\S+|\$TMPDIR/\S+|/tmp/claude-\S+)\s*)+$")


def decide(event):
    tool = event.get("tool_name", "")
    ti = event.get("tool_input") or {}
    if tool == "Bash":
        cmd = ti.get("command", "")
        if TMP_ONLY.match(cmd):
            return None
        reasons = [why for pat, why in ASK_RULES if pat.search(cmd)]
        if reasons:
            return "ask", "Second Brain guard: " + "; ".join(dict.fromkeys(reasons)) + \
                ". This needs explicit user approval (CLAUDE.md autonomy rules)."
        return None
    if tool in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        path = ti.get("file_path") or ti.get("notebook_path") or ""
        if is_sensitive_path(path):
            return "deny", f"Second Brain guard: refusing to write secret-bearing file {path!r}. " \
                           "Keep secrets in environment variables; document names in config/.env.example."
        text = "\n".join(str(ti.get(k, "")) for k in ("content", "new_string", "new_source"))
        for e in ti.get("edits", []) or []:
            text += "\n" + str(e.get("new_string", ""))
        hits = find_secrets(text)
        if hits:
            return "deny", f"Second Brain guard: content looks like it contains a secret ({hits[0][0]}). " \
                           "Use an environment variable reference instead."
    return None


def scan(paths):
    found = 0
    for root in paths:
        for p in ([Path(root)] if Path(root).is_file() else Path(root).rglob("*")):
            if not p.is_file() or ".git" in p.parts or p.stat().st_size > 2_000_000:
                continue
            try:
                text = p.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            for label, red in find_secrets(text):
                print(f"{p}: {label} ({red})")
                found += 1
            if is_sensitive_path(str(p)):
                print(f"{p}: sensitive file present")
                found += 1
    print(f"{found} finding(s)")
    return 1 if found else 0


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--scan":
        sys.exit(scan(sys.argv[2:] or ["."]))
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)
    result = decide(event)
    if result:
        decision, reason = result
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": reason}}))
    sys.exit(0)


if __name__ == "__main__":
    main()
