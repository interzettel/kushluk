from __future__ import annotations

import importlib
import importlib.util
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from kushluk.config import Settings
from kushluk.printing import detect_printer_capabilities


CheckStatus = Literal["ready", "optional", "missing"]


@dataclass(slots=True)
class HealthCheck:
    name: str
    status: CheckStatus
    detail: str


def run_doctor(settings: Settings) -> list[HealthCheck]:
    checks = [
        HealthCheck(
            "python",
            "ready" if sys.version_info >= (3, 11) else "missing",
            f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        ),
        _directory_check("output", settings.output_dir),
        _directory_check("archive", settings.archive_dir),
        _calendar_check(settings),
        _pdf_check(),
        _printer_check(settings),
        HealthCheck(
            "email",
            "ready" if settings.email_configured else "optional",
            "SMTP delivery configured."
            if settings.email_configured
            else "SMTP not configured; email delivery remains disabled.",
        ),
    ]
    return checks


def core_ready(checks: list[HealthCheck]) -> bool:
    core_names = {"python", "output", "archive", "calendar"}
    return all(check.status != "missing" for check in checks if check.name in core_names)


def _directory_check(name: str, path: Path) -> HealthCheck:
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".kushluk-write-test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
    except OSError as exc:
        return HealthCheck(name, "missing", f"{path}: {exc}")
    return HealthCheck(name, "ready", str(path))


def _calendar_check(settings: Settings) -> HealthCheck:
    if settings.calendar_ics:
        return HealthCheck("calendar", "ready", "ICS calendar source configured.")
    if settings.calendar_fixture.exists():
        return HealthCheck(
            "calendar",
            "ready",
            f"Stage 1 fixture active: {settings.calendar_fixture}",
        )
    return HealthCheck(
        "calendar",
        "missing",
        "No ICS source configured and calendar fixture is unavailable.",
    )


def _pdf_check() -> HealthCheck:
    has_weasy = importlib.util.find_spec("weasyprint") is not None
    has_pypdf = importlib.util.find_spec("pypdf") is not None
    if has_weasy and has_pypdf:
        try:
            # A distribution can be installed while its native Pango libraries are missing.
            # Importing the renderer detects this common macOS setup failure.
            importlib.import_module("weasyprint")
            importlib.import_module("pypdf")
        except (ImportError, OSError) as exc:
            return HealthCheck(
                "pdf",
                "optional",
                f"PDF libraries installed but unusable: {type(exc).__name__}: {exc}. "
                "On macOS, install Homebrew Pango and check DYLD_FALLBACK_LIBRARY_PATH.",
            )
        return HealthCheck("pdf", "ready", "WeasyPrint + pypdf available.")
    return HealthCheck(
        "pdf",
        "optional",
        "Install the pdf extra to enable validated PDF output: pip install -e '.[pdf]'",
    )


def _printer_check(settings: Settings) -> HealthCheck:
    if not shutil.which("lp"):
        return HealthCheck(
            "printer",
            "optional",
            "CUPS lp is unavailable; generation still works without printing.",
        )
    capabilities = detect_printer_capabilities(settings.printer)
    if capabilities.printer:
        duplex = "duplex" if capabilities.duplex_supported else "simplex/unknown duplex"
        return HealthCheck(
            "printer",
            "ready" if capabilities.available else "optional",
            f"{capabilities.printer}: {capabilities.detail} ({duplex})",
        )
    return HealthCheck("printer", "optional", capabilities.detail)
