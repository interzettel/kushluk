"""Pure portfolio comparison tests; no live API or writes."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from tools.portfolio_audit import AuditError, audit_snapshot, collect_snapshot, parse_crosswalk, summary


REPO_ROOT = Path(__file__).resolve().parent.parent
FILES = ("docs/WORK_LEDGER.md", "docs/ISSUE_CROSSWALK.md",
         "docs/progress-manifest.json", "docs/RELEASE_PLAN.md",
         "docs/WORK_JOURNAL.md", "docs/STATUS.md", "pyproject.toml")


class PortfolioAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for item in FILES:
            path = self.root / item
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO_ROOT / item, path)
        owners, _ = parse_crosswalk(
            (self.root / "docs/ISSUE_CROSSWALK.md").read_text()
        )
        gates = json.loads((self.root / "docs/progress-manifest.json").read_text())["gates"]
        numbers = sorted({1, 43, 129} | set(owners.values()) |
                         {n for g in gates for n in g["issues"]})
        self.issues = [{
            "number": n, "state": "closed" if n == 1 else "open",
            "labels": [{"name": "kind:task"}, {"name": "priority:P2"},
                       {"name": "workstream:a"}],
            "assignees": [{"login": "yigit-denktas"}],
        } for n in numbers]
        self.project = [{
            "content": {"url": f"https://github.com/interzettel/kushluk/issues/{n}"},
            "Status": "Done" if n == 1 else "Backlog",
            "Triage Priority": "P2", "Workstream": "A",
            "Maturity": "Idea", "Evidence": "Missing",
        } for n in numbers]
        self.snapshot = {
            "issues": self.issues,
            "releases": [{"tag_name": "v0.2.0-alpha.1", "draft": False,
                          "published_at": "2026-10-18T00:00:00Z"}],
            "project": {"totalCount": len(numbers), "items": self.project},
            "index_body": "## 1. Portfolio map\n" + "".join(
                f"| #{n} | {'CLOSED' if n == 1 else 'OPEN'} | NOW | Test |\n"
                for n in numbers
            ) + "### Non-issues",
        }

    def audit(self):
        return audit_snapshot(self.snapshot, self.root)

    def test_clean_report_never_certifies_any_gate(self):
        result = self.audit()
        self.assertEqual(result["status"], "consistent")
        self.assertEqual(result["counts"]["tasks"], 90)
        self.assertEqual(result["counts"]["crosswalk_mapped"], 90)
        self.assertEqual(result["counts"]["tasks_checked"], 26)
        self.assertEqual(result["counts"]["gates_verified_in_manifest"], 0)
        self.assertFalse(any(result["policy"].values()))
        self.assertIn("observation, not acceptance", summary(result))

    def test_missing_state_and_duplicate_rows(self):
        s = self.snapshot["index_body"].replace(
            "| #43 | OPEN | NOW | Test |\n", ""
        ).replace("| #129 | OPEN", "| #129 | CLOSED")
        self.snapshot["index_body"] = s.replace(
            "### Non-issues", "| #129 | CLOSED | NOW | Test |\n### Non-issues"
        )
        codes = {x["code"] for x in self.audit()["findings"]}
        self.assertIn("issues_missing_from_index", codes)
        self.assertIn("index_state_outdated", codes)
        self.assertIn("duplicate_index_rows", codes)

    def test_ignore_pull_requests(self):
        self.snapshot["issues"].append({
            "number": 147, "state": "closed", "pull_request": {"url": "PR"}
        })
        self.assertEqual(self.audit()["status"], "consistent")

    def test_project_missing_field_and_membership_are_read_only_findings(self):
        self.snapshot["project"]["items"].pop()
        self.snapshot["project"]["totalCount"] -= 1
        result = self.audit()
        codes = {f["code"] for f in result["findings"]}
        self.assertIn("issues_not_in_project", codes)
        self.assertIn("project_field_missing:Status", codes)
        self.assertIn("project_sync_pending", codes)
        self.assertFalse(result["policy"]["github_writes"])

    def test_truncation_is_incomplete_not_false_clean(self):
        self.snapshot["project"]["totalCount"] += 1
        with self.assertRaisesRegex(AuditError, "truncated"):
            self.audit()

    def test_crosswalk_missing_task(self):
        path = self.root / "docs/ISSUE_CROSSWALK.md"
        path.write_text(path.read_text().replace("| **UX-03** | 1 |",
                                                  "| **UX-99** | 1 |"))
        codes = {f["code"] for f in self.audit()["findings"]}
        self.assertIn("crosswalk_tasks_missing", codes)
        self.assertIn("crosswalk_tasks_unknown", codes)

    def test_mismatched_release_never_advances_gates(self):
        self.snapshot["releases"][0]["tag_name"] = "v8.8.8"
        result = self.audit()
        codes = {f["code"] for f in result["findings"]}
        self.assertIn("latest_release_undocumented:RELEASE_PLAN.md", codes)
        self.assertIn("source_version_ahead_or_mismatched", codes)
        self.assertEqual(result["counts"]["gates_verified_in_manifest"], 0)

    def test_live_reader_invokes_only_reads(self):
        calls = []
        def fake(label, *args):
            calls.append(args)
            if label == "issues":
                return [self.issues]
            if label == "releases":
                return [self.snapshot["releases"]]
            if label == "project":
                return self.snapshot["project"]
            return {"body": self.snapshot["index_body"]}
        with patch("tools.portfolio_audit._read", side_effect=fake):
            self.assertEqual(len(collect_snapshot()["issues"]), len(self.issues))
        self.assertEqual(len(calls), 4)
        for args in calls:
            self.assertIn(args[0], {"api", "project", "issue"})
            self.assertFalse({"edit", "close", "delete", "create", "add"} & set(args))

    def test_comparison_has_no_network(self):
        with patch("subprocess.run", side_effect=AssertionError("external")):
            self.assertEqual(self.audit()["status"], "consistent")


if __name__ == "__main__":
    unittest.main()
