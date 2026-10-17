"""Generate disabled, reviewable native scheduler files; never install or enable them."""
from __future__ import annotations

from datetime import time
import os
from pathlib import Path
import plistlib
import re


class ScheduleTemplateError(ValueError):
    """Fixed diagnostics that never repeat private user paths."""


def _safe_exec(path: Path) -> str:
    if not path.is_absolute() or not re.fullmatch(r"[A-Za-z0-9_./+\-]+", str(path)):
        raise ScheduleTemplateError("absolute_executable_path_required")
    return str(path)


def _safe_dir(path: Path, *, systemd: bool) -> str:
    if not path.is_absolute() or ".." in path.parts:
        raise ScheduleTemplateError("absolute_workdir_required")
    if systemd and not re.fullmatch(r"[A-Za-z0-9_./+\-]+", str(path)):
        raise ScheduleTemplateError("systemd_workdir_contains_unsupported_characters")
    return str(path)


def _parse_clock(value: str) -> time:
    if not isinstance(value, str) or not re.fullmatch(
        r"(?:[01]\d|2[0-3]):[0-5]\d", value
    ):
        raise ScheduleTemplateError("clock_must_be_HH_MM")
    return time.fromisoformat(value)


def templates(
    *, platform: str, executable: Path, working_dir: Path,
    start: str, latest_start: str,
) -> dict[str, str]:
    """Render native OS units in memory. Not even an executable is launched."""
    if platform not in {"systemd", "launchd"}:
        raise ScheduleTemplateError("unsupported_platform")
    exec_path = _safe_exec(executable)
    workdir = _safe_dir(working_dir, systemd=platform == "systemd")
    start_time = _parse_clock(start)
    cutoff_time = _parse_clock(latest_start)
    if start_time >= cutoff_time:
        raise ScheduleTemplateError("start_must_precede_latest_start")
    h, m = start_time.hour, start_time.minute

    if platform == "systemd":
        service = (
            "[Unit]\n"
            "Description=Generate the local Kushluk morning edition\n"
            "Documentation=https://github.com/interzettel/kushluk\n"
            "\n[Service]\n"
            "Type=oneshot\n"
            f"WorkingDirectory={workdir}\n"
            f"ExecStart={exec_path} run --latest-start {latest_start}\n"
            "UMask=0077\n"
            "NoNewPrivileges=true\n"
            "\n[Install]\n"
            "WantedBy=default.target\n"
        )
        timer = (
            "[Unit]\n"
            "Description=Run local Kushluk edition every morning\n"
            "\n[Timer]\n"
            f"OnCalendar=*-*-* {h:02d}:{m:02d}:00\n"
            "Persistent=true\n"
            "AccuracySec=1min\n"
            "Unit=kushluk.service\n"
            "\n[Install]\n"
            "WantedBy=timers.target\n"
        )
        return {"kushluk.service": service, "kushluk.timer": timer}

    # launchd runs in the logged-in user's session, not a persistent headless host.
    # Explicit argument array (not a shell command) prevents quoting/injection.
    plist = {
        "Label": "org.interzettel.kushluk.morning",
        "ProgramArguments": [exec_path, "run", "--latest-start", latest_start],
        "WorkingDirectory": workdir,
        "StartCalendarInterval": {"Hour": h, "Minute": m},
        "RunAtLoad": False,
        "StandardOutPath": str(working_dir / "kushluk-scheduler.stdout.log"),
        "StandardErrorPath": str(working_dir / "kushluk-scheduler.stderr.log"),
    }
    return {
        "org.interzettel.kushluk.morning.plist":
            plistlib.dumps(plist, sort_keys=True).decode("utf-8")
    }


def export_templates(
    *, platform: str, executable: Path, working_dir: Path, output_dir: Path,
    start: str, latest_start: str,
) -> list[str]:
    """Write create-only 0600 files; do not call systemctl, launchctl or CUPS."""
    rendered = templates(
        platform=platform, executable=executable, working_dir=working_dir,
        start=start, latest_start=latest_start,
    )
    if not output_dir.is_absolute() or ".." in output_dir.parts or output_dir.is_symlink():
        raise ScheduleTemplateError("absolute_output_dir_required")
    try:
        output_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    except OSError as exc:
        raise ScheduleTemplateError("output_directory_unavailable") from exc
    if any((output_dir / name).exists() or (output_dir / name).is_symlink()
           for name in rendered):
        raise ScheduleTemplateError("schedule_files_exist")
    created = []
    try:
        for name, body in rendered.items():
            path = output_dir / name
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            created.append(path)
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                stream.write(body)
                stream.flush()
                os.fsync(stream.fileno())
        return sorted(rendered)
    except OSError as exc:
        for path in created:
            path.unlink(missing_ok=True)
        raise ScheduleTemplateError("schedule_export_failed") from exc
