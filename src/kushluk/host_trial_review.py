"""Read-only matching of human host-trial receipts to local scheduled runs.

A matching self-report is not proof of unattended execution or physical delivery.
Never submits a job, enables a scheduler, uploads evidence or accepts a release gate.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from hashlib import sha256
import json
from pathlib import Path
import re

from kushluk.config import Settings
from kushluk.run_metrics import run_report


MAX_RECEIPTS = 100
MAX_RECEIPT_BYTES = 128 * 1024
MAX_RUN_BYTES = 16 * 1024
SHA256 = re.compile(r"[0-9a-f]{64}\Z")


class HostTrialReviewError(ValueError):
    """An operator-safe, non-content-bearing error."""


def _local_file_bytes(path: Path, limit: int) -> bytes | None:
    try:
        if path.is_symlink() or not path.is_file():
            return None
        size = path.stat().st_size
        if not 0 < size <= limit:
            return None
        with path.open("rb") as stream:
            data = stream.read(limit + 1)
        return data if len(data) == size else None
    except OSError:
        return None


def _sha_entry(value: object) -> bool:
    return (isinstance(value, dict)
            and isinstance(value.get("sha256"), str)
            and SHA256.fullmatch(value["sha256"]) is not None
            and type(value.get("bytes")) is int
            and value["bytes"] > 0)


def _host_attestation(value: object) -> bool:
    if not isinstance(value, dict):
        return False
    if (type(value.get("schema_version")) is not int
            or value["schema_version"] != 1
            or value.get("kind") != "host-resume"
            or value.get("operator_reported_result") != "pass"
            or value.get("attestation") != "operator-self-report; not independently validated"
            or value.get("independently_verified") is not False
            or value.get("release_gate_accepted") is not False
            or value.get("acknowledged_direct_observation") is not True
            or not _sha_entry(value.get("artifact"))):
        return False
    evidence = value.get("evidence_files")
    if not isinstance(evidence, list) or not 1 <= len(evidence) <= 8:
        return False
    if not all(_sha_entry(item) for item in evidence):
        return False
    timestamp = value.get("observed_at_utc")
    try:
        if not isinstance(timestamp, str) or len(timestamp) > 40:
            return False
        stamp = datetime.fromisoformat(timestamp)
        return stamp.tzinfo is not None and stamp.utcoffset() is not None
    except ValueError:
        return False


def _receipts(receipts_dir: Path) -> tuple[dict[tuple[str, int], list[dict]], int]:
    if receipts_dir.is_symlink() or not receipts_dir.is_dir():
        raise HostTrialReviewError("receipt_directory_unavailable")
    try:
        paths = sorted(receipts_dir.iterdir())
    except OSError as exc:
        raise HostTrialReviewError("receipt_directory_unavailable") from exc
    if len(paths) > MAX_RECEIPTS:
        raise HostTrialReviewError("receipt_directory_exceeds_100_entries")
    indexed: dict[tuple[str, int], list[dict]] = {}
    invalid = 0
    for path in paths:
        data = _local_file_bytes(path, MAX_RECEIPT_BYTES) if path.suffix == ".json" else None
        if data is None:
            invalid += 1
            continue
        try:
            payload = json.loads(data)
        except (ValueError, UnicodeError):
            invalid += 1
            continue
        if not _host_attestation(payload):
            invalid += 1
            continue
        key = (payload["artifact"]["sha256"], payload["artifact"]["bytes"])
        indexed.setdefault(key, []).append(payload)
    return indexed, invalid


def review_host_trial(
    *, archive_root: Path, receipts_dir: Path, start_date: date, days: int = 5,
    timezone: str = "Europe/Berlin",
) -> dict:
    """Correlate precisely five or more *local edition dates* to private evidence.

    All evidence remains operator-reported and requires actual host/device review.
    """
    if type(days) is not int or not 5 <= days <= 14:
        raise HostTrialReviewError("trial_days_must_be_between_5_and_14")
    if type(start_date) is not date:
        raise HostTrialReviewError("invalid_start_date")
    if archive_root.is_symlink() or not archive_root.is_dir():
        raise HostTrialReviewError("archive_directory_unavailable")
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
    try:
        ZoneInfo(timezone)
    except (ZoneInfoNotFoundError, ValueError, TypeError) as exc:
        raise HostTrialReviewError("invalid_timezone") from exc
    matching, invalid = _receipts(receipts_dir)
    settings = Settings(archive_dir=archive_root, timezone=timezone)
    rows: list[dict] = []
    matched: set[tuple[str, int]] = set()
    for offset in range(days):
        day = start_date + timedelta(days=offset)
        expected_id = f"{day:%Y%m%d}-001"
        edition_dir = archive_root / expected_id
        file = edition_dir / "scheduled.json"
        raw = None if edition_dir.is_symlink() else _local_file_bytes(file, MAX_RUN_BYTES)
        digest = (sha256(raw).hexdigest(), len(raw)) if raw is not None else None
        record_valid = False
        if raw:
            try:
                record = json.loads(raw)
                record_valid = (
                    isinstance(record, dict)
                    and type(record.get("schema_version")) is int
                    and record.get("schema_version") == 1
                    and record.get("edition_id") == expected_id
                )
            except (UnicodeError, ValueError):
                pass
        row = {
            "local_edition_date": day.isoformat(),
            "run_receipt_readable": record_valid,
            "software_completed_with_validated_archive": False,
            "expected_scheduler_start_recorded": False,
            "software_ready_by_target": None,
            "print_submission": "unknown",
            "email_submission": "unknown",
            "matching_operator_host_pass_reported": False,
        }
        if record_valid:
            report = run_report(settings, target_date=day)
            # Fail closed when a writer changes the receipt during inspection.
            if _local_file_bytes(file, MAX_RUN_BYTES) == raw:
                timing = report["timing"]
                row["software_completed_with_validated_archive"] = (
                    report["status"] == "completed" and timing["validated_archived"] is True
                )
                row["expected_scheduler_start_recorded"] = (
                    timing["expected_trigger_local"] is not None
                )
                row["software_ready_by_target"] = timing["ready_by_met"]
                row["print_submission"] = report["delivery"]["print"]
                row["email_submission"] = report["delivery"]["email"]
                if row["software_completed_with_validated_archive"] and digest in matching:
                    # The receipt filename is irrelevant: match actual archived bytes.
                    # A self-report recorded BEFORE the run ended cannot describe its outcome.
                    finished = record.get("finished_at")
                    try:
                        completed_at = datetime.fromisoformat(finished)
                        for receipt in matching[digest]:
                            observed_at = datetime.fromisoformat(receipt["observed_at_utc"])
                            if (completed_at.tzinfo is not None
                                    and observed_at >= completed_at):
                                row["matching_operator_host_pass_reported"] = True
                                matched.add(digest)
                                break
                    except (TypeError, ValueError):
                        pass
        rows.append(row)
    paired = sum(row["matching_operator_host_pass_reported"] for row in rows)
    scheduled_paired = sum(
        row["matching_operator_host_pass_reported"]
        and row["expected_scheduler_start_recorded"] for row in rows
    )
    return {
        "schema_version": 1,
        "trial_local_start_date": start_date.isoformat(),
        "trial_days": days,
        "days_with_validated_software_archives": sum(
            row["software_completed_with_validated_archive"] for row in rows
        ),
        "days_with_matching_operator_host_reports": paired,
        "days_with_matching_reports_and_recorded_expected_start": scheduled_paired,
        "all_trial_days_have_matching_reports": paired == days,
        "unmatched_or_out_of_window_host_reports": sum(
            len(items) for key, items in matching.items() if key not in matched
        ),
        "invalid_or_unsupported_receipts": invalid,
        "days": rows,
        "independently_verified": False,
        "unattended_host_verified": False,
        "physical_print_verified": False,
        "release_gate_accepted": False,
        "note": ("A match only ties a self-report to scheduled.json bytes. Expected start "
                 "can be passed manually; five dates do not prove unattended mornings. "
                 "Review OS scheduler logs, wake/reboot, retries, PDFs and physical paper."),
    }
