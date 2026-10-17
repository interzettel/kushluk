"""Minimal local-only setup browser, no API, cookies, analytics or public listener.

One form writes the exact same create-only private profile as `kushluk setup`.
Source rights, paid accounts, print jobs and scheduler controls are out of scope.
"""
from __future__ import annotations

from hmac import compare_digest
from http.server import BaseHTTPRequestHandler, HTTPServer
import secrets
from pathlib import Path
from urllib.parse import parse_qs
import webbrowser

from kushluk.local_profile import (
    LocalProfileError, profile_path, read_local_profile,
    update_local_printer, update_local_paper_size, write_local_profile,
)
from kushluk.opml import OPMLImportError
from kushluk.printer_preflight import (
    check_queue, discover_queues, render_printer_review,
)
from kushluk.setup_sources_web import (
    approve_reviewed, change_reviewed_mode, import_review_opml, render_source_review,
)
from kushluk.source_registry import SourceApprovalError, registry_path

_FORM = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Kushluk — Set up your morning</title>
<style>
:root{color-scheme:light;font-family:system-ui,-apple-system,sans-serif;background:#f4f0e8;color:#252b26}
*{box-sizing:border-box}body{margin:0;min-height:100vh}\n.skip{position:absolute;left:1rem;top:-10rem;padding:.7rem 1rem;background:#fffefa;color:#244f3b;z-index:10}\n.skip:focus{top:1rem}
.shell{max-width:1080px;margin:0 auto;padding:48px 26px}
.eyebrow{font-size:12px;letter-spacing:.16em;text-transform:uppercase;font-weight:700;color:#596b59}
header{border-bottom:1px solid #c2c5b7;padding-bottom:22px;display:flex;justify-content:space-between;gap:20px}
.brand{font-family:Georgia,serif;font-weight:700;font-size:24px;letter-spacing:-.04em}
main{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:8%;padding-top:72px}
h1{font:normal clamp(38px,5.4vw,72px)/1.04 Georgia,serif;letter-spacing:-.055em;margin:14px 0 26px}
.intro{font-size:17px;line-height:1.65;color:#4b554a;max-width:440px}
aside{margin-top:48px;padding-top:24px;border-top:1px solid #c2c5b7;font-size:14px;line-height:1.8;color:#536052}
.panel{background:#fffefa;border:1px solid #d8d8cb;padding:36px;box-shadow:0 12px 36px #353f3210}
h2{font:normal 26px Georgia,serif;margin:0 0 10px}
.note{font-size:13px;color:#647063;line-height:1.6;margin-bottom:24px}
label{display:block;font-size:13px;font-weight:650;margin:20px 0 7px}
input,select{width:100%;border:1px solid #bdc4b9;background:#fff;padding:12px 13px;border-radius:2px;font:inherit}
input:focus-visible,select:focus-visible,button:focus-visible,a:focus-visible{outline:3px solid #367554;outline-offset:2px}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:16px}
button{margin-top:30px;background:#244f3b;color:#fff;border:0;border-radius:2px;padding:14px 24px;font-weight:700;cursor:pointer;width:100%;font:inherit}
button:hover{background:#316a4c}
.small{font-size:12px;color:#677166;line-height:1.6}
footer{border-top:1px solid #c2c5b7;margin-top:86px;padding-top:20px;font-size:12px;color:#627162}
@media(max-width:760px){main{grid-template-columns:1fr;gap:36px;padding-top:36px}.shell{padding:24px 18px}.panel{padding:23px}aside{margin-top:20px}.pair{gap:10px}}
</style>
</head><body><a class="skip" href="#setup-form">Skip to setup form</a><div class="shell">
<header><span class="brand">kushluk.</span><span class="eyebrow">Your local morning paper · 01 / 03</span></header>
<main>
<div><p class="eyebrow">Your home, your sources</p>
<h1>A quieter way to start the day.</h1>
<p class="intro">A personal newspaper, prepared on your own computer. Set your approximate location and timezone for the daily edition. You stay in control of sources and delivery.</p>
<aside><strong>What this step does</strong><br>Creates one private profile on this computer. No accounts, subscriptions, printer jobs or source permissions are changed.<br><br><strong>Next</strong><br>Review your sources, then test a printer separately. Nothing runs unattended until you configure it.</aside>
</div>
<div class="panel"><h2>Make it yours</h2>
<p class="note" id="location-help">Use an approximate city-center location; a street address is not required. All fields stay on this device.</p>
<form id="setup-form" method="post" action="/" autocomplete="off" aria-label="Local home profile setup">
<input type="hidden" name="csrf" value="__TOKEN__">
<label for="home_name">Name of your home</label>
<input id="home_name" name="home_name" required maxlength="120" placeholder="e.g. My Morning" autocomplete="off">
<div class="pair">
<div><label for="latitude">Approximate latitude</label><input id="latitude" type="number" step="any" min="-90" max="90" name="latitude" required aria-describedby="location-help" placeholder="50.9"></div>
<div><label for="longitude">Approximate longitude</label><input id="longitude" type="number" step="any" min="-180" max="180" name="longitude" required aria-describedby="location-help" placeholder="6.9"></div>
</div>
<label for="timezone">Time zone (region/city)</label>
<input id="timezone" name="timezone" required maxlength="100" aria-describedby="timezone-help" placeholder="e.g. Europe/Berlin" spellcheck="false"><p class="small" id="timezone-help">Enter a time zone such as Europe/Berlin, not only GMT+2. This keeps your edition time correct when clocks change.</p>
<label for="paper_size">Preferred home paper format</label>
<select id="paper_size" name="paper_size" required aria-describedby="paper-help">
<option value="a4" selected>DIN A4 — 210 × 297 mm</option>
<option value="letter">US Letter — 8.5 × 11 in (216 × 279 mm)</option>
</select>
<p class="small" id="paper-help">Choose the paper you actually keep at home. A4 is the default for existing profiles; you can change this later. Selecting a format never starts printing.</p>
<p class="small">Your printer comes later. Step 3 lets you discover and check an installed queue before saving it.</p>
<button type="submit">Save my local profile</button>
<p class="small">After saving, your profile stays on this computer. No feed activation, printing, telemetry or background services.</p>
</form></div></main>
<footer>Local-first · Reference-only sources · Your morning, not another account.</footer>
</div></body></html>"""

_DONE = """<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Kushluk — Saved locally</title>
<style>body{font:17px/1.65 system-ui;background:#f4f0e8;color:#25372c;
max-width:600px;margin:12vh auto;padding:25px}
h1{font:normal 54px/1.1 Georgia,serif}a{color:#244f3b}</style>
<h1>You're ready for the next step.</h1>
<p>Your personal preferences are saved in a private file on this computer.
No sources were enabled and no paper was printed.</p>
<p><a href="/sources">Review and approve your reading sources</a> in the next local step,
or use <code>kushluk doctor</code> to inspect runtime readiness.</p>
<p>No release or physical-printer verification is implied.</p></html>"""


class SetupHTTPServer(HTTPServer):
    """Always loopback, with a per-instance CSRF token and no external routes."""

    def __init__(self, path: Path, port: int = 0, *, registry: Path | None = None):
        self.profile_file = path
        self.registry_file = registry if registry is not None else registry_path()
        self.pending_feeds = ()  # Ephemeral, unapproved, never written to disk.
        self.printer_inventory = None
        self.printer_readiness = None
        self.csrf = secrets.token_urlsafe(32)
        super().__init__(("127.0.0.1", port), SetupHandler)

    @property
    def origin(self) -> str:
        return f"http://127.0.0.1:{self.server_port}"


class SetupHandler(BaseHTTPRequestHandler):
    server: SetupHTTPServer

    def log_message(self, _format: str, *_args: object) -> None:
        # Suppress request paths/headers: they could contain local private data.
        pass

    def _reply(self, status: int, html: str) -> None:
        payload = html.encode("utf-8")
        self.send_response(status)
        for key, value in {
            "Content-Type": "text/html; charset=utf-8",
            "Content-Length": str(len(payload)),
            "Cache-Control": "no-store, max-age=0",
            "Pragma": "no-cache",
            "Referrer-Policy": "no-referrer",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Content-Security-Policy": (
                "default-src 'none'; style-src 'unsafe-inline'; "
                "form-action 'self'; base-uri 'none'; frame-ancestors 'none'"
            ),
        }.items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(payload)

    def _valid_request(self) -> bool:
        return (
            self.client_address[0] == "127.0.0.1"
            and self.headers.get("Host") == f"127.0.0.1:{self.server.server_port}"
            and self.path in {
                "/", "/sources", "/sources/import", "/sources/approve", "/sources/mode",
                "/printer", "/printer/scan", "/printer/check", "/printer/save",
            }
        )

    def do_GET(self) -> None:
        if not self._valid_request() or self.path not in {"/", "/sources", "/printer"}:
            self._reply(404, "<h1>Not found</h1>")
            return
        if self.path == "/printer":
            try:
                profile = read_local_profile(self.server.profile_file)
            except LocalProfileError:
                profile = {}
            page = render_printer_review(
                self.server.printer_inventory, self.server.printer_readiness,
                csrf=self.server.csrf, saved_queue=profile.get("printer"),
                profile_exists=bool(profile), paper_size=profile.get("paper_size", "a4"),
            )
            self._reply(200, page)
            return
        if self.path == "/sources":
            try:
                page = render_source_review(
                    self.server.pending_feeds, path=self.server.registry_file,
                    csrf=self.server.csrf,
                )
            except SourceApprovalError:
                self._reply(422, "<h1>Cannot read the private source registry</h1>")
                return
            self._reply(200, page)
            return
        if self.server.profile_file.exists() or self.server.profile_file.is_symlink():
            self._reply(409, "<h1>Profile already exists</h1>"
                        "<p>This setup page never overwrites your local preferences. <a href=\'/sources\'>Continue to source review</a>.</p>")
            return
        self._reply(200, _FORM.replace("__TOKEN__", self.server.csrf))

    def do_POST(self) -> None:
        if not self._valid_request():
            self._reply(404, "<h1>Not found</h1>")
            return
        if (self.headers.get("Origin") != self.server.origin
                or self.headers.get("Sec-Fetch-Site", "same-origin") != "same-origin"):
            self._reply(403, "<h1>Cross-site submission rejected</h1>")
            return
        if self.headers.get("Content-Type") != "application/x-www-form-urlencoded":
            self._reply(415, "<h1>Unsupported form encoding</h1>")
            return
        try:
            length = int(self.headers.get("Content-Length", "-1"))
        except ValueError:
            length = -1
        max_length = 131_072 if self.path == "/sources/import" else 4096
        if length <= 0 or length > max_length:
            self._reply(413, "<h1>Invalid form size</h1>")
            return
        body = self.rfile.read(length)
        try:
            fields = parse_qs(body.decode("utf-8", errors="strict"),
                              keep_blank_values=True, strict_parsing=True,
                              max_num_fields=6)
        except (UnicodeError, ValueError):
            self._reply(400, "<h1>Invalid form</h1>")
            return
        expected_fields = {
            "/": {"csrf", "home_name", "latitude", "longitude", "timezone", "paper_size"},
            "/paper/save": {"csrf", "paper_size"},
            "/sources/import": {"csrf", "opml"},
            "/sources/approve": {"csrf", "index", "consent"},
            "/sources/mode": {"csrf", "id", "mode"},
            "/printer/scan": {"csrf"},
            "/printer/check": {"csrf", "queue"},
            "/printer/save": {"csrf", "queue", "consent"},
        }
        if self.path == "/sources/mode" and "consent" in fields:
            expected_fields["/sources/mode"].add("consent")
        expected = expected_fields.get(self.path)
        if expected is None:
            self._reply(404, "<h1>Not found</h1>")
            return
        if set(fields) != expected or any(len(vals) != 1 for vals in fields.values()):
            self._reply(400, "<h1>Form fields do not match</h1>")
            return
        if (not fields["csrf"][0].isascii()
                or not compare_digest(fields["csrf"][0], self.server.csrf)):
            self._reply(403, "<h1>Expired or invalid form</h1>")
            return
        if self.path == "/paper/save":
            try:
                update_local_paper_size(self.server.profile_file,
                                        paper_size=fields["paper_size"][0])
                profile = read_local_profile(self.server.profile_file)
            except (LocalProfileError, OSError):
                self._reply(422, "<h1>Paper preference not saved</h1>"
                            "<p>Create a local profile and choose A4 or Letter.</p>")
                return
            self._reply(200, render_printer_review(
                self.server.printer_inventory, self.server.printer_readiness,
                csrf=self.server.csrf,
                notice="Paper preference saved locally. Nothing has been printed.",
                saved_queue=profile.get("printer"), profile_exists=True,
                paper_size=profile["paper_size"],
            ))
            return
        if self.path.startswith("/printer/"):
            if self.path == "/printer/scan":
                self.server.printer_inventory = discover_queues()
                self.server.printer_readiness = None
                notice = "Local queue discovery completed; no print job sent."
            elif self.path == "/printer/check":
                # Enforce explicit discovery before invoking any capability checker.
                if (self.server.printer_inventory is None
                        or fields["queue"][0] not in self.server.printer_inventory.queues):
                    self._reply(422, "<h1>Printer was not selected from the scan</h1>")
                    return
                try:
                    self.server.printer_readiness = check_queue(
                        fields["queue"][0], self.server.printer_inventory,
                    )
                except ValueError:
                    self._reply(422, "<h1>Printer was not selected from the scan</h1>")
                    return
                notice = "Read-only capability check completed; nothing printed."
            else:
                # No unscanned, unchecked, stale or unconsented queue may persist.
                queue = fields["queue"][0]
                if (fields["consent"][0] != "yes"
                        or self.server.printer_inventory is None
                        or self.server.printer_inventory.status != "found"
                        or queue not in self.server.printer_inventory.queues
                        or self.server.printer_readiness is None
                        or self.server.printer_readiness.name != queue):
                    self._reply(422, "<h1>Check the printer and confirm before saving</h1>")
                    return
                try:
                    update_local_printer(self.server.profile_file, printer=queue)
                    profile = read_local_profile(self.server.profile_file)
                except (LocalProfileError, OSError):
                    self._reply(422, "<h1>Printer preference not saved</h1>"
                                "<p>Create a private profile first or check its permissions.</p>")
                    return
                notice = "Printer preference saved locally. No printing has been enabled."
            if self.path != "/printer/save":
                try:
                    profile = read_local_profile(self.server.profile_file)
                except LocalProfileError:
                    profile = {}
            self._reply(200, render_printer_review(
                self.server.printer_inventory, self.server.printer_readiness,
                csrf=self.server.csrf, notice=notice,
                saved_queue=profile.get("printer"), profile_exists=bool(profile),
                paper_size=profile.get("paper_size", "a4"),
            ))
            return
        if self.path.startswith("/sources/"):
            try:
                if self.path == "/sources/import":
                    self.server.pending_feeds = import_review_opml(fields["opml"][0])
                    notice = (
                        f"{len(self.server.pending_feeds)} feeds proposed for review. "
                        "None was approved or contacted."
                    )
                elif self.path == "/sources/approve":
                    created = approve_reviewed(
                        self.server.pending_feeds, fields["index"][0],
                        consent=fields["consent"][0] == "yes",
                        path=self.server.registry_file,
                    )
                    notice = (
                        "One source approved for reference-only access."
                        if created else "That source was already approved."
                    )
                else:
                    action = fields["mode"][0]
                    change_reviewed_mode(
                        fields["id"][0], action,
                        consent=fields.get("consent") == ["yes"],
                        path=self.server.registry_file,
                    )
                    notice = (
                        "One feed paused." if action == "ignore"
                        else "One feed resumed for reference-only access."
                    )
                page = render_source_review(
                    self.server.pending_feeds, path=self.server.registry_file,
                    csrf=self.server.csrf, notice=notice,
                )
            except (OPMLImportError, SourceApprovalError):
                self._reply(422, "<h1>Source review not changed</h1>"
                            "<p>Invalid proposal, selection or missing permission. "
                            "No source was silently activated.</p>")
                return
            self._reply(200, page)
            return
        try:
            write_local_profile(
                self.server.profile_file,
                home_name=fields["home_name"][0],
                latitude=float(fields["latitude"][0]),
                longitude=float(fields["longitude"][0]),
                timezone=fields["timezone"][0],
                paper_size=fields["paper_size"][0], printer=None,
            )
        except (LocalProfileError, ValueError, OSError):
            self._reply(422, "<h1>Could not save profile</h1>"
                        "<p>Check the coordinates and IANA timezone, "
                        "and confirm a profile does not already exist.</p>")
            return
        self._reply(201, _DONE)


def run_setup_web(*, path: Path | None = None, open_browser: bool = True) -> None:
    """Serve a manual one-session setup page on numeric IPv4 loopback only."""
    server = SetupHTTPServer(path or profile_path())
    try:
        print(f"Local setup: {server.origin}/", flush=True)
        print("No cloud service. Close with Ctrl+C.", flush=True)
        if open_browser:
            webbrowser.open(f"{server.origin}/")
        try:
            server.serve_forever(poll_interval=0.2)
        except KeyboardInterrupt:
            pass
    finally:
        server.server_close()
