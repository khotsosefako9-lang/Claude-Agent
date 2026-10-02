#!/usr/bin/env python3
"""End-to-end system test: run one prompt through a fresh headless Claude Code session in a
throwaway copy of this repo, and record which agents/skills/tools were actually used.

Usage: run_system_test.py NAME "PROMPT" [--setup "shell cmd run inside the copy first"]
Writes <workdir>/<NAME>.json (summary) and <NAME>.stream.jsonl (raw events).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ALLOWED = ["Bash", "Read", "Write", "Edit", "Glob", "Grep", "WebSearch", "WebFetch",
           "Agent", "Skill", "TaskCreate", "TaskUpdate", "TaskList", "NotebookEdit"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("prompt")
    ap.add_argument("--setup", default="")
    ap.add_argument("--out", default=os.environ.get("SYSTEST_OUT", tempfile.gettempdir()))
    ap.add_argument("--timeout", type=int, default=1500)
    a = ap.parse_args()

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    work = out / f"repo-{a.name}"
    if work.exists():
        shutil.rmtree(work)
    shutil.copytree(REPO, work, ignore=shutil.ignore_patterns("__pycache__"))
    # Sandbox: the copy must never be able to push to the real remote.
    subprocess.run(["git", "remote", "set-url", "origin", "/nonexistent/sandbox-remote.git"],
                   cwd=work, check=True)
    if a.setup:
        subprocess.run(a.setup, shell=True, cwd=work, check=True)
    before = set(p.relative_to(work).as_posix() for p in work.rglob("*")
                 if p.is_file() and ".git" not in p.parts)

    cmd = ["claude", "-p", a.prompt, "--output-format", "stream-json", "--verbose",
           "--permission-mode", "acceptEdits", "--allowedTools", *ALLOWED]
    t0 = time.time()
    stream = out / f"{a.name}.stream.jsonl"
    with stream.open("w") as f:
        proc = subprocess.run(cmd, cwd=work, stdout=f, stderr=subprocess.STDOUT,
                              timeout=a.timeout, env=dict(os.environ, CLAUDE_PROJECT_DIR=str(work)))

    agents, skills, tools, denials, final, cost = [], [], {}, [], "", None
    for line in stream.read_text().splitlines():
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "assistant" and not ev.get("parent_tool_use_id"):
            for c in ev.get("message", {}).get("content", []):
                if c.get("type") == "tool_use":
                    tools[c["name"]] = tools.get(c["name"], 0) + 1
                    if c["name"] in ("Agent", "Task"):
                        agents.append(c["input"].get("subagent_type", "general-purpose"))
                    if c["name"] == "Skill":
                        skills.append(c["input"].get("skill"))
        if ev.get("type") == "result":
            final = ev.get("result", "")
            cost = ev.get("total_cost_usd")
            denials = ev.get("permission_denials", [])
    after = set(p.relative_to(work).as_posix() for p in work.rglob("*")
                if p.is_file() and ".git" not in p.parts)
    summary = {
        "name": a.name, "exit": proc.returncode, "seconds": round(time.time() - t0),
        "cost_usd": cost, "agents": agents, "skills": skills, "top_level_tools": tools,
        "permission_denials": [{"tool": d.get("tool_name"), "input": str(d.get("tool_input"))[:200]}
                               for d in denials],
        "files_created": sorted(after - before), "files_deleted": sorted(before - after),
        "final": final,
    }
    (out / f"{a.name}.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps({k: v for k, v in summary.items() if k != "final"}, indent=2))


if __name__ == "__main__":
    sys.exit(main())
