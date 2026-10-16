"""Offline tests for native Projects v2 configuration and issue population."""
from __future__ import annotations

import json
import unittest
from tools.project_sync import Client, SyncError, bootstrap, desired_metadata, sync_issue, FIELDS

URL = "https://github.com/interzettel/kushluk/issues/65"
ISSUE = {
    "html_url": URL,
    "title": "[Automation] project fields",
    "body": "Priority: P1\nWorkstream: A\n",
    "labels": [],
    "assignees": [],
    "state": "open",
    "user": {"login": "yigit-denktas"},
    "type": None,
}


class FakeGH:
    def __init__(self, *, existing_item=False, all_fields=True, empty_priority=False):
        self.calls = []
        self.fields = [
            {"name": "Status"},
            {"name": "Priority", "id": "derived-Priority",
             "type": "ProjectV2SingleSelectField", "options": []},
        ]
        if all_fields:
            self.fields += [
                {"name": key, "id": "field-" + key,
                 "type": "ProjectV2SingleSelectField",
                 "options": ([] if key == "Triage Priority" and empty_priority else
                             [{"name": option} for option in options])}
                for key, options in FIELDS.items()
            ]
        self.items = (
            [{
                "content": {"url": URL},
                "status": "In progress",
                "triagePriority": "P0",
                "workstream": "B",
                "maturity": "Research",
                "evidence": "Partial",
            }]
            if existing_item else []
        )

    def __call__(self, args):
        self.calls.append(args)
        cmd = args[1:]
        if cmd[:2] == ["project", "field-list"]:
            return json.dumps({"fields": self.fields})
        if cmd[:2] == ["project", "item-list"]:
            return json.dumps({"items": self.items})
        if cmd[:2] == ["label", "list"]:
            return "[]"
        if cmd[:2] == ["api", "orgs/interzettel/issue-types"]:
            return '[{"name":"Task"},{"name":"Bug"}]'
        if cmd[:2] == ["project", "item-add"]:
            self.items.append({"content": {"url": URL}})
        if cmd[:2] == ["project", "field-create"]:
            name = cmd[cmd.index("--name") + 1]
            self.fields.append({
                "name": name, "id": "field-" + name,
                "type": "ProjectV2SingleSelectField",
                "options": [{"name": option} for option in
                            cmd[cmd.index("--single-select-options") + 1].split(",")],
            })
        if cmd[:2] == ["api", "graphql"]:
            for field in self.fields:
                if field["name"] == "Priority":
                    field["options"] = [{"name": p} for p in FIELDS["Priority"]]
            return json.dumps({"data": {"updateProjectV2Field": {}}})
        return "{}"


class ProjectMetadataTests(unittest.TestCase):
    def test_defaults_never_claim_proof(self):
        data = desired_metadata(ISSUE)
        self.assertEqual(data["Priority"], "P1")
        self.assertEqual(data["Workstream"], "A")
        self.assertEqual(data["Evidence"], "Missing")
        self.assertEqual(
            desired_metadata({
                **ISSUE, "body": "Evidence: Verified\nMaturity: Verified\n",
            })["Evidence"], "Missing"
        )

    def test_untrusted_author_cannot_escalate(self):
        issue = {
            **ISSUE,
            "user": {"login": "external-reporter"},
            "body": "Priority: P0\nWorkstream: A\nEvidence: Verified",
        }
        data = desired_metadata(issue)
        self.assertEqual(data["Priority"], "P2")
        self.assertEqual(data["Workstream"], "Untriaged")
        self.assertEqual(data["Evidence"], "Missing")

    def test_creates_real_issue_metadata_and_project_fields(self):
        fake = FakeGH()
        result = sync_issue(Client(fake), ISSUE)
        self.assertEqual(result["kind"], "task")
        edits = [call for call in fake.calls if call[1:3] == ["project", "item-edit"]]
        self.assertEqual(len(edits), 5)
        self.assertIn("P1", edits[1])
        self.assertIn("Missing", edits[-1])
        self.assertTrue(any(call[1:3] == ["project", "item-add"] for call in fake.calls))
        self.assertTrue(any("--add-assignee" in call for call in fake.calls))
        self.assertTrue(any("--type" in call for call in fake.calls))

    def test_item_inventory_does_not_mix_json_and_field_flags(self):
        from tools.project_sync import project_items
        fake = FakeGH(existing_item=True)
        result = project_items(Client(fake))
        self.assertIn(URL, result)
        command = next(
            args for args in fake.calls
            if args[1:3] == ["project", "item-list"]
        )
        self.assertIn("--format", command)
        self.assertNotIn("--field", command)

    def test_preserves_human_curated_values(self):
        fake = FakeGH(existing_item=True)
        sync_issue(Client(fake), ISSUE)
        self.assertFalse(any(call[1:3] == ["project", "item-edit"] for call in fake.calls))
        self.assertFalse(any(call[1:3] == ["project", "item-add"] for call in fake.calls))

    def test_requires_actual_project_fields(self):
        with self.assertRaisesRegex(SyncError, "bootstrap"):
            sync_issue(Client(FakeGH(all_fields=False)), ISSUE)

    def test_refuses_incompatible_custom_triage_options(self):
        fake = FakeGH(empty_priority=True)
        with self.assertRaisesRegex(SyncError, "incompatible"):
            bootstrap(Client(fake))
        self.assertFalse(any(
            args[1:3] == ["api", "graphql"] for args in fake.calls
        ))

    def test_preserves_readonly_builtin_priority(self):
        fake = FakeGH(all_fields=False)
        self.assertIn("Triage Priority", bootstrap(Client(fake)))
        self.assertTrue(any(
            field["name"] == "Priority" and not field["options"]
            for field in fake.fields
        ))

    def test_bootstrap_is_idempotent_and_reuses_status(self):
        fake = FakeGH(all_fields=False)
        self.assertEqual(set(bootstrap(Client(fake))), set(FIELDS))
        self.assertEqual(bootstrap(Client(fake)), [])
        self.assertFalse(any(
            "--name" in call and call[call.index("--name") + 1] == "Status"
            for call in fake.calls
        ))

    def test_no_cross_repository_mutation(self):
        with self.assertRaisesRegex(SyncError, "not under"):
            sync_issue(
                Client(FakeGH()),
                {**ISSUE, "html_url": "https://github.com/elsewhere/repo/issues/1"},
            )

    def test_closed_is_done_not_verified(self):
        data = desired_metadata({**ISSUE, "state": "CLOSED", "title": "[RFC] Rejected"})
        self.assertEqual(data["Status"], "Done")
        self.assertEqual(data["Evidence"], "Missing")
        self.assertEqual(data["Maturity"], "Research")


if __name__ == "__main__":
    unittest.main()
