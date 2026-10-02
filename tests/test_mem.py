import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MEM = REPO / "scripts" / "mem.py"


class MemTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        (self.root / "projects").mkdir()
        shutil.copytree(REPO / "projects" / "_template", self.root / "projects" / "_template")
        (self.root / "projects" / "REGISTRY.md").write_text(
            "| slug | name | status | description |\n|---|---|---|---|\n"
            "| `trading` | Trading | active | t |\n| `c4` | C4 | active | c |\n")
        self.env = dict(os.environ, SECOND_BRAIN_ROOT=str(self.root))

    def tearDown(self):
        shutil.rmtree(self.root)

    def run_mem(self, *args, ok=True):
        r = subprocess.run([sys.executable, str(MEM), *args], env=self.env,
                           capture_output=True, text=True)
        if ok is True:
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return r

    def body(self, text):
        p = self.root / "body.md"
        p.write_text(text)
        return str(p)

    def test_new_creates_valid_entry_and_lint_passes(self):
        out = self.run_mem("new", "decision", "--title", "Use DuckDB for CSVs", "--project", "trading",
                           "--body-file", self.body("## Decision\nx\n## Reason\ny\n## Alternatives considered\nz\n"))
        path = self.root / out.stdout.strip()
        self.assertTrue(path.exists())
        self.assertIn("project: trading", path.read_text())
        self.run_mem("lint")

    def test_unknown_project_rejected(self):
        r = self.run_mem("new", "semantic", "--title", "x", "--project", "nope", ok=None)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("unknown project", r.stderr)

    def test_duplicate_detected(self):
        self.run_mem("new", "learning", "--title", "Check units before plotting", "--project", "c4")
        r = self.run_mem("new", "learning", "--title", "Check units before plotting!", "--project", "c4", ok=None)
        self.assertEqual(r.returncode, 3)
        self.assertIn("POSSIBLE DUPLICATE", r.stdout)
        # same title in a different project is not a duplicate (isolation)
        self.run_mem("new", "learning", "--title", "Check units before plotting", "--project", "trading")

    def test_secret_refused(self):
        fake = "sk-ant-" + "a1B2" * 8
        r = self.run_mem("new", "semantic", "--title", "key", "--project", "global",
                         "--body", f"## Fact\nkey={fake}", ok=None)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("secret", r.stderr)

    def test_search_isolation(self):
        self.run_mem("new", "semantic", "--title", "Risk limit is 2 percent", "--project", "trading",
                     "--body", "## Fact\nrisk limit", "--sources", "https://example.com")
        self.run_mem("new", "semantic", "--title", "C4 risk register owner", "--project", "c4",
                     "--body", "## Fact\nrisk owner", "--sources", "https://example.com")
        out = self.run_mem("search", "risk", "--project", "trading").stdout
        self.assertIn("Risk limit", out)
        self.assertNotIn("C4 risk", out)

    def test_supersede_and_lint_missing_sections(self):
        a = self.run_mem("new", "decision", "--title", "Price at 10", "--project", "c4").stdout.strip()
        b = self.run_mem("new", "decision", "--title", "Price at 12 after survey", "--project", "c4").stdout.strip()
        self.run_mem("supersede", a, b)
        self.assertIn("status: superseded", (self.root / a).read_text())
        default = self.run_mem("search", "price", "--project", "c4").stdout
        self.assertNotIn("Price at 10\n", default)
        self.assertIn("Price at 10", self.run_mem("search", "price", "--project", "c4", "--all").stdout)
        bad = self.root / "memory" / "learnings" / "bad.md"
        bad.parent.mkdir(parents=True, exist_ok=True)
        bad.write_text("---\ntype: learning\ntitle: t\nproject: c4\ncreated: x\nupdated: x\n"
                       "status: active\ntags: []\n---\n\n## Mistake\nm\n")
        r = self.run_mem("lint", ok=None)
        self.assertEqual(r.returncode, 1)
        self.assertIn("missing section '## Prevention'", r.stdout)

    def test_project_new_and_index(self):
        self.run_mem("project-new", "uni", "--name", "University", "--description", "study")
        self.assertIn("University", (self.root / "projects" / "uni" / "CLAUDE.md").read_text())
        self.assertIn("uni", self.run_mem("projects").stdout)
        self.run_mem("index")
        self.assertTrue((self.root / "memory" / "INDEX.md").exists())


if __name__ == "__main__":
    unittest.main()
