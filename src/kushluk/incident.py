"""Typed, content-free, local run incident protocol. No automatic escalation.

An agent may inspect this deterministic summary but it cannot act on or share
the underlying receipt without a separate user authorization.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import stat

from kushluk.config import Settings
from kushluk.run_metrics import run_report


# No user-supplied/third-party diagnostic string is echoed into reports.
# Unknown failure identifiers are replaced with one generic code.
KNOWN_FAILURE_CODES = frozenset({
    "request_mismatch", "run_not_safe_to_retry", "invalid_failure_codes",
    "invalid_pause_marker", "pause_state_changed", "pause_marker_unavailable",
    "invalid_print_profile", "latest_start_missed", "print_failed",
    "print_skipped", "email_failed", "pdf_unavailable", "layout_overflow",
    "imposition_failed", "weather_unavailable", "calendar_unavailable",
    "calendar_ics_unavailable", "tasks_unavailable", "task_unavailable",
    "rss_unavailable", "research_unavailable", "editorial_unavailable",
    "source_unavailable", "archive_unavailable", "render_unavailable",
    "delivery_uncertain", "printer_unavailable", "lock_unavailable",
    "run_interrupted", "no_pdf", "unknown_failure", "invalid_receipt",
})
_GUIDANCE = {
    # (component, severity when no stronger run failure, action, permission)
    "manual_review_no_auto_retry": (
        "scheduler", "failed", "inspect_local_receipt_and_external_queues",
        "human_review_required",
    ),
    "delivery_needs_attention": (
        "delivery", "failed", "inspect_external_delivery_queue",
        "human_review_required",
    ),
    "archive_ready_late": (
        "scheduler", "degraded", "review_measured_scheduler_history",
        "human_review_required",
    ),
    "no_run_receipt": (
        "scheduler", "degraded", "check_local_scheduler_configuration",
        "read_only",
    ),
    "schedule_paused": (
        "scheduler", "info", "review_pause_state", "read_only",
    ),
    "run_in_progress": (
        "scheduler", "info", "inspect_run_status_without_restarting",
        "read_only",
    ),
    "printer_queue_not_physical_proof": (
        "printer", "info", "inspect_physical_paper_output", "human_review_required",
    ),
    "smtp_accepted_not_recipient_proof": (
        "email", "info", "check_recipient_delivery_separately", "human_review_required",
    ),
    "archive_complete_delivery_not_implied": (
        "archive", "info", "no_action_needed", "none",
    ),
    "status_requires_review": (
        "scheduler", "failed", "inspect_local_run_status", "human_review_required",
    ),
}
_DELIVERY_STATES = frozenset({
    "submission_accepted", "submission_failed", "submission_uncertain",
    "not_submitted", "not_requested", "unknown",
})
_SEVERITY_ORDER = {"info": 0, "degraded": 1, "failed": 2}


def build_incident_report(settings: Settings, *, target_date: date) -> dict:
    """Return fixed-schema local facts and suggested manual action only."""
    report = run_report(settings, target_date=target_date)
    guidance = report["operator_guidance"]
    code = guidance.get("code")
    if code not in _GUIDANCE:
        code = "status_requires_review"
    component, default_severity, action, permission = _GUIDANCE[code]
    failures = list(report.get("failure_codes") or [])[:40]
    # A malformed receipt could contain a plausible-looking secret value:
    # never trust even alphanumeric codes without a strict known-code match.
    error_codes = sorted({
        value if type(value) is str and value in KNOWN_FAILURE_CODES
        else "unclassified_failure"
        for value in failures
    })
    state = report["status"]
    severity = default_severity
    if state == "needs_review":
        severity = "failed"
    elif state in {"not_run", "interrupted"} and _SEVERITY_ORDER[severity] < 1:
        severity = "degraded"
    delivery = report.get("delivery", {})
    print_state = delivery.get("print")
    email_state = delivery.get("email")
    print_state = print_state if print_state in _DELIVERY_STATES else "unknown"
    email_state = email_state if email_state in _DELIVERY_STATES else "unknown"
    signature = "|".join((str(target_date), code, severity, *error_codes))
    return {
        "schema_version": 1,
        "report_template_version": 1,
        "kind": "local_run_incident",
        "incident_id": "local-" + sha256(signature.encode("ascii")).hexdigest()[:20],
        "edition_id": f"{target_date:%Y%m%d}-001",
        "observed_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": state,
        "component": component,
        "severity": severity,
        "error_code": code,
        "failure_codes": error_codes,
        "delivery": {
            "printer_submission": print_state,
            "email_submission": email_state,
            "paper_verified": False,
            "recipient_verified": False,
        },
        "edition_usable": (
            "validated_archive_reported" if report["timing"]["validated_archived"]
            else "not_established"
        ),
        "fallback_observation": "not_independently_verified",
        "suggested_actions": [{
            "id": action,
            "permission": permission,
            "automatic_retry_allowed": False,
            "requires_operator_decision": permission == "human_review_required",
        }],
        # Read the *known* fixed-text response only, never arbitrary receipt text.
        "human_notice": {
            "code": code,
            "message": _safe_message(code),
        },
        "user_notification_required": severity == "failed",
        "report_prepared": True,
        "remote_report_authorized": False,
        "remote_report_sent": False,
        "sources_contacted": False,
        "delivery_attempted_by_report": False,
        "sensitive_fields_redacted": True,
        "safe_diagnostic_fields": [
            "edition_id", "status", "component", "severity", "error_code",
            "failure_codes", "delivery", "edition_usable",
        ],
        "evidence_scope": "local_receipts_only_not_real_device_verification",
    }


def _safe_message(code: str) -> str:
    """Content-independent plain language, even if a receipt was manipulated."""
    return {
        "manual_review_no_auto_retry": (
            "The run needs review. Check the local receipt and external queues "
            "before deciding whether to resend. No automatic retry is allowed."
        ),
        "delivery_needs_attention": (
            "Delivery failed or is uncertain. Check the external queue before "
            "considering a deliberate archive-only resend."
        ),
        "archive_ready_late": (
            "The edition archive was prepared after the target time. Review the "
            "local timing history; no physical delivery is confirmed."
        ),
        "no_run_receipt": (
            "No completed run receipt was found for this date. Check your local "
            "scheduler before starting anything."
        ),
        "schedule_paused": "This edition date is paused. No run was started.",
        "run_in_progress": (
            "A local run appears active. Do not start another instance."
        ),
        "printer_queue_not_physical_proof": (
            "A printer submission was accepted. Check the actual pages before "
            "marking the edition delivered."
        ),
        "smtp_accepted_not_recipient_proof": (
            "SMTP accepted the request; receipt by the reader is unconfirmed."
        ),
        "archive_complete_delivery_not_implied": (
            "The archive is ready. This does not establish paper or email delivery."
        ),
        "status_requires_review": (
            "Review the local run state; no action or successful delivery is implied."
        ),
    }[code]


def save_private_incident_report(path: Path, report: dict) -> None:
    """Explicit create-only local export; never uploads, replaces or follows links."""
    if path.is_symlink() or path.exists():
        raise ValueError("incident_export_already_exists")
    if path.parent.is_symlink():
        raise ValueError("incident_export_unsafe_directory")
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    parent_stat = path.parent.lstat()
    if (not stat.S_ISDIR(parent_stat.st_mode)
            or parent_stat.st_mode & 0o077):
        raise ValueError("incident_export_unsafe_directory")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags, 0o600)
    except FileExistsError as exc:
        raise ValueError("incident_export_already_exists") from exc
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(report, stream, ensure_ascii=True, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise
