"""Synthetic multi-morning rehearsal of #47; never substitutes for actual host trials."""
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

from kushluk import scheduled
from kushluk.config import Settings
from kushluk.run_metrics import timing_plan


def test_five_morning_rehearsal_pauses_recovers_and_never_reprints(
    tmp_path, monkeypatch,
):
    cfg = Settings(
        archive_dir=tmp_path / "archive", output_dir=tmp_path / "out",
        timezone="Europe/Berlin",
    )
    day = date(2026, 9, 23)
    calls = []

    def fixture_pipeline(*_args, **kwargs):
        calls.append(kwargs)
        for stage in ("sources_complete", "editorial_complete",
                      "rendered", "validated", "archive_ready", "complete"):
            kwargs["on_stage"](stage)
        return SimpleNamespace(
            failures=[], print_result=None, email_result=None,
            pdf_path=Path("synthetic-no-real-paper.pdf"),
        )

    monkeypatch.setattr(scheduled, "run_pipeline", fixture_pipeline)
    outcomes = []
    for i in range(5):
        target = day + timedelta(days=i)
        if i == 1:
            assert scheduled.pause_day(cfg, target_date=target).status == "paused"
            assert scheduled.run_once(cfg, target_date=target).status == "paused"
            assert scheduled.resume_day(cfg, target_date=target).status == "resumed"
        if i == 3:
            late = scheduled.run_once(
                cfg, target_date=target,
                latest_start=time(7, 45),
                now=datetime.combine(target, time(6), tzinfo=timezone.utc),
            )
            # Berlin in September is UTC+2: 06:00Z is after 07:45 local cutoff.
            assert late.status == "deadline_missed"
        completed = scheduled.run_once(cfg, target_date=target, ready_by=time(8))
        outcomes.append(completed.status)
        assert completed.status == "completed"
        # Recreate the Settings object to simulate a process restart.
        new_cfg = Settings(
            archive_dir=cfg.archive_dir, output_dir=cfg.output_dir,
            timezone=cfg.timezone,
        )
        assert scheduled.run_once(new_cfg, target_date=target).status == "already_completed"
    assert outcomes == ["completed"] * 5
    assert len(calls) == 5
    plan = timing_plan(cfg, target_date=day + timedelta(days=5))
    assert plan["status"] == "suggested_not_installed"
    assert plan["sample_count"] == 5
    assert plan["schedule_enabled"] is False
