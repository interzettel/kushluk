"""Native-scheduler-safe run gate. No external agent, service or daemon required."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timezone
import stat
from zoneinfo import ZoneInfo
import json
import os
from pathlib import Path
import tempfile
from typing import Any

try:
    import fcntl  # POSIX advisory locks for active-vs-interrupted status on Linux/macOS
except ImportError:  # Windows can still fail closed on nonterminal receipts
    fcntl = None

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
    stages: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "status": self.status,
            "edition_id": self.edition_id,
            "print_submitted": self.print_submitted,
            "email_sent": self.email_sent,
            "failure_codes": list(self.failure_codes),
            "stage": self.stage,
            "stages": list(self.stages),
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


# Only known, content-free machine stages may appear in status JSON.
STAGES = frozenset({
    "not_started", "paused", "started", "sources_complete",
    "editorial_complete", "rendering", "rendered", "validated",
    "archive_ready", "print_submission_unknown", "print_submitted",
    "print_failed", "email_submission_unknown", "email_sent", "email_failed",
    "complete", "interrupted",
})
TERMINAL = frozenset({"completed", "needs_review"})


def _safe_stages(value: object) -> tuple[str, ...]:
    if not isinstance(value, list) or len(value) > 40:
        return ()
    if not all(isinstance(s, str) and s in STAGES for s in value):
        return ()
    return tuple(value)


def _safe_failure_codes(value: object) -> tuple[str, ...]:
    if not isinstance(value, list) or len(value) > 40:
        return ("invalid_failure_codes",)
    if not all(isinstance(s, str) and 1 <= len(s) <= 64
               and s.replace("_", "").isalnum() for s in value):
        return ("invalid_failure_codes",)
    return tuple(value)


def _safe_stage(value: object) -> str:
    return value if isinstance(value, str) and value in STAGES else "interrupted"


def _lock_path(receipt: Path) -> Path:
    return receipt.with_name(".kushluk-run.lock")


def _run_lock(receipt: Path) -> int | None:
    """Keep the per-edition POSIX lock open until the run completes.

    Returning None means a concurrent run holds the lock. Never remove the lock
    inode, since replacing/unlinking it can let another process acquire a new one.
    """
    if fcntl is None:
        return -1  # Windows: exclusive receipt creation still prevents replay.
    flags = os.O_RDWR | os.O_CREAT
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(_lock_path(receipt), flags, 0o600)
    try:
        metadata = os.fstat(fd)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_mode & 0o077:
            raise OSError("Insecure run lock")
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            os.close(fd)
            return None
        return fd
    except BaseException:
        try:
            os.close(fd)
        except OSError:
            pass
        raise


def _running_lock_held(receipt: Path) -> bool:
    """Only a held POSIX lock proves a run is still alive, not an old PID."""
    if fcntl is None:
        return False
    lock = _lock_path(receipt)
    if not lock.exists() or lock.is_symlink():
        return False
    try:
        fd = os.open(lock, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    except OSError:
        return False
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        os.close(fd)
        return True
    except OSError:
        os.close(fd)
        return False
    else:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)
        return False


def _existing_outcome(path: Path, edition_id: str, request: dict[str, Any]) -> ScheduledOutcome:
    try:
        saved = json.loads(path.read_text(encoding="utf-8"))
        if saved.get("edition_id") != edition_id or saved.get("schema_version") != 1:
            raise ValueError("Receipt format does not match the edition.")
        if saved.get("request") != request:
            return ScheduledOutcome(
                "needs_review", edition_id,
                failure_codes=("request_mismatch",), stage=_safe_stage(saved.get("stage")),
            )
        if saved.get("status") == "completed":
            return ScheduledOutcome(
                "already_completed", edition_id,
                bool(saved.get("print_submitted")), bool(saved.get("email_sent")),
                _safe_failure_codes(saved.get("failure_codes", [])),
                _safe_stage(saved.get("stage", "complete")),
                _safe_stages(saved.get("stages", [])),
            )
    except (ValueError, OSError, TypeError, AttributeError):
        pass
    # Corrupt, interrupted, or failed deliveries must never silently resubmit.
    return ScheduledOutcome("needs_review", edition_id, failure_codes=("run_not_safe_to_retry",))


def _pause_marker(settings: Settings, target_date: date) -> Path:
    return settings.archive_dir / f"{target_date:%Y%m%d}-001" / ".kushluk-paused.json"


def _pause_state(path: Path, edition_id: str) -> str:
    """Fail closed if marker exists but isn't a private, valid pause record."""
    if not path.is_symlink() and not path.exists():
        return "active"
    try:
        metadata = path.lstat()
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_mode & 0o077:
            return "invalid"
        record = json.loads(path.read_text(encoding="utf-8"))
        if (not isinstance(record, dict) or record.get("schema_version") != 1
                or record.get("edition_id") != edition_id or record.get("paused") is not True):
            return "invalid"
        return "paused"
    except (OSError, UnicodeError, ValueError, TypeError):
        return "invalid"


def pause_day(settings: Settings, *, target_date: date) -> ScheduledOutcome:
    """Block future starts for this edition date; never cancel a running job."""
    edition_id = f"{target_date:%Y%m%d}-001"
    marker = _pause_marker(settings, target_date)
    marker.parent.mkdir(parents=True, exist_ok=True)
    existing = _pause_state(marker, edition_id)
    if existing != "active":
        return ScheduledOutcome(
            "already_paused" if existing == "paused" else "needs_review",
            edition_id, failure_codes=() if existing == "paused" else ("invalid_pause_marker",),
            stage="paused" if existing == "paused" else "not_started",
        )
    try:
        fd = os.open(marker, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump({"schema_version": 1, "edition_id": edition_id, "paused": True},
                      stream, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError:
        return ScheduledOutcome("needs_review", edition_id,
                                failure_codes=("pause_state_changed",))
    return ScheduledOutcome("paused", edition_id, stage="paused")


def resume_day(settings: Settings, *, target_date: date) -> ScheduledOutcome:
    """Remove only a well-formed pause marker; does not start or resend anything."""
    edition_id = f"{target_date:%Y%m%d}-001"
    marker = _pause_marker(settings, target_date)
    state = _pause_state(marker, edition_id)
    if state == "active":
        return ScheduledOutcome("not_paused", edition_id)
    if state == "invalid":
        return ScheduledOutcome("needs_review", edition_id,
                                failure_codes=("invalid_pause_marker",))
    try:
        marker.unlink()
    except OSError:
        return ScheduledOutcome("needs_review", edition_id,
                                failure_codes=("pause_marker_unavailable",))
    return ScheduledOutcome("resumed", edition_id)


def _latest_start_missed(
    target_date: date, latest_start: time, timezone_name: str, *, now: datetime | None,
) -> bool:
    """This is a last *start* cutoff, never a guarantee of delivery by that time."""
    tz = ZoneInfo(timezone_name)
    current = now or datetime.now(tz)
    if current.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    deadline = datetime.combine(target_date, latest_start, tzinfo=tz)
    return current.astimezone(timezone.utc) >= deadline.astimezone(timezone.utc)


def run_once(
    settings: Settings,
    *,
    target_date: date,
    send_to_printer: bool = False,
    send_email: bool = False,
    email_on_print_failure: bool = False,
    print_profile: str = "a4-home",
    latest_start: time | None = None,
    now: datetime | None = None,
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
    receipt = folder / "scheduled.json"
    if receipt.exists() or receipt.is_symlink():
        return _existing_outcome(receipt, edition_id, request)
    state = _pause_state(_pause_marker(settings, target_date), edition_id)
    if state == "paused":
        return ScheduledOutcome("paused", edition_id, stage="paused")
    if state == "invalid":
        return ScheduledOutcome("needs_review", edition_id,
                                failure_codes=("invalid_pause_marker",))
    if latest_start is not None and _latest_start_missed(
        target_date, latest_start, settings.timezone, now=now,
    ):
        return ScheduledOutcome("deadline_missed", edition_id,
                                failure_codes=("latest_start_missed",))
    folder.mkdir(parents=True, exist_ok=True)
    # Recheck after mkdir for a pause written by another process.
    state = _pause_state(_pause_marker(settings, target_date), edition_id)
    if state != "active":
        return ScheduledOutcome(
            "paused" if state == "paused" else "needs_review", edition_id,
            failure_codes=() if state == "paused" else ("invalid_pause_marker",),
            stage="paused" if state == "paused" else "not_started",
        )
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
        "stages": ["started"],
    }
    try:
        lock_fd = _run_lock(receipt)
    except OSError:
        return ScheduledOutcome("needs_review", edition_id, failure_codes=("run_lock_unavailable",))
    if lock_fd is None:
        return ScheduledOutcome("needs_review", edition_id, failure_codes=("run_in_progress",))
    try:
        # The receipt is still the durable at-most-once gate, independent of locks.
        with receipt.open("x", encoding="utf-8") as stream:
            os.chmod(receipt, 0o600)
            json.dump(initial, stream, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError:
        if lock_fd >= 0:
            os.close(lock_fd)
        return _existing_outcome(receipt, edition_id, request)

    record = initial

    def on_stage(stage: str) -> None:
        if stage not in STAGES:
            raise ValueError("Unrecognized pipeline stage")
        record["stage"] = stage
        record["stages"].append(stage)
        record["updated_at"] = datetime.now(timezone.utc).isoformat()
        _atomic_write(receipt, record)

    def before_delivery(channel: str) -> None:
        # Crash-after-request / before-response is ambiguous: a second call MUST
        # not repeat a print or SMTP side effect without explicit human review.
        record["delivery_attempts"].append(channel)
        record["status"] = f"{channel}_submission_unknown"
        record["stage"] = f"{channel}_submission_unknown"
        record["stages"].append(record["stage"])
        _atomic_write(receipt, record)

    try:
        result = run_pipeline(
            settings, target_date=target_date, send_to_printer=send_to_printer,
            send_email=send_email, email_on_print_failure=email_on_print_failure,
            print_profile=print_profile, before_delivery=before_delivery,
            on_stage=on_stage,
        )
        errors = tuple(f.code for f in result.failures if f.severity == "failed")
        if getattr(result, "pdf_path", True) is None:
            errors += ("validated_pdf_missing",)
        submitted = bool(result.print_result and result.print_result.success)
        mailed = bool(result.email_result and result.email_result.status == "sent")
        status = "needs_review" if errors else "completed"
        outcome = ScheduledOutcome(
            status, edition_id, submitted, mailed, errors, "complete",
            tuple(record["stages"]),
        )
        record.update(outcome.as_dict())
        _atomic_write(receipt, record)
        return outcome
    except Exception as exc:
        # Don't store str(exc): providers sometimes put tokens/URLs in errors.
        record["status"] = "needs_review"
        record["stage"] = "interrupted"
        record["stages"].append("interrupted")
        record["failure_codes"] = [f"unexpected_{type(exc).__name__}"]
        _atomic_write(receipt, record)
        return ScheduledOutcome(
            "needs_review", edition_id,
            failure_codes=(f"unexpected_{type(exc).__name__}",),
            stage="interrupted", stages=tuple(record["stages"]),
        )
    finally:
        if lock_fd >= 0:
            os.close(lock_fd)


def read_run_status(settings: Settings, *, target_date: date) -> ScheduledOutcome:
    edition_id = f"{target_date:%Y%m%d}-001"
    path = settings.archive_dir / edition_id / "scheduled.json"
    if not path.exists() and not path.is_symlink():
        paused = _pause_state(_pause_marker(settings, target_date), edition_id)
        if paused == "paused":
            return ScheduledOutcome("paused", edition_id, stage="paused")
        if paused == "invalid":
            return ScheduledOutcome("needs_review", edition_id,
                                    failure_codes=("invalid_pause_marker",))
        return ScheduledOutcome("not_run", edition_id)
    try:
        saved = json.loads(path.read_text(encoding="utf-8"))
        if saved.get("edition_id") != edition_id or saved.get("schema_version") != 1:
            raise ValueError("Invalid receipt")
        if not isinstance(saved, dict):
            raise ValueError("Invalid receipt type")
        state = saved["status"]
        if state not in {"started", "print_submission_unknown",
                         "email_submission_unknown", "completed", "needs_review"}:
            raise ValueError("Unknown receipt state")
        if state not in TERMINAL:
            state = "in_progress" if _running_lock_held(path) else "needs_review"
        return ScheduledOutcome(
            state, edition_id,
            bool(saved.get("print_submitted")), bool(saved.get("email_sent")),
            _safe_failure_codes(saved.get("failure_codes", [])),
            _safe_stage(saved.get("stage", "interrupted")),
            _safe_stages(saved.get("stages", [])),
        )
    except (ValueError, OSError, TypeError, AttributeError, KeyError):
        return ScheduledOutcome("needs_review", edition_id, failure_codes=("invalid_receipt",))
