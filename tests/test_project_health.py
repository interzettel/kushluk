"""Regression tests for the standalone, network-free project health tool."""
from __future__ import annotations

from pathlib import Path
import json
import shutil
from tempfile import TemporaryDirectory
import unittest

from tools.project_health import HealthError, analyze, render, render_svg


REPO = Path(__file__).resolve().parent.parent


class ProjectHealthTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "docs").mkdir()
        for filename in ("WORK_LEDGER.md", "progress-manifest.json"):
            shutil.copyfile(REPO / "docs" / filename, self.root / "docs" / filename)

    def manifest(self):
        return json.loads((self.root / "docs/progress-manifest.json").read_text())

    def store_manifest(self, data):
        (self.root / "docs/progress-manifest.json").write_text(
            json.dumps(data), encoding="utf-8"
        )

    def test_real_repository_all_tasks_mapped(self):
        result = analyze(REPO)
        self.assertEqual(result["task_progress"]["total"], 90)
        self.assertEqual(len(result["task_progress"]["groups"]), 13)
        self.assertEqual(len(result["gates"]), 8)
        self.assertEqual(result["verified_count"], 0)
        self.assertEqual(
            (REPO / "docs/PROGRESS.md").read_text(encoding="utf-8"),
            render(result),
        )
        graphic = render_svg(result)
        self.assertEqual(
            (REPO / "docs/progress.svg").read_text(encoding="utf-8"), graphic
        )
        self.assertIn('#F3EFE4', graphic)
        self.assertIn('role="img"', graphic)
        self.assertIn("AWAITING PROOF", graphic)

    def test_missing_task_is_rejected(self):
        file = self.root / "docs/WORK_LEDGER.md"
        file.write_text(file.read_text().replace("**FMT-01**", "**FMT-99**"),
                        encoding="utf-8")
        with self.assertRaisesRegex(HealthError, "missing"):
            analyze(self.root)

    def test_duplicate_task_is_rejected(self):
        file = self.root / "docs/WORK_LEDGER.md"
        file.write_text(file.read_text() + "\n- [ ] **FMT-01** duplicate\n",
                        encoding="utf-8")
        with self.assertRaisesRegex(HealthError, "duplicated"):
            analyze(self.root)

    def test_new_task_requires_manifest_update(self):
        file = self.root / "docs/WORK_LEDGER.md"
        file.write_text(file.read_text() + "\n- [ ] **FMT-11** new\n",
                        encoding="utf-8")
        with self.assertRaisesRegex(HealthError, "unexpected"):
            analyze(self.root)

    def test_verified_gate_requires_evidence(self):
        data = self.manifest()
        data["gates"][0]["status"] = "verified"
        self.store_manifest(data)
        with self.assertRaisesRegex(HealthError, "requires dated evidence"):
            analyze(self.root)

    def test_verified_gate_accepts_dated_evidence(self):
        data = self.manifest()
        data["gates"][0]["status"] = "verified"
        data["gates"][0]["verified_on"] = "2026-10-16"
        data["gates"][0]["evidence"] = [
            "https://github.com/interzettel/kushluk/pull/999"
        ]
        self.store_manifest(data)
        result = analyze(self.root)
        self.assertEqual(result["verified_count"], 1)
        self.assertIn("Proof (2026-10-16)", render(result))

    def test_invalid_or_duplicate_gate_is_rejected(self):
        data = self.manifest()
        data["gates"][1]["id"] = "G1"
        self.store_manifest(data)
        with self.assertRaisesRegex(HealthError, "unique and ordered"):
            analyze(self.root)


if __name__ == "__main__":
    unittest.main()
