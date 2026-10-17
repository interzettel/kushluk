"""Synthetic full U1-U6 browser contract: NOT a human usability observation.

Exercises real loopback HTTP and private temporary files. CUPS discovery is faked,
all input is synthetic, and no print job, network feed access or scheduler runs.
"""
from __future__ import annotations

import re
import socket
from http.client import HTTPConnection
from threading import Thread
from urllib.parse import urlencode

import pytest

from kushluk.local_profile import read_local_profile
from kushluk.printer_preflight import PrinterInventory, PrinterReadiness
from kushluk.setup_web import SetupHTTPServer
from kushluk.source_registry import read_registry


@pytest.fixture
def browser(tmp_path):
    server = SetupHTTPServer(tmp_path / "private" / "profile.json",
                             registry=tmp_path / "private" / "sources.json")
    worker = Thread(target=server.serve_forever,
                    kwargs={"poll_interval": 0.01}, daemon=True)
    worker.start()
    try:
        yield server, tmp_path
    finally:
        server.shutdown()
        worker.join(timeout=3)
        server.server_close()


def request(server, path="/", fields=None, *, origin=None):
    method = "POST" if fields is not None else "GET"
    body = urlencode(fields).encode("utf-8") if fields is not None else None
    headers = {}
    if body is not None:
        headers = {
            "Origin": origin or server.origin,
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": str(len(body)),
        }
    conn = HTTPConnection("127.0.0.1", server.server_port, timeout=4)
    try:
        conn.request(method, path, body=body, headers=headers)
        response = conn.getresponse()
        return response.status, response.read().decode("utf-8")
    finally:
        conn.close()


def csrf(html):
    match = re.search(r'name="csrf" value="([^"]+)"', html)
    assert match is not None
    return match.group(1)


OPML = (
    '<opml version="2.0"><body>'
    '<outline text="Trusted &amp; useful" xmlUrl="https://reader.example.org/rss"/>'
    '<outline text="Untrusted" xmlUrl="https://untrusted.example.org/private?'
    'token=SECRET_DO_NOT_RENDER"/></body></opml>'
)


def test_synthetic_first_reader_journey_u1_to_u6(browser, monkeypatch):
    """Software evidence for route behavior, not installation or human comprehension."""
    server, root = browser
    assert server.server_address[0] == "127.0.0.1"  # U1: local browser entrypoint
    calls = []

    def discover():
        calls.append("discover")
        return PrinterInventory("found", ("Local_A4",), "Select a queue.")

    def check(name, inventory):
        calls.append(("check", name))
        assert inventory.queues == ("Local_A4",)
        return PrinterReadiness(name, "reported-ready", True, False, False,
                                "No paper has been printed.")

    monkeypatch.setattr("kushluk.setup_web.discover_queues", discover)
    monkeypatch.setattr("kushluk.setup_web.check_queue", check)

    # Prohibit live source access and OS print submissions during this rehearsal.
    original_connect = socket.create_connection

    def loopback_only(address, *args, **kwargs):
        if address[0] != "127.0.0.1":
            pytest.fail("Synthetic first-reader journey attempted external network access")
        return original_connect(address, *args, **kwargs)

    monkeypatch.setattr(socket, "create_connection", loopback_only)
    monkeypatch.setattr(
        "kushluk.printer_preflight.subprocess.run",
        lambda *_a, **_kw: pytest.fail("Synthetic first-reader journey ran a system command"),
    )

    # U1/U2: first GET is inert; create exactly one owner-local home profile.
    status, page = request(server)
    assert status == 200
    token = csrf(page)
    assert 'name="printer"' not in page  # no unverified queue shortcut
    assert "street address is not required" in page
    assert not server.profile_file.exists()
    assert not server.registry_file.exists()
    assert calls == []
    status, done = request(server, fields={
        "csrf": token, "home_name": "Synthetic home", "latitude": "50.9",
        "longitude": "6.9", "timezone": "Europe/Berlin",
    })
    assert status == 201
    assert "No sources were enabled and no paper was printed" in done
    profile = read_local_profile(server.profile_file)
    assert profile["printer"] is None
    assert profile["home_name"] == "Synthetic home"
    assert (server.profile_file.stat().st_mode & 0o777) == 0o600

    # U3: proposing does not activate; approving one requires fresh checkbox.
    status, page = request(server, "/sources")
    assert status == 200
    assert "Nothing is activated until you approve" in page
    status, proposed = request(server, "/sources/import", {"csrf": token, "opml": OPML})
    assert status == 200
    assert "2 feeds proposed for review" in proposed
    assert "SECRET_DO_NOT_RENDER" not in proposed
    assert "Trusted &amp; useful" in proposed
    assert not server.registry_file.exists()
    assert request(server, "/sources/approve", {
        "csrf": token, "index": "1", "consent": "no",
    })[0] == 422
    assert not server.registry_file.exists()
    status, approved = request(server, "/sources/approve", {
        "csrf": token, "index": "1", "consent": "yes",
    })
    assert status == 200
    assert "One source approved" in approved
    rows = read_registry(server.registry_file)
    assert len(rows) == 1
    assert rows[0]["mode"] == "reference-only"
    assert rows[0]["enabled"] is True
    assert "untrusted" not in rows[0]["url"]
    assert "SECRET_DO_NOT_RENDER" not in approved

    # U4: pausing takes effect; resume fails without distinct consent.
    identifier = rows[0]["id"]
    assert request(server, "/sources/mode", {
        "csrf": token, "id": identifier, "mode": "ignore",
    })[0] == 200
    assert not read_registry(server.registry_file)[0]["enabled"]
    assert request(server, "/sources/mode", {
        "csrf": token, "id": identifier, "mode": "reference-only",
    })[0] == 422
    assert not read_registry(server.registry_file)[0]["enabled"]
    assert request(server, "/sources/mode", {
        "csrf": token, "id": identifier, "mode": "reference-only",
        "consent": "yes",
    })[0] == 200
    assert read_registry(server.registry_file)[0]["enabled"]

    # U5: no implicit CUPS scan on page load. Save preference separately.
    status, printer_page = request(server, "/printer")
    assert status == 200
    assert "Discover local printer queues" in printer_page
    assert calls == []
    assert request(server, "/printer/save", {
        "csrf": token, "queue": "Local_A4", "consent": "yes",
    })[0] == 422
    assert request(server, "/printer/scan", {"csrf": token})[0] == 200
    assert calls == ["discover"]
    status, checked = request(server, "/printer/check", {
        "csrf": token, "queue": "Local_A4",
    })
    assert status == 200
    assert "A4 advertised: yes" in checked
    assert "Save printer preference" in checked
    assert calls == ["discover", ("check", "Local_A4")]
    assert read_local_profile(server.profile_file)["printer"] is None
    assert request(server, "/printer/save", {
        "csrf": token, "queue": "Local_A4", "consent": "no",
    })[0] == 422
    assert read_local_profile(server.profile_file)["printer"] is None
    assert request(server, "/printer/save", {
        "csrf": token, "queue": "Local_A4", "consent": "yes",
    })[0] == 200
    assert read_local_profile(server.profile_file)["printer"] == "Local_A4"
    assert calls == ["discover", ("check", "Local_A4")]

    # U6: the flow must be truthful about disabled operations.
    assert "will never submit a print job" in printer_page
    assert "never copied articles" in page
    assert "No sources were enabled and no paper was printed" in done
    assert list(root.glob("**/*.pdf")) == []
    assert list(root.glob("**/*.epub")) == []
    assert not (root / "archive").exists()
    assert not (root / "output").exists()


def test_no_cups_fallback_and_no_implicit_permission(browser, monkeypatch):
    server, _ = browser
    interactions = []

    def missing_cups():
        interactions.append("discovery")
        return PrinterInventory("unavailable", (), "CUPS lpstat is not installed.")

    monkeypatch.setattr("kushluk.setup_web.discover_queues", missing_cups)
    monkeypatch.setattr("kushluk.setup_web.check_queue",
                        lambda *_: pytest.fail("unexpected queue check"))
    status, page = request(server, "/printer")
    assert status == 200 and interactions == []
    token = csrf(page)
    status, page = request(server, "/printer/scan", {"csrf": token})
    assert status == 200
    assert interactions == ["discovery"]
    assert "CUPS lpstat is not installed" in page
    assert "Save printer preference" not in page
    assert request(server, "/printer/check", {
        "csrf": token, "queue": "Invented",
    })[0] == 422
    assert not server.profile_file.exists()
    assert not server.registry_file.exists()
