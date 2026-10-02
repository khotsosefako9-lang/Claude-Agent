---
name: verify
description: Verification checklist and report format for finished work (code, research, data, documents). Use before declaring any significant task complete, or when the user asks "did it actually work / prove it".
---

# /verify — evidence before "done"

1. Restate **what was requested** (from the user's words, not your plan).
2. List **what was actually done** (files, commands, outputs).
3. Collect **evidence** by running things now, not from memory:
   - Code: run tests (`python3 -m unittest discover -s tests -v` or the project's runner), run the
     program on a realistic input, one edge case, one failure case; check `git diff` for stray
     changes and secrets (`python3 .claude/hooks/guard.py --scan <changed paths>`).
   - Research: every key claim has a URL you opened; conflicts noted; dates checked.
   - Data: inputs validated; key numbers reproduced a second way; units stated.
   - Documents: requested structure present; file opens; claims and citations checked.
4. For medium/complex work, hand the output + original requirement to the `reviewer` agent and
   honour a REJECT.
5. Report:
```
REQUESTED: …            DONE: …
EVIDENCE: …
ASSUMPTIONS: …          UNCERTAIN: …          COULD FAIL: …
REMEMBERED: …
```
Never write "should work" or "tests pass" without having run them in this session.
