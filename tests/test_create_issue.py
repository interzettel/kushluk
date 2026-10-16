"""Unit tests for agent issue intake without network or Project writes."""
from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools.create_issue import create


class FakeClient:
    def __init__(self, duplicate=False):
        self.calls = []
        self.duplicate = duplicate

    def json(self, *args):
        self.calls.append(args)
        if args[:2] == ("issue", "list"):
            return [{"title": "[Task] Existing", "url": "https://github.com/interzettel/kushluk/issues/20"}] if self.duplicate else []
        if args[:2] == ("api", "orgs/interzettel/issue-types"):
            return [{"name": "Task"}]
        raise AssertionError(args)

    def run(self, *args):
        self.calls.append(args)
        if args[:2] == ("issue", "create"):
            return "https://github.com/interzettel/kushluk/issues/99\\n"
        raise AssertionError(args)


class CreateIssueTests(unittest.TestCase):
    def test_writes_real_issue_and_project_sync(self):
        fake = FakeClient()
        with tempfile.TemporaryDirectory() as directory:
            body = Path(directory) / "issue.md"
            body.write_text("Acceptance: real test passes", encoding="utf-8")
            with (patch("tools.create_issue.Client", return_value=fake),
                  patch("tools.create_issue.issue_from_cli", return_value={"html_url": "https://github.com/interzettel/kushluk/issues/99"}) as view,
                  patch("tools.create_issue.sync_issue") as sync):
                url = create(["--title", "[Task] New","--body-file", str(body),
                              "--kind", "task", "--priority", "P1",
                              "--workstream", "A", "--parent", "21",
                              "--blocked-by", "45"])
        self.assertTrue(url.endswith("/99"))
        view.assert_called_once_with(fake, "99")
        sync.assert_called_once()
        commands = [x for x in fake.calls if x[:2] == ("issue", "create")]
        self.assertEqual(len(commands), 1)
        cmd = commands[0]
        for item in ("--type", "--parent", "--blocked-by", "--assignee",
                     "kind:task", "priority:P1", "workstream:a"):
            self.assertIn(item, cmd)

    def test_prevents_identical_title(self):
        fake = FakeClient(duplicate=True)
        with tempfile.TemporaryDirectory() as directory:
            body = Path(directory) / "issue.md"
            body.write_text("Some findings", encoding="utf-8")
            with patch("tools.create_issue.Client", return_value=fake):
                with self.assertRaisesRegex(ValueError, "identical title"):
                    create(["--title", "[Task] Existing", "--body-file", str(body),
                            "--kind", "task"])
        self.assertFalse(any(x[:2] == ("issue", "create") for x in fake.calls))


if __name__ == "__main__":
    unittest.main()
