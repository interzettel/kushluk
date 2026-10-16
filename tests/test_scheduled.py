from datetime import date
import json
from types import SimpleNamespace

from kushluk import scheduled
from kushluk.config import Settings


TARGET = date(2026, 9, 23)


def settings(tmp_path):
    return Settings(archive_dir=tmp_path / "archive", output_dir=tmp_path / "output")


def outcome(*, print_success=True):
    return SimpleNamespace(
        failures=[],
        print_result=SimpleNamespace(success=print_success) if print_success else None,
        email_result=None,
    )


def test_repeated_scheduled_print_cannot_submit_twice(tmp_path, monkeypatch):
    calls = []

    def fake_pipeline(*args, **kwargs):
        calls.append(kwargs)
        kwargs["before_delivery"]("print")
        return outcome()

    monkeypatch.setattr(scheduled, "run_pipeline", fake_pipeline)
    cfg = settings(tmp_path)
    first = scheduled.run_once(cfg, target_date=TARGET, send_to_printer=True)
    second = scheduled.run_once(cfg, target_date=TARGET, send_to_printer=True)
    assert first.status == "completed"
    assert first.print_submitted
    assert second.status == "already_completed"
    assert len(calls) == 1
    receipt = json.loads(
        (cfg.archive_dir / "20260923-001" / "scheduled.json").read_text()
    )
    assert receipt["delivery_attempts"] == ["print"]
    assert receipt["print_submitted"] is True


def test_interrupted_submission_blocks_retry_and_redacts_failure(tmp_path, monkeypatch):
    calls = []

    def interrupted(*args, **kwargs):
        calls.append(True)
        kwargs["before_delivery"]("print")
        raise RuntimeError("https://private.example/ics?token=secret")

    monkeypatch.setattr(scheduled, "run_pipeline", interrupted)
    cfg = settings(tmp_path)
    one = scheduled.run_once(cfg, target_date=TARGET, send_to_printer=True)
    two = scheduled.run_once(cfg, target_date=TARGET, send_to_printer=True)
    assert one.status == "needs_review"
    assert two.status == "needs_review"
    assert len(calls) == 1
    saved = (cfg.archive_dir / "20260923-001" / "scheduled.json").read_text()
    assert "secret" not in saved
    assert "RuntimeError" in saved


def test_concurrent_attempt_is_refused(tmp_path, monkeypatch):
    cfg = settings(tmp_path)
    inner = []

    def fake_pipeline(*args, **kwargs):
        inner.append(scheduled.run_once(cfg, target_date=TARGET))
        return outcome(print_success=False)

    monkeypatch.setattr(scheduled, "run_pipeline", fake_pipeline)
    first = scheduled.run_once(cfg, target_date=TARGET)
    assert first.status == "completed"
    assert inner[0].status == "needs_review"


def test_corrupt_receipt_does_not_trigger_new_delivery(tmp_path, monkeypatch):
    cfg = settings(tmp_path)
    path = cfg.archive_dir / "20260923-001" / "scheduled.json"
    path.parent.mkdir(parents=True)
    path.write_text("{bad JSON", encoding="utf-8")
    monkeypatch.setattr(
        scheduled, "run_pipeline", lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("No retry permitted")
        )
    )
    assert scheduled.run_once(cfg, target_date=TARGET).status == "needs_review"
    assert scheduled.read_run_status(cfg, target_date=TARGET).status == "needs_review"


def test_run_status_unstarted_and_receipt_without_private_sources(tmp_path, monkeypatch):
    cfg = settings(tmp_path)
    assert scheduled.read_run_status(cfg, target_date=TARGET).status == "not_run"
    monkeypatch.setattr(
        scheduled, "run_pipeline", lambda *args, **kwargs: outcome(print_success=False)
    )
    out = scheduled.run_once(cfg, target_date=TARGET)
    assert out.status == "completed"
    assert scheduled.read_run_status(cfg, target_date=TARGET).status == "completed"
    receipt = (cfg.archive_dir / "20260923-001" / "scheduled.json").read_text()
    assert "calendar" not in receipt
    assert "smtp" not in receipt
