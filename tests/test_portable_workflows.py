"""Keep the portable entry points aligned with the native workflow sources."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PortableWorkflows(unittest.TestCase):
    def test_every_native_workflow_has_a_portable_entry(self):
        index = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        routes = dict(re.findall(r"^\| `([\w-]+)` \| [^|]+ \| \[[^\]]+\]\(([^)]+)\) \|$", index, re.M))

        native = {
            path.stem: path.relative_to(ROOT).as_posix()
            for path in (ROOT / ".claude/commands").glob("*.md")
        }
        for path in (ROOT / ".claude/skills").glob("*/SKILL.md"):
            frontmatter = path.read_text(encoding="utf-8").split("---", 2)[1]
            name = re.search(r"^name: ([\w-]+)$", frontmatter, re.M)
            self.assertIsNotNone(name, path)
            native[name.group(1)] = path.relative_to(ROOT).as_posix()

        self.assertEqual(routes, native)
        for name, source in routes.items():
            with self.subTest(workflow=name):
                entry = ROOT / ".agents/skills" / name / "SKILL.md"
                _, metadata, body = entry.read_text(encoding="utf-8").split("---", 2)
                self.assertRegex(metadata, rf"(?m)^name: {name}$")
                self.assertNotIn("allowed-tools:", metadata)
                links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", body)
                self.assertEqual(
                    [(entry.parent / link).resolve() for link in links],
                    [ROOT / "AGENT-RUNTIMES.md", ROOT / source],
                )
                self.assertTrue((ROOT / "AGENT-RUNTIMES.md").is_file())
                self.assertFalse((entry.parent / "cli/package.json").exists())


if __name__ == "__main__":
    unittest.main()
