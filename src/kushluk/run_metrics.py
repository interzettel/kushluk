"""Read-only, content-free local timing evidence for unattended morning runs.

Software readiness means a validated four-page PDF reached the archive.
It never means the printer produced paper or an email reached a human.
"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
import json
import math
import re
from zoneinfo import ZoneInfo

from kushluk.config import Settings
from kushluk.scheduled import STAGES, read_run_status


def _utc(value: object) -> datetime | None:
    if not isinstance(value, str) or len(value) > 40:
        return None
    try:
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            return None
        return parsed.astimezone(timezone.utc)
    except ValueError:
        return None


def _events(record: dict) -> list[dict[str, str]]:
    raw = record.get("stage_events", [])
    if not isinstance(raw, list) or len(raw) > 40:
        return []
    events = []
    previous = None
    for row in raw:
        if not isinstance(row, dict) or row.get("stage") not in STAGES:
            return []
        stamped = _utc(row.get("at"))
        if stamped is None or (previous is not None and stamped < previous):
            return []
        previous = stamped
        events.append({"stage": row["stage"], "at": stamped.isoformat()})
    return events


def _record(settings: Settings, target_date: date) -> dict:
    edition = settings.archive_dir / f"{target_date:%Y%m%d}-001" / "scheduled.json"
    if edition.is_symlink():
        return {}
    try:
        if not edition.is_file() or edition.stat().st_size > 16384:
            return {}
        data = json.loads(edition.read_text(encoding="utf-8"))
        if (not isinstance(data, dict) or data.get("schema_version") != 1
                or data.get("edition_id") != f"{target_date:%Y%m%d}-001"):
            return {}
        return data
    except (OSError, ValueError, UnicodeError):
        return {}


def _timing(record: dict, *, target_date: date, timezone_name: str) -> dict:
    events = _events(record)
    started = _utc(record.get("started_at"))
    if events and events[0]["stage"] == "started":
        start_event = _utc(events[0]["at"])
        if started is None or start_event != started:
            started = None
    else:
        events = []
    validated = False
    archived = None
    for event in events:
        if event["stage"] == "validated":
            validated = True
        if validated and event["stage"] == "archive_ready":
            archived = _utc(event["at"])
            break
    if started is None or archived is None or archived < started:
        archived = None
    elapsed = round((archived - started).total_seconds(), 2) if archived else None
    expected_clock = record.get("expected_start_local")
    expected = None
    if isinstance(expected_clock, str) and re.fullmatch(
        r"(?:[01]\\d|2[0-3]):[0-5]\\d", expected_clock
    ):
        expected = datetime.combine(
            target_date, time.fromisoformat(expected_clock),
            tzinfo=ZoneInfo(timezone_name),
        ).astimezone(timezone.utc)
    trigger_delay = round((started - expected).total_seconds(), 2) if (
        started is not None and expected is not None
    ) else None
    trigger_to_archive = round((archived - expected).total_seconds(), 2) if (
        archived is not None and expected is not None and archived >= expected
    ) else None
    ready_clock = record.get("ready_by_local")
    cutoff = None
    met = None
    if isinstance(ready_clock, str) and re.fullmatch(
        r"(?:[01]\d|2[0-3]):[0-5]\d", ready_clock
    ):
        cutoff = ready_clock
        if archived:
            deadline = datetime.combine(
                target_date, time.fromisoformat(cutoff),
                tzinfo=ZoneInfo(timezone_name),
            ).astimezone(timezone.utc)
            met = archived <= deadline
    return {
        "started_at_utc": started.isoformat() if started else None,
        "archive_ready_at_utc": archived.isoformat() if archived else None,
        "elapsed_to_archive_seconds": elapsed,
        "expected_trigger_local": expected_clock if expected is not None else None,
        "trigger_delay_seconds": trigger_delay,
        "trigger_to_archive_seconds": trigger_to_archive,
        "ready_by_local": cutoff,
        "ready_by_met": met,
        "finished_at_utc": (
            _utc(record.get("finished_at")).isoformat()
            if _utc(record.get("finished_at")) else None
        ),
        "validated_archived": archived is not None,
    }


def _delivery(record: dict, channel: str) -> str:
    requested = record.get("request", {})
    if not isinstance(requested, dict):
        return "unknown"
    flag = "send_to_printer" if channel == "print" else "send_email"
    events = _events(record)
    stages = [row["stage"] for row in events]
    if record.get("print_submitted" if channel == "print" else "email_sent") is True:
        return "submission_accepted"
    if f"{channel}_failed" in stages:
        return "submission_failed"
    if f"{channel}_submission_unknown" in stages:
        return "submission_uncertain"
    if requested.get(flag) is True:
        return "not_submitted"
    return "not_requested"


def run_report(settings: Settings, *, target_date: date) -> dict:
    state = read_run_status(settings, target_date=target_date)
    record = _record(settings, target_date)
    timing = _timing(record, target_date=target_date, timezone_name=settings.timezone)
    return {
        "schema_version": 1,
        "edition_id": state.edition_id,
        "status": state.status,
        "stage": state.stage,
        "failure_codes": list(state.failure_codes),
        "stage_events": _events(record),
        "timing": timing,
        "delivery": {
            "print": _delivery(record, "print"),
            "email": _delivery(record, "email"),
            "physical_print_verified": False,
            "recipient_delivery_verified": False,
        },
        "evidence_scope": "local_software_receipt_only",
    }


def timing_plan(
    settings: Settings, *, target_date: date, ready_by: time = time(8),
    margin_minutes: int = 10, history_days: int = 30,
) -> dict:
    """Conservative p90 software-readiness recommendation, never a scheduler."""
    if not 0 <= margin_minutes <= 120 or not 3 <= history_days <= 90:
        raise ValueError("invalid_timing_options")
    started_samples = []
    scheduled_samples = []
    for offset in range(1, history_days + 1):
        previous = target_date - timedelta(days=offset)
        report = run_report(settings, target_date=previous)
        metrics = report["timing"]
        if (report["status"] == "completed" and metrics["validated_archived"]
                and metrics["elapsed_to_archive_seconds"] is not None):
            seconds = metrics["elapsed_to_archive_seconds"]
            if 0 <= seconds <= 21600:
                started_samples.append(seconds)
            triggered = metrics["trigger_to_archive_seconds"]
            if triggered is not None and 0 <= triggered <= 21600:
                scheduled_samples.append(triggered)
    # Use like-for-like observations; never silently mix trigger-to-ready
    # and process-start-to-ready duration. Prefer the end-to-end series only
    # when at least three real local receipts actually contain a trigger clock.
    use_triggered = len(scheduled_samples) >= 3
    samples = sorted(scheduled_samples if use_triggered else started_samples)
    summary = {
        "schema_version": 1, "status": "insufficient_history",
        "history_days": history_days, "sample_count": len(samples),
        "required_samples": 3, "percentile": "nearest_rank_p90",
        "margin_minutes": margin_minutes, "ready_by_local": ready_by.strftime("%H:%M"),
        "recommended_start_local": None, "p90_seconds": None,
        "evidence_scope": "local_receipts_not_independent_host_proof",
        "schedule_enabled": False,
        "sample_basis": ("expected_trigger_to_archive" if use_triggered
                         else "run_started_to_archive"),
        "trigger_sample_count": len(scheduled_samples),
    }
    if len(samples) < 3:
        return summary
    p90 = samples[math.ceil(0.9 * len(samples)) - 1]
    ready_dt = datetime.combine(target_date, ready_by)
    planned = ready_dt - timedelta(seconds=p90, minutes=margin_minutes)
    if planned.date() != target_date:
        summary["status"] = "start_previous_day_not_supported"
        summary["p90_seconds"] = p90
        return summary
    summary.update({
        "status": "suggested_not_installed",
        "p90_seconds": p90,
        "recommended_start_local": planned.strftime("%H:%M"),
        "recommended_latest_start_local": (
            ready_dt - timedelta(minutes=margin_minutes)
        ).strftime("%H:%M"),
        "observed_samples_seconds": samples,
    })
    return summary
