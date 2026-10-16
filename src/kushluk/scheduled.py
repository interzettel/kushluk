"""Native-scheduler-safe run gate. No external agent, service or daemon required."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
import json
import os
from pathlib import Path
import tempfile
from typing import Any

from kushluk.config import Settings
from kushluk.pipeline import run_pipeline


@dataclass(slots=True)
class ScheduledOutcome:
    status: str
    edition_id: str
    print_submitted: bool = False
    email_sent: bool = False
    failure_codes: tuple[str, ...] = ()
    stage: str = "not_started"

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "status": self.status,
            "edition_id": self.edition_id,
            "print_submitted": self.print_submitted,
            "email_sent": self.email_sent,
            "failure_codes": list(self.failure_codes),
            "stage": self.stage,
        }


def _atomic_write(path: Path, record: dict[str, Any]) -> None:
    """Replace a durable receipt atomically; no edition text or secrets in records."""
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, prefix=".kushluk-run-",
            delete=False,
        ) as stream:
            tmp_path = Path(stream.name)
            json.dump(record, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp_path, path)
    finally:
        if tmp_path is not None:
            tmp_path.unlink(missing_ok=True)


def _existing_outcome(path: Path, edition_id: str, request: dict[str, Any]) -> ScheduledOutcome:
    try:
        saved = json.loads(path.read_text(encoding="utf-8"))
        if saved.get("edition_id") != edition_id or saved.get("schema_version") != 1:
            raise ValueError("Receipt format does not match the edition.")
        if saved.get("request") != request:
            return ScheduledOutcome(
                "needs_review", edition_id,
                failure_codes=("request_mismatch",), stage=str(saved.get("stage", "unknown")),
            )
        if saved.get("status") == "completed":
            return ScheduledOutcome(
                "already_completed", edition_id,
                bool(saved.get("print_submitted")), bool(saved.get("email_sent")),
                tuple(saved.get("failure_codes", [])),
                str(saved.get("stage", "complete")),
            )
    except (ValueError, OSError, TypeError, AttributeError):
        pass
    # Corrupt, interrupted, or failed deliveries must never silently resubmit.
    return ScheduledOutcome("needs_review", edition_id, failure_codes=("run_not_safe_to_retry",))


def run_once(
    settings: Settings,
    *,
    target_date: date,
    send_to_printer: bool = False,
    send_email: bool = False,
    email_on_print_failure: bool = False,
    print_profile: str = "a4-home",
) -> ScheduledOutcome:
    """At-most-once delivery attempt per local edition; uncertain states block replay."""
    if print_profile not in {"a4-home", "a3-folded"}:
        return ScheduledOutcome(
            "needs_review", f"{target_date:%Y%m%d}-001",
            failure_codes=("invalid_print_profile",),
        )
    request = {
        "send_to_printer": send_to_printer,
        "send_email": send_email,
        "email_on_print_failure": email_on_print_failure,
        "print_profile": print_profile,
    }
    edition_id = f"{target_date:%Y%m%d}-001"
    folder = settings.archive_dir / edition_id
    folder.mkdir(parents=True, exist_ok=True)
    receipt = folder / "scheduled.json"
    initial = {
        "schema_version": 1,
        "edition_id": edition_id,
        "status": "started",
        "stage": "started",
        "request": request,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "print_submitted": False,
        "email_sent": False,
        "failure_codes": [],
        "delivery_attempts": [],
    }
    try:
        # Exclusive creation is the durable concurrency gate across processes.
        with receipt.open("x", encoding="utf-8") as stream:
            os.chmod(receipt, 0o600)
            json.dump(initial, stream, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError:
        return _existing_outcome(receipt, edition_id, request)

    record = initial

    def on_stage(stage: str) -> None:
        record["stage"] = stage
        record["updated_at"] = datetime.now(timezone.utc).isoformat()
        _atomic_write(receipt, record)

    def before_delivery(channel: str) -> None:
        # Crash-after-request / before-response is ambiguous: a second call MUST
        # not repeat a print or SMTP side effect without explicit human review.
        record["delivery_attempts"].append(channel)
        record["status"] = f"{channel}_submission_unknown"
        record["stage"] = f"{channel}_submission_unknown"
        _atomic_write(receipt, record)

    try:
        result = run_pipeline(
            settings, target_date=target_date, send_to_printer=send_to_printer,
            send_email=send_email, email_on_print_failure=email_on_print_failure,
            print_profile=print_profile, before_delivery=before_delivery,
            on_stage=on_stage,
        )
        errors = tuple(f.code for f in result.failures if f.severity == "failed")
        submitted = bool(result.print_result and result.print_result.success)
        mailed = bool(result.email_result and result.email_result.status == "sent")
        status = "needs_review" if errors else "completed"
        outcome = ScheduledOutcome(status, edition_id, submitted, mailed, errors, "complete")
        record.update(outcome.as_dict())
        _atomic_write(receipt, record)
        return outcome
    except Exception as exc:
        # Don't store str(exc): providers sometimes put tokens/URLs in errors.
        record["status"] = "needs_review"
        record["stage"] = "interrupted"
        record["failure_codes"] = [f"unexpected_{type(exc).__name__}"]
        _atomic_write(receipt, record)
        return ScheduledOutcome(
            "needs_review", edition_id,
            failure_codes=(f"unexpected_{type(exc).__name__}",),
            stage="interrupted",
        )


def read_run_status(settings: Settings, *, target_date: date) -> ScheduledOutcome:
    edition_id = f"{target_date:%Y%m%d}-001"
    path = settings.archive_dir / edition_id / "scheduled.json"
    if not path.exists():
        return ScheduledOutcome("not_run", edition_id)
    try:
        saved = json.loads(path.read_text(encoding="utf-8"))
        if saved.get("edition_id") != edition_id or saved.get("schema_version") != 1:
            raise ValueError("Invalid receipt")
        return ScheduledOutcome(
            str(saved["status"]), edition_id,
            bool(saved.get("print_submitted")), bool(saved.get("email_sent")),
            tuple(saved.get("failure_codes", [])),
            str(saved.get("stage", "unknown")),
        )
    except (ValueError, OSError, TypeError, AttributeError, KeyError):
        return ScheduledOutcome("needs_review", edition_id, failure_codes=("invalid_receipt",))
