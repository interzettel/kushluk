"""Durable run-state stages and crash-vs-active process semantics."""
from __future__ import annotations

from datetime import date
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from kushluk import scheduled
from kushluk.config import Settings


DAY = date(2026, 9, 23)


def settings(tmp_path):
    return Settings(archive_dir=tmp_path / "archive", output_dir=tmp_path / "out")


def test_pipeline_stages_are_ordered_and_visible_during_active_run(tmp_path, monkeypatch):
    if scheduled.fcntl is None:
        pytest.skip("POSIX lock detection is Linux/macOS-only")
    cfg = settings(tmp_path)
    observations = []

    def fake_pipeline(*_args, **kwargs):
        for stage in ("sources_complete", "editorial_complete", "rendering",
                      "rendered", "validated", "archive_ready"):
            kwargs["on_stage"](stage)
            snap = scheduled.read_run_status(cfg, target_date=DAY)
            assert snap.status == "in_progress"
            assert snap.stage == stage
            assert snap.stages[-1] == stage
            observations.append(stage)
        return SimpleNamespace(
            failures=[], print_result=None, email_result=None,
            pdf_path=Path("validated-synthetic.pdf"),
        )

    monkeypatch.setattr(scheduled, "run_pipeline", fake_pipeline)
    result = scheduled.run_once(cfg, target_date=DAY)
    assert result.status == "completed"
    assert result.stages == ("started", *observations)
    receipt = cfg.archive_dir / "20260923-001" / "scheduled.json"
    record = json.loads(receipt.read_text())
    assert record["stages"] == list(result.stages)
    assert scheduled.read_run_status(cfg, target_date=DAY).stages == result.stages


def test_unlocked_started_receipt_means_review_not_running_or_safe_to_retry(
    tmp_path, monkeypatch,
):
    cfg = settings(tmp_path)
    folder = cfg.archive_dir / "20260923-001"
    folder.mkdir(parents=True)
    receipt = folder / "scheduled.json"
    receipt.write_text(json.dumps({
        "schema_version": 1,
        "edition_id": "20260923-001",
        "status": "started",
        "stage": "sources_complete",
        "stages": ["started", "sources_complete"],
        "failure_codes": [],
    }))
    monkeypatch.setattr(scheduled, "run_pipeline",
                        lambda *_a, **_kw: pytest.fail("No automatic retry"))
    status = scheduled.read_run_status(cfg, target_date=DAY)
    assert status.status == "needs_review"
    assert status.stage == "sources_complete"
    assert status.stages == ("started", "sources_complete")
    assert scheduled.run_once(cfg, target_date=DAY).status == "needs_review"


def test_submission_unknown_is_not_claimed_printed(tmp_path):
    cfg = settings(tmp_path)
    folder = cfg.archive_dir / "20260923-001"
    folder.mkdir(parents=True)
    (folder / "scheduled.json").write_text(json.dumps({
        "schema_version": 1, "edition_id": "20260923-001",
        "status": "print_submission_unknown", "stage": "print_submission_unknown",
        "stages": ["started", "archive_ready", "print_submission_unknown"],
        "print_submitted": False, "delivery_attempts": ["print"],
        "failure_codes": [],
    }))
    status = scheduled.read_run_status(cfg, target_date=DAY)
    assert status.status == "needs_review"
    assert status.print_submitted is False
    assert status.stage == "print_submission_unknown"


def test_tampered_receipt_stage_or_diagnostics_never_echo_private_text(tmp_path):
    cfg = settings(tmp_path)
    folder = cfg.archive_dir / "20260923-001"
    folder.mkdir(parents=True)
    secret = "PRIVATE-SOURCE-TOKEN-DO-NOT-ECHO"
    (folder / "scheduled.json").write_text(json.dumps({
        "schema_version": 1, "edition_id": "20260923-001",
        "status": "completed",
        "stage": secret,
        "stages": ["started", secret],
        "failure_codes": [secret],
    }))
    result = scheduled.read_run_status(cfg, target_date=DAY)
    assert secret not in json.dumps(result.as_dict())
    assert result.stage == "interrupted"
    assert result.stages == ()
    assert result.failure_codes == ("invalid_failure_codes",)


def test_receipt_status_is_private_when_read_by_same_owner(tmp_path, monkeypatch):
    cfg = settings(tmp_path)
    monkeypatch.setattr(scheduled, "run_pipeline",
                        lambda *_a, **_kw: SimpleNamespace(
                            failures=[], print_result=None, email_result=None,
                            pdf_path=Path("ready.pdf")))
    result = scheduled.run_once(cfg, target_date=DAY)
    assert result.status == "completed"
    folder = cfg.archive_dir / "20260923-001"
    assert (folder / "scheduled.json").stat().st_mode & 0o777 == 0o600
    if scheduled.fcntl is not None:
        assert (folder / ".kushluk-run.lock").stat().st_mode & 0o777 == 0o600
