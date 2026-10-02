#!/usr/bin/env python3
"""Second Brain memory tool. Zero dependencies (stdlib only).

Usage:
  mem.py new TYPE --title T --project P [--tags a,b] [--body TEXT | --body-file F] [--force]
  mem.py search QUERY [--project P] [--type T] [--all] [--limit N]
  mem.py supersede OLD_PATH NEW_PATH
  mem.py index            # regenerate memory/INDEX.md
  mem.py lint             # validate entries, find duplicates/contradictions/secrets
  mem.py brief            # compact session-start summary
  mem.py projects         # list registered projects
  mem.py project-new SLUG --name NAME [--description D]

Entry = one markdown file under memory/<dir>/YYYY-MM-DD-<slug>.md with simple frontmatter
(`key: value` or `key: [a, b]`). See memory/README.md.
"""
import argparse
import datetime as dt
import difflib
import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SECOND_BRAIN_ROOT", Path(__file__).resolve().parent.parent))
MEM = ROOT / "memory"
PROJECTS = ROOT / "projects"
REGISTRY = PROJECTS / "REGISTRY.md"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from secret_patterns import find_secrets  # noqa: E402

TYPES = {  # type -> (directory, required body headings)
    "episodic": ("episodic", ["What happened", "Outcome"]),
    "semantic": ("semantic", ["Fact"]),
    "procedural": ("procedural", ["When to use", "Steps"]),
    "decision": ("decisions", ["Decision", "Reason", "Alternatives considered"]),
    "learning": ("learnings", ["Mistake", "Cause", "Correction", "Prevention"]),
    "preference": ("preferences", ["Preference"]),
}
REQUIRED_FIELDS = ["type", "title", "project", "created", "updated", "status", "tags"]
TYPE_FIELDS = {"decision": ["revisitable"], "semantic": ["sources"]}
STATUSES = {"active", "superseded", "archived"}
DUP_THRESHOLD = 0.82


# ---------------------------------------------------------------- parsing
def parse(path):
    """Return (meta: dict, body: str). Raises ValueError on malformed frontmatter."""
    text = Path(path).read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("missing frontmatter")
    end = text.find("\n---", 4)
    if end == -1:
        raise ValueError("unterminated frontmatter")
    meta = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"bad frontmatter line: {line!r}")
        k, v = line.split(":", 1)
        v = v.strip()
        if v.startswith("[") and v.endswith("]"):
            v = [x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()]
        else:
            v = v.strip("'\"")
        meta[k.strip()] = v
    return meta, text[end + 4:].lstrip("\n")


def dump(meta, body):
    lines = ["---"]
    for k, v in meta.items():
        if isinstance(v, list):
            v = "[" + ", ".join(v) + "]"
        lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines) + "\n\n" + body.rstrip() + "\n"


def entries():
    """Yield (path, meta, body, error) for every memory entry."""
    for _, (d, _) in TYPES.items():
        folder = MEM / d
        if not folder.is_dir():
            continue
        for p in sorted(folder.glob("*.md")):
            try:
                meta, body = parse(p)
                yield p, meta, body, None
            except ValueError as e:
                yield p, {}, "", str(e)


def registered_projects():
    if not REGISTRY.exists():
        return {}
    out = {}
    for line in REGISTRY.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\|\s*`?([a-z0-9][a-z0-9-]*)`?\s*\|\s*([^|]+)\|\s*([^|]+)\|", line)
        if m and m.group(1) not in ("slug",):
            out[m.group(1)] = {"name": m.group(2).strip(), "status": m.group(3).strip()}
    return out


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60] or "entry"


def rel(p):
    return str(Path(p).relative_to(ROOT))


def similar(a, b):
    return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()


def find_duplicates(mtype, project, title):
    hits = []
    for p, meta, _, err in entries():
        if err or meta.get("type") != mtype or meta.get("project") != project:
            continue
        if meta.get("status", "active") != "active":
            continue
        r = similar(title, meta.get("title", ""))
        if r >= DUP_THRESHOLD:
            hits.append((r, p, meta.get("title")))
    return sorted(hits, reverse=True)


# ---------------------------------------------------------------- commands
def cmd_new(a):
    if a.type not in TYPES:
        sys.exit(f"unknown type {a.type!r}; choose from {', '.join(TYPES)}")
    projects = registered_projects()
    if a.project != "global" and a.project not in projects:
        sys.exit(f"unknown project {a.project!r}; register it first (mem.py project-new) "
                 f"or use 'global'. Known: {', '.join(sorted(projects))}")
    body = a.body or ""
    if a.body_file:
        body = Path(a.body_file).read_text(encoding="utf-8")
    secrets = find_secrets(a.title + "\n" + body)
    if secrets:
        sys.exit(f"REFUSED: possible secret in entry ({secrets[0][0]}). Memory must never hold secrets.")
    dups = find_duplicates(a.type, a.project, a.title)
    if dups and not a.force:
        print("POSSIBLE DUPLICATE — update the existing entry instead, or pass --force:")
        for r, p, t in dups:
            print(f"  {r:.2f}  {rel(p)}  ({t})")
        sys.exit(3)
    d, headings = TYPES[a.type]
    if not body.strip():
        body = "\n\n".join(f"## {h}\n" for h in headings)
    today = dt.date.today().isoformat()
    meta = {
        "type": a.type, "title": a.title, "project": a.project,
        "created": today, "updated": today, "status": "active",
        "tags": [t.strip() for t in (a.tags or "").split(",") if t.strip()],
    }
    if a.type == "decision":
        meta["revisitable"] = a.revisitable
    if a.type == "semantic":
        meta["sources"] = [s.strip() for s in (a.sources or "").split(",") if s.strip()]
    folder = MEM / d
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{today}-{slugify(a.title)}.md"
    n = 2
    while path.exists():
        path = folder / f"{today}-{slugify(a.title)}-{n}.md"
        n += 1
    path.write_text(dump(meta, body), encoding="utf-8")
    print(rel(path))


def cmd_search(a):
    terms = [t for t in re.findall(r"\w+", a.query.lower()) if len(t) > 1]
    results = []
    for p, meta, body, err in entries():
        if err:
            continue
        if not a.all and meta.get("status", "active") != "active":
            continue
        if a.type and meta.get("type") != a.type:
            continue
        if a.project and meta.get("project") not in (a.project, "global"):
            continue
        title = meta.get("title", "").lower()
        tags = " ".join(meta.get("tags") or []).lower()
        low = body.lower()
        score = sum(3 * title.count(t) + 2 * tags.count(t) + low.count(t) for t in terms)
        if score or not terms:
            snippet = next((ln.strip() for ln in body.splitlines()
                            if ln.strip() and not ln.startswith("#")
                            and any(t in ln.lower() for t in terms)), "")
            results.append((score, p, meta, snippet[:140]))
    results.sort(key=lambda r: (-r[0], r[1].name))
    if not results:
        print("no matches")
        return
    for score, p, meta, snip in results[: a.limit]:
        print(f"[{meta.get('type')}|{meta.get('project')}|{meta.get('status')}] "
              f"{meta.get('title')}\n    {rel(p)}" + (f"\n    {snip}" if snip else ""))


def cmd_supersede(a):
    old, new = ROOT / a.old, ROOT / a.new
    for p in (old, new):
        if not p.exists():
            sys.exit(f"not found: {p}")
    meta, body = parse(old)
    meta["status"] = "superseded"
    meta["superseded_by"] = rel(new)
    meta["updated"] = dt.date.today().isoformat()
    old.write_text(dump(meta, body), encoding="utf-8")
    print(f"{rel(old)} -> superseded by {rel(new)}")


def cmd_index(a):
    groups = {}
    for p, meta, _, err in entries():
        if err:
            continue
        groups.setdefault(meta.get("project", "?"), []).append((meta, p))
    projects = registered_projects()
    out = ["# Memory Index", "",
           "<!-- Generated by `python3 scripts/mem.py index`. Do not edit by hand. -->", ""]
    order = ["global"] + sorted(k for k in groups if k != "global")
    for proj in order:
        if proj not in groups:
            continue
        name = "Global" if proj == "global" else projects.get(proj, {}).get("name", proj)
        out.append(f"## {name} (`{proj}`)")
        for meta, p in sorted(groups[proj], key=lambda x: (x[0].get("type"), x[1].name)):
            flag = "" if meta.get("status") == "active" else f" _({meta.get('status')})_"
            out.append(f"- **{meta.get('type')}** [{meta.get('title')}]({p.relative_to(MEM)}){flag}")
        out.append("")
    if len(out) == 4:
        out.append("_No memories yet._")
    MEM.mkdir(parents=True, exist_ok=True)
    (MEM / "INDEX.md").write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")
    print(f"wrote memory/INDEX.md ({sum(len(v) for v in groups.values())} entries)")


def lint_issues():
    errors, warnings = [], []
    projects = registered_projects()
    seen = []
    paths = set()
    for p, meta, body, err in entries():
        r = rel(p)
        paths.add(r)
        if err:
            errors.append(f"{r}: {err}")
            continue
        for f in REQUIRED_FIELDS + TYPE_FIELDS.get(meta.get("type"), []):
            if f not in meta:
                errors.append(f"{r}: missing field '{f}'")
        t = meta.get("type")
        if t not in TYPES:
            errors.append(f"{r}: unknown type {t!r}")
            continue
        if p.parent.name != TYPES[t][0]:
            errors.append(f"{r}: type {t} belongs in memory/{TYPES[t][0]}/")
        if meta.get("status") not in STATUSES:
            errors.append(f"{r}: status must be one of {sorted(STATUSES)}")
        proj = meta.get("project")
        if proj != "global" and proj not in projects:
            errors.append(f"{r}: project {proj!r} not in projects/REGISTRY.md")
        for h in TYPES[t][1]:
            if not re.search(rf"^##\s+{re.escape(h)}\s*$", body, re.M):
                errors.append(f"{r}: missing section '## {h}'")
        for h in TYPES[t][1]:  # empty required sections
            m = re.search(rf"^##\s+{re.escape(h)}\s*$\n(.*?)(?=^##\s|\Z)", body, re.M | re.S)
            if m and not m.group(1).strip():
                warnings.append(f"{r}: section '## {h}' is empty")
        if t == "semantic" and not meta.get("sources"):
            warnings.append(f"{r}: semantic fact without sources")
        if meta.get("status") == "superseded" and not meta.get("superseded_by"):
            errors.append(f"{r}: superseded without superseded_by")
        for label, _ in find_secrets(Path(p).read_text(encoding="utf-8")):
            errors.append(f"{r}: possible secret ({label})")
        if meta.get("status") == "active":
            for (r2, m2) in seen:
                if m2.get("type") == t and m2.get("project") == proj and \
                        similar(m2.get("title", ""), meta.get("title", "")) >= DUP_THRESHOLD:
                    kind = "possible contradiction" if t == "decision" else "possible duplicate"
                    warnings.append(f"{r}: {kind} of {r2} — merge or supersede one")
            seen.append((r, meta))
    for p, meta, _, err in entries():
        sb = meta.get("superseded_by") if not err else None
        if sb and sb not in paths:
            errors.append(f"{rel(p)}: superseded_by points to missing {sb}")
    return errors, warnings


def cmd_lint(a):
    errors, warnings = lint_issues()
    for w in warnings:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    n = sum(1 for _ in entries())
    print(f"{n} entries, {len(errors)} errors, {len(warnings)} warnings")
    sys.exit(1 if errors else 0)


def cmd_brief(a):
    projects = registered_projects()
    items = [(p, m) for p, m, _, e in entries() if not e and m.get("status") == "active"]
    prefs = [m for _, m in items if m.get("type") == "preference"]
    recent = sorted(items, key=lambda x: x[1].get("updated", ""), reverse=True)[:5]
    print("SECOND BRAIN — session brief")
    print("Projects: " + (", ".join(f"{s} ({v['status']})" for s, v in projects.items()) or "none"))
    print(f"Memory: {len(items)} active entries. Recall: python3 scripts/mem.py search \"<terms>\" --project <slug>")
    if prefs:
        print("User preferences:")
        for m in prefs[:15]:
            print(f"  - {m.get('title')} [{m.get('project')}]")
    if recent:
        print("Recently updated:")
        for p, m in recent:
            print(f"  - [{m.get('type')}|{m.get('project')}] {m.get('title')}")
    errors, _ = lint_issues()
    if errors:
        print(f"WARNING: memory lint has {len(errors)} error(s); run python3 scripts/mem.py lint")


def cmd_projects(a):
    for slug, v in registered_projects().items():
        print(f"{slug:24} {v['status']:10} {v['name']}")


def cmd_project_new(a):
    slug = a.slug
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
        sys.exit("slug must be lowercase letters, digits and hyphens")
    if slug in registered_projects() or (PROJECTS / slug).exists():
        sys.exit(f"project {slug!r} already exists")
    tpl = PROJECTS / "_template"
    shutil.copytree(tpl, PROJECTS / slug)
    claude_md = PROJECTS / slug / "CLAUDE.md"
    claude_md.write_text(claude_md.read_text(encoding="utf-8")
                         .replace("{{NAME}}", a.name).replace("{{SLUG}}", slug)
                         .replace("{{DESCRIPTION}}", a.description or "TODO: describe this project"),
                         encoding="utf-8")
    with REGISTRY.open("a", encoding="utf-8") as f:
        f.write(f"| `{slug}` | {a.name} | active | {a.description or ''} |\n")
    print(f"created projects/{slug}/ and registered it")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    n = sp.add_parser("new")
    n.add_argument("type")
    n.add_argument("--title", required=True)
    n.add_argument("--project", required=True)
    n.add_argument("--tags", default="")
    n.add_argument("--body")
    n.add_argument("--body-file")
    n.add_argument("--sources", default="", help="comma-separated URLs (semantic)")
    n.add_argument("--revisitable", default="true", choices=["true", "false"])
    n.add_argument("--force", action="store_true")
    s = sp.add_parser("search")
    s.add_argument("query")
    s.add_argument("--project")
    s.add_argument("--type")
    s.add_argument("--all", action="store_true", help="include superseded/archived")
    s.add_argument("--limit", type=int, default=10)
    su = sp.add_parser("supersede")
    su.add_argument("old")
    su.add_argument("new")
    sp.add_parser("index")
    sp.add_parser("lint")
    sp.add_parser("brief")
    sp.add_parser("projects")
    pn = sp.add_parser("project-new")
    pn.add_argument("slug")
    pn.add_argument("--name", required=True)
    pn.add_argument("--description", default="")
    a = ap.parse_args(argv)
    {"new": cmd_new, "search": cmd_search, "supersede": cmd_supersede, "index": cmd_index,
     "lint": cmd_lint, "brief": cmd_brief, "projects": cmd_projects,
     "project-new": cmd_project_new}[a.cmd](a)


if __name__ == "__main__":
    main()
