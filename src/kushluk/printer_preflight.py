"""Bounded, read-only CUPS discovery for explicit local onboarding actions.

Never uses lp, lpr, driver installation, configuration changes, or print jobs.
No commands run merely because a page is opened.
"""
from __future__ import annotations

from dataclasses import dataclass
from html import escape
import re
import shutil
import subprocess

from kushluk.printing import detect_printer_capabilities


_QUEUE = re.compile(r"^[A-Za-z0-9_.-]{1,80}$")
_LINE = re.compile(r"^printer ([A-Za-z0-9_.-]{1,80}) is ", re.IGNORECASE)
_MAX_QUEUES = 20


@dataclass(frozen=True)
class PrinterInventory:
    status: str
    queues: tuple[str, ...]
    note: str


@dataclass(frozen=True)
class PrinterReadiness:
    name: str
    status: str
    a4: bool
    a3: bool
    duplex: bool
    note: str


def discover_queues() -> PrinterInventory:
    lpstat = shutil.which("lpstat")
    if not lpstat:
        return PrinterInventory("unavailable", (), "CUPS lpstat is not installed.")
    try:
        process = subprocess.run(
            [lpstat, "-p"], capture_output=True, text=True,
            check=False, timeout=6,
        )
    except (OSError, subprocess.TimeoutExpired):
        return PrinterInventory("unavailable", (), "Local printer listing did not complete.")
    if process.returncode != 0 or len(process.stdout) > 65536:
        return PrinterInventory("unavailable", (), "Local CUPS could not list printers.")
    names: list[str] = []
    for line in process.stdout.splitlines():
        match = _LINE.match(line)
        if match and match.group(1) not in names:
            names.append(match.group(1))
            if len(names) > _MAX_QUEUES:
                return PrinterInventory("unavailable", (), "Too many queues to review safely.")
    return PrinterInventory(
        "found" if names else "empty", tuple(names),
        "Choose a queue for a separate read-only check."
        if names else "No installed CUPS queues were reported.",
    )


def check_queue(name: str, inventory: PrinterInventory) -> PrinterReadiness:
    # A caller must scan first; never trust arbitrary destinations from a POST.
    if (not isinstance(name, str) or not _QUEUE.fullmatch(name)
            or not isinstance(inventory, PrinterInventory)
            or inventory.status != "found" or name not in inventory.queues):
        raise ValueError("Select a queue from the last local printer scan")
    capabilities = detect_printer_capabilities(name)
    options = tuple(value.lower() for value in capabilities.media_options)
    a4 = any(value == "a4" or value.startswith("iso_a4_") for value in options)
    a3 = any(value == "a3" or value.startswith("iso_a3_") for value in options)
    status = "reported-ready" if capabilities.available else "unconfirmed"
    return PrinterReadiness(
        name, status, a4, a3, capabilities.duplex_supported,
        "CUPS reports a usable queue. No paper has been printed or inspected."
        if capabilities.available
        else "Queue availability is not confirmed. Check CUPS and printer power.",
    )


def render_printer_review(
    inventory: PrinterInventory | None, readiness: PrinterReadiness | None,
    *, csrf: str, notice: str | None = None,
) -> str:
    banner = f'<p role="status">{escape(notice)}</p>' if notice else ""
    if inventory is None:
        listing = "<p>Nothing has been checked. Discover printers only when you choose.</p>"
    else:
        listing = '<p role="status">' + escape(inventory.note) + '</p>'
        for name in inventory.queues:
            label = escape(name, quote=True)
            listing += (
                '<section class="queue"><strong>' + label + '</strong>'
                '<form method="post" action="/printer/check">'
                f'<input type="hidden" name="csrf" value="{csrf}">'
                f'<input type="hidden" name="queue" value="{label}">'
                '<button type="submit">Check this queue</button></form></section>'
            )
    result = ""
    if readiness:
        result = (
            '<div class="status" role="status"><h2>' + escape(readiness.name)
            + '</h2><p>Queue: ' + escape(readiness.status)
            + '</p><p>A4 advertised: ' + ("yes" if readiness.a4 else "not confirmed")
            + ' · A3 advertised: ' + ("yes" if readiness.a3 else "not confirmed")
            + ' · Duplex advertised: '
            + ("yes" if readiness.duplex else "not confirmed")
            + '</p><p>' + escape(readiness.note) + '</p></div>'
        )
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>Kuşluk · Printer check</title><style>'
        ':root{font:17px/1.55 system-ui;color:#26382d;background:#f4f0e8}'
        'body{max-width:850px;margin:5vh auto;padding:20px}'
        'h1{font:normal clamp(35px,6vw,58px) Georgia,serif}'
        'h2{font:normal 26px Georgia,serif}'
        '.queue,.status{padding:18px;border:1px solid #ccd3c8;background:#fffefa;margin:10px 0}'
        'button{background:#24513a;color:#fff;border:0;padding:12px 16px;cursor:pointer}'
        'button:focus-visible,a:focus-visible{outline:3px solid #427c56;outline-offset:3px}'
        'a{color:#24513a}</style></head><body>'
        '<p>kuşluk. · 03 / 03 · Local only</p>'
        '<h1>Meet your printer.</h1>'
        '<p>Printer discovery is optional. This step asks your local CUPS system '
        'about installed queues and capabilities. It will never submit a print job, '
        'install a driver, modify a queue, or authorize unattended printing.</p>'
        + banner
        + '<form method="post" action="/printer/scan">'
        f'<input type="hidden" name="csrf" value="{csrf}">'
        '<button type="submit">Discover local printer queues</button></form>'
        + listing + result
        + '<p><strong>What this does not prove:</strong> that the printer is powered on, '
        'has paper, prints A4/A3 correctly, handles duplex alignment, or works after reboot. '
        'Complete a real hardware trial separately.</p>'
        '<p><a href="/sources">Previous: source permissions</a> · '
        '<a href="/">Home profile</a></p></body></html>'
    )
