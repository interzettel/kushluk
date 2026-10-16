from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class PrinterCapabilities:
    printer: str | None
    available: bool
    duplex_supported: bool
    media_options: tuple[str, ...]
    detail: str


@dataclass(slots=True)
class PrintResult:
    attempted: bool
    success: bool
    detail: str
    printer: str | None = None
    duplex_used: bool = False


def detect_printer_capabilities(printer: str | None = None) -> PrinterCapabilities:
    lpoptions = shutil.which("lpoptions")
    lpstat = shutil.which("lpstat")
    resolved = _preferred_printer(printer, lpstat)
    if not resolved:
        return PrinterCapabilities(None, False, False, (), "No configured default printer.")
    if not lpoptions:
        return PrinterCapabilities(
            resolved, False, False, (), "CUPS 'lpoptions' command is not available."
        )

    try:
        completed = subprocess.run(
            [lpoptions, "-p", resolved, "-l"],
            capture_output=True,
            text=True,
            check=False,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return PrinterCapabilities(
            resolved, False, False, (), f"CUPS query failed: {type(exc).__name__}: {exc}"
        )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or "Unable to query printer capabilities."
        return PrinterCapabilities(resolved, False, False, (), detail)

    duplex, media = parse_lpoptions(completed.stdout)
    available = _printer_available(lpstat, resolved)
    detail = "Printer ready." if available else "Printer configured; live state unavailable/offline."
    return PrinterCapabilities(resolved, available, duplex, media, detail)


def parse_lpoptions(text: str) -> tuple[bool, tuple[str, ...]]:
    duplex = False
    media: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        lower = line.lower()
        if lower.startswith("duplex/") or lower.startswith("sides/"):
            values = line.split(":", 1)[-1].split()
            duplex = any(
                value.lstrip("*").lower()
                in {
                    "duplexnotumble",
                    "duplextumble",
                    "two-sided-long-edge",
                    "two-sided-short-edge",
                }
                for value in values
            )
        if lower.startswith(("pagesize/", "media/", "mediasize/")):
            values = line.split(":", 1)[-1].split()
            media.extend(value.lstrip("*") for value in values)
    return duplex, tuple(dict.fromkeys(media))


def print_pdf(
    pdf_path: Path,
    printer: str | None = None,
    *,
    execute: bool = False,
    duplex: bool = True,
    media: str = "A4",
    duplex_edge: str = "long",
    require_duplex: bool = False,
) -> PrintResult:
    if not execute:
        return PrintResult(False, True, "Print skipped (dry-run). Use --print to submit the job.")
    if not pdf_path.exists():
        return PrintResult(True, False, f"PDF not found: {pdf_path}", printer=printer)

    lp = shutil.which("lp")
    if not lp:
        return PrintResult(True, False, "CUPS 'lp' command is not available.", printer=printer)

    capabilities = detect_printer_capabilities(printer)
    resolved = capabilities.printer or printer
    if media not in {"A4", "A3"} or duplex_edge not in {"long", "short"}:
        return PrintResult(True, False, "Unsupported print media or duplex edge.", printer=resolved)
    if require_duplex and not capabilities.duplex_supported:
        return PrintResult(
            True, False, "Selected print profile needs a confirmed duplex-capable printer.",
            printer=resolved,
        )
    if media == "A3":
        if not capabilities.available:
            return PrintResult(True, False, "A3 printer is unavailable or offline.", printer=resolved)
        if not any("a3" in value.lower() for value in capabilities.media_options):
            return PrintResult(
                True, False,
                "Printer does not advertise A3 media; refusing unverified A3 submission.",
                printer=resolved,
            )
    command = [lp]
    if resolved:
        command += ["-d", resolved]
    command += ["-o", f"media={media}"]

    duplex_used = bool(duplex and capabilities.duplex_supported)
    # Explicit simplex avoids inheriting a conflicting user-default duplex setting.
    command += ["-o", f"sides=two-sided-{duplex_edge}-edge" if duplex_used else "sides=one-sided"]

    command.append(str(pdf_path))
    try:
        completed = subprocess.run(
            command, capture_output=True, text=True, check=False, timeout=30
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return PrintResult(
            True,
            False,
            f"CUPS print submission failed: {type(exc).__name__}: {exc}",
            printer=resolved,
            duplex_used=duplex_used,
        )
    if completed.returncode == 0:
        return PrintResult(
            True,
            True,
            completed.stdout.strip() or "Print job submitted.",
            printer=resolved,
            duplex_used=duplex_used,
        )
    return PrintResult(
        True,
        False,
        completed.stderr.strip() or "Print submission failed.",
        printer=resolved,
        duplex_used=duplex_used,
    )


def _preferred_printer(printer: str | None, lpstat: str | None) -> str | None:
    # Same precedence as CUPS: explicit Kushluk destination, LPDEST, PRINTER,
    # then the system/user's lpstat default (works on Linux and macOS).
    for candidate in (printer, os.getenv("LPDEST"), os.getenv("PRINTER")):
        if candidate and candidate.strip():
            return candidate.strip()
    return _default_printer(lpstat)


def _default_printer(lpstat: str | None) -> str | None:
    if not lpstat:
        return None
    try:
        completed = subprocess.run(
            [lpstat, "-d"], capture_output=True, text=True, check=False, timeout=15
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if completed.returncode != 0:
        return None
    text = completed.stdout.strip()
    if ":" not in text:
        return None
    return text.split(":", 1)[1].strip() or None


def _printer_available(lpstat: str | None, printer: str) -> bool:
    if not lpstat:
        return False
    try:
        completed = subprocess.run(
            [lpstat, "-p", printer],
            capture_output=True,
            text=True,
            check=False,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    if completed.returncode != 0:
        return False
    lowered = completed.stdout.lower()
    return "disabled" not in lowered and ("idle" in lowered or "enabled" in lowered)
