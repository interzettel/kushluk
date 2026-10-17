"""Explicit, on-device best-effort incident notification; never a delivery guarantee.

This never installs a daemon or contacts an external API. Only a directly
requested invocation may call the OS notification tool; failures stay local.
"""
from __future__ import annotations

from datetime import date
import json
import os
import platform
import shutil
import stat
import subprocess

try:
    import fcntl
except ImportError:  # Unsupported non-POSIX hosts fail closed on send.
    fcntl = None

from kushluk.config import Settings
from kushluk.incident import build_incident_report

# Both arguments are fixed strings selected by an internal code allowlist.
TITLE = "Kuşluk needs attention"
NOTICES = {
    "manual_review_no_auto_retry": "A morning run needs review. Check local status before retrying.",
    "delivery_needs_attention": "Edition delivery needs review. Check printer or mail queue.",
    "status_requires_review": "A morning run needs inspection. Open Kuşluk run status.",
}
# No third-party string, folder name, printer ID or private text reaches these.
RESULT_BASE = {"notification_display_verified": False, "paper_verified": False,
               "remote_diagnostics_sent": False, "delivery_retried": False}


def _backend(system: str) -> tuple[str, list[str]] | None:
    if system == "Darwin":
        exe = shutil.which("osascript")
        if exe:
            # AppleScript is a fixed literal expression, never user interpolation.
            command = 'display notification "A morning run needs review. Open Kushluk status." with title "Kushluk"'
            return ("macos_notification_center", [exe, "-e", command])
    elif system == "Linux":
        exe = shutil.which("notify-send")
        if exe:
            return ("freedesktop_notifications", [
                exe, "--app-name=Kushluk", "--urgency=normal",
                "--expire-time=10000", TITLE, "A morning run needs review. Open Kushluk status.",
            ])
    return None


def notify_local(
    settings: Settings, *, target_date: date, send: bool = False,
    system: str | None = None,
) -> dict:
    """Preview by default; explicit OS send only for failed incidents, once per ID.

    The OS tool's success proves only process submission, never that a desktop
    session displayed a banner or a person saw it.
    """
    event = build_incident_report(settings, target_date=target_date)
    code = event["error_code"]
    eligible = (event["user_notification_required"] is True
                and event["severity"] == "failed")
    base = {
        "schema_version": 1, "kind": "local_notification_attempt",
        "edition_id": event["edition_id"], "incident_id": event["incident_id"],
        "error_code": code, "notification_required": eligible,
        "notification_sent_to_os": False, "os_backend": None,
        **RESULT_BASE,
    }
    if not eligible:
        return {**base, "status": "not_required"}
    if not send:
        return {**base, "status": "preview_only", "send_requested": False}

    chosen = _backend(system or platform.system())
    if chosen is None or fcntl is None:
        return {**base, "status": "os_backend_unavailable", "send_requested": True}
    kind, args = chosen
    base["os_backend"] = kind

    # Never create an archive or marker for a read-only preview. The run must
    # already have created a real dated directory before a send is attempted.
    parent = settings.archive_dir / event["edition_id"]
    if settings.archive_dir.is_symlink() or parent.is_symlink() or not parent.is_dir():
        return {**base, "status": "unsafe_or_missing_archive"}
    if not stat.S_ISDIR(parent.lstat().st_mode):
        return {**base, "status": "unsafe_or_missing_archive"}
    marker = parent / (".notification-" + event["incident_id"] + ".json")
    lock = parent / ".kushluk-notification.lock"
    fd = None
    try:
        flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(lock, flags, 0o600)
        meta = os.fstat(fd)
        if not stat.S_ISREG(meta.st_mode) or meta.st_mode & 0o077:
            return {**base, "status": "unsafe_notification_lock"}
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return {**base, "status": "another_notification_active"}
        if marker.is_symlink():
            return {**base, "status": "unsafe_notification_marker"}
        if marker.exists():
            return {**base, "status": "already_submitted"}
        # Claim the incident BEFORE OS submission. A crash after the OS call
        # must not trigger an automatic duplicate on the next invocation.
        receipt = {
            "schema_version": 1, "incident_id": event["incident_id"],
            "edition_id": event["edition_id"], "backend": kind,
            "os_submission_state": "uncertain",
            "display_or_human_read_confirmed": False,
        }
        create_flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        try:
            marker_fd = os.open(marker, create_flags, 0o600)
        except FileExistsError:
            return {**base, "status": "already_submitted"}
        with os.fdopen(marker_fd, "w", encoding="utf-8") as handle:
            json.dump(receipt, handle, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        try:
            # No shell, URL, private message, unbounded output or retries.
            completed = subprocess.run(
                args, capture_output=True, text=True, timeout=5, check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            return {**base, "status": "os_submission_uncertain_no_auto_retry"}
        if completed.returncode != 0:
            return {**base, "status": "os_submission_uncertain_no_auto_retry"}
        # The backend accepted the request. Receipt was already claimed,
        # so process death remains duplicate-safe; update without rewinding.
        receipt["os_submission_state"] = "accepted_not_display_verified"
        tmp_path = parent / (".notification-update-" + event["incident_id"])
        try:
            temp_fd = os.open(tmp_path, create_flags, 0o600)
            with os.fdopen(temp_fd, "w", encoding="utf-8") as handle:
                json.dump(receipt, handle, sort_keys=True)
                handle.write("\\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(tmp_path, marker)
        except OSError:
            return {**base, "status": "os_submitted_receipt_unavailable",
                    "notification_sent_to_os": True}
        finally:
            tmp_path.unlink(missing_ok=True)
        return {**base, "status": "submitted_to_os_not_verified",
                "notification_sent_to_os": True}
    except OSError:
        return {**base, "status": "os_submission_unavailable"}
    finally:
        if fd is not None:
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
            except OSError:
                pass
            os.close(fd)
