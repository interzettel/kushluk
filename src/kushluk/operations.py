"""Stable local orchestration request/response v1.

Reads only a small explicit JSON instruction, never arbitrary code or network
endpoints. External schedulers invoke the same owned core; no provider runtime
owns editorial state. Actual delivery requires explicit authorization.
"""
from __future__ import annotations

from datetime import date, datetime, time
import json
from pathlib import Path
import re
from typing import Any

from kushluk.config import Settings
from kushluk.recovery import deliver_archived
from kushluk.run_metrics import run_report, timing_plan
from kushluk.scheduled import pause_day, read_run_status, resume_day, run_once


class OperationError(ValueError):
    """Safe, fixed-shape request error: never include arbitrary request values."""


_ACTION_FIELDS = {
    "run": {"schema_version", "action", "date", "print", "email",
            "email_on_print_failure", "print_profile", "latest_start",
            "acknowledge_delivery", "ready_by"},
    "status": {"schema_version", "action", "date"},
    "report": {"schema_version", "action", "date"},
    "timing_plan": {"schema_version", "action", "date", "ready_by",
                    "margin_minutes", "history_days"},
    "pause": {"schema_version", "action", "date"},
    "resume": {"schema_version", "action", "date"},
    "deliver_archived": {"schema_version", "action", "date", "channel",
                         "request_id", "print_profile", "acknowledge_possible_duplicate"},
}


def _strict_date(value: object) -> date:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise OperationError("invalid_date")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise OperationError("invalid_date") from exc


def _time(value: object) -> time:
    if not isinstance(value, str) or not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", value):
        raise OperationError("invalid_latest_start")
    return time.fromisoformat(value)


def operate_request(
    settings: Settings, request: object, *, now: datetime | None = None,
) -> dict[str, Any]:
    if not isinstance(request, dict) or request.get("schema_version") != 1:
        raise OperationError("unsupported_schema")
    action = request.get("action")
    if not isinstance(action, str) or action not in _ACTION_FIELDS:
        raise OperationError("unsupported_action")
    if set(request) - _ACTION_FIELDS[action]:
        raise OperationError("unknown_fields")
    target_date = _strict_date(request.get("date"))
    if action == "report":
        report = run_report(settings, target_date=target_date)
        return {"schema_version": 1, "action": action,
                "status": report["status"], "outcome": report, "physical_verified": False}
    if action == "timing_plan":
        for key, lo, hi in (("margin_minutes", 0, 120), ("history_days", 3, 90)):
            if key in request and (
                type(request[key]) is not int or not lo <= request[key] <= hi
            ):
                raise OperationError("invalid_timing_options")
        ready_clock = _time(request.get("ready_by", "08:00"))
        result_plan = timing_plan(
            settings, target_date=target_date, ready_by=ready_clock,
            margin_minutes=request.get("margin_minutes", 10),
            history_days=request.get("history_days", 30),
        )
        return {"schema_version": 1, "action": action,
                "status": result_plan["status"], "outcome": result_plan,
                "physical_verified": False}
    if action == "status":
        result = read_run_status(settings, target_date=target_date)
    elif action == "pause":
        result = pause_day(settings, target_date=target_date)
    elif action == "resume":
        result = resume_day(settings, target_date=target_date)
    elif action == "run":
        for field in ("print", "email", "email_on_print_failure", "acknowledge_delivery"):
            if field in request and type(request[field]) is not bool:
                raise OperationError("invalid_boolean")
        printer = request.get("print", False)
        email = request.get("email", False)
        fallback = request.get("email_on_print_failure", False)
        if fallback and not printer:
            raise OperationError("fallback_requires_print")
        if (printer or email or fallback) and request.get("acknowledge_delivery") is not True:
            raise OperationError("delivery_consent_required")
        profile = request.get("print_profile", "a4-home")
        if profile not in ("a4-home", "a3-folded"):
            raise OperationError("invalid_print_profile")
        latest_start = (_time(request["latest_start"])
                        if "latest_start" in request else None)
        ready_by = _time(request["ready_by"]) if "ready_by" in request else None
        result = run_once(
            settings, target_date=target_date,
            send_to_printer=printer, send_email=email,
            email_on_print_failure=fallback, print_profile=profile,
            latest_start=latest_start, ready_by=ready_by, now=now,
        )
    else:
        channel = request.get("channel")
        if channel not in ("print", "email"):
            raise OperationError("invalid_channel")
        req_id = request.get("request_id")
        if not isinstance(req_id, str) or not re.fullmatch(
            r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", req_id
        ):
            raise OperationError("invalid_request_id")
        if type(request.get("acknowledge_possible_duplicate")) is not bool:
            raise OperationError("explicit_reprint_consent_required")
        if request["acknowledge_possible_duplicate"] is not True:
            raise OperationError("explicit_reprint_consent_required")
        profile = request.get("print_profile", "a4-home")
        if profile not in ("a4-home", "a3-folded"):
            raise OperationError("invalid_print_profile")
        result = deliver_archived(
            settings, target_date=target_date, channel=channel,
            request_id=req_id, print_profile=profile,
            acknowledge_possible_duplicate=True,
        )
    payload = result.as_dict()
    return {
        "schema_version": 1,
        "action": action,
        "status": payload["status"],
        "outcome": payload,
        "physical_verified": False,
    }


def operate_file(settings: Settings, path: Path) -> dict[str, Any]:
    """Small owner-local JSON file; deliberately no inline shell/remote URL input."""
    try:
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 4096:
            raise OperationError("invalid_request_file")
        request = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise OperationError("invalid_request_file") from exc
    return operate_request(settings, request)
