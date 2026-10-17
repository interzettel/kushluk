"""Read-only local CUPS preflight and browser: no lp call or disk modifications."""
import re
import subprocess
from http.client import HTTPConnection
from threading import Thread
from urllib.parse import urlencode

import pytest

from kushluk import printer_preflight as preflight
from kushluk.printing import PrinterCapabilities
from kushluk.local_profile import write_local_profile, read_local_profile
from kushluk.setup_web import SetupHTTPServer


def test_lpstat_list_only_and_safe_queue_parsing(monkeypatch):
    calls = []
    monkeypatch.setattr(preflight.shutil, "which", lambda n: f"/usr/bin/{n}")

    def fake_run(cmd, **kwargs):
        calls.append((cmd, kwargs))
        return subprocess.CompletedProcess(
            cmd, 0,
            "printer Office_A4 is idle. enabled since now\n"
            "printer Printer-2 now printing\n"
            "printer <script>alert(1)</script> is idle. enabled\n"
            "printer Office_A4 is idle. enabled\n", "",
        )

    monkeypatch.setattr(preflight.subprocess, "run", fake_run)
    inventory = preflight.discover_queues()
    assert inventory.status == "found"
    assert inventory.queues == ("Office_A4",)
    assert calls[0][0] == ["/usr/bin/lpstat", "-p"]
    assert calls[0][1]["timeout"] == 6
    assert calls[0][1]["check"] is False
    assert not any("lp" == cmd[0].split("/")[-1] for cmd, _ in calls)


@pytest.mark.parametrize("exception", [OSError("private info"), subprocess.TimeoutExpired("lpstat", 6)])
def test_failed_listing_returns_nonsecret_status(monkeypatch, exception):
    monkeypatch.setattr(preflight.shutil, "which", lambda n: f"/bin/{n}")
    monkeypatch.setattr(preflight.subprocess, "run", lambda *a, **k: (_ for _ in ()).throw(exception))
    result = preflight.discover_queues()
    assert result.status == "unavailable"
    assert not result.queues
    assert "private info" not in result.note


def test_missing_cups_does_not_run_subprocess(monkeypatch):
    monkeypatch.setattr(preflight.shutil, "which", lambda _: None)
    monkeypatch.setattr(
        preflight.subprocess, "run", lambda *a, **k: pytest.fail("should not run")
    )
    assert preflight.discover_queues().status == "unavailable"


def test_queue_check_requires_recent_discovery_and_reports_media(monkeypatch):
    inventory = preflight.PrinterInventory("found", ("Office_A4",), "test")
    calls = []

    def fake_detect(name):
        calls.append(name)
        return PrinterCapabilities(
            name, True, True, ("iso_a4_210x297mm", "iso_a3_297x420mm"),
            "reported ready",
        )

    monkeypatch.setattr(preflight, "detect_printer_capabilities", fake_detect)
    for name in ("Unlisted", "../Office_A4", "-Unknown", "<script>"):
        with pytest.raises(ValueError):
            preflight.check_queue(name, inventory)
    with pytest.raises(ValueError):
        preflight.check_queue("Office_A4", None)
    assert calls == []
    check = preflight.check_queue("Office_A4", inventory)
    assert calls == ["Office_A4"]
    assert (check.status, check.a4, check.a3, check.duplex) == (
        "reported-ready", True, True, True,
    )


@pytest.fixture
def local_server(tmp_path):
    server = SetupHTTPServer(
        tmp_path / "profile.json",
        registry=tmp_path / "sources.json",
    )
    thread = Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
    thread.start()
    try:
        yield server
    finally:
        server.shutdown()
        thread.join(timeout=3)
        server.server_close()


def request(server, method="GET", path="/printer", fields=None, headers=None):
    conn = HTTPConnection("127.0.0.1", server.server_port, timeout=4)
    data = urlencode(fields).encode() if fields is not None else None
    params = dict(headers or {})
    if method == "POST":
        params.setdefault("Origin", server.origin)
        params.setdefault("Content-Type", "application/x-www-form-urlencoded")
        params.setdefault("Content-Length", str(len(data)))
    try:
        conn.request(method, path, body=data, headers=params)
        response = conn.getresponse()
        return response.status, response.read().decode("utf-8")
    finally:
        conn.close()


def token(page):
    found = re.search(r'name="csrf" value="([^"]+)"', page)
    assert found
    return found.group(1)


def test_printer_page_is_idle_and_requires_explicit_local_scan(local_server, monkeypatch):
    calls = []
    def inventory():
        calls.append("scan")
        return preflight.PrinterInventory("found", ("Queue_A",), "Available queues")
    def inspect(name, inventory):
        calls.append(("check", name, inventory.queues))
        return preflight.PrinterReadiness(name, "reported-ready", True, False, False,
                                          "No paper was printed.")
    monkeypatch.setattr("kushluk.setup_web.discover_queues", inventory)
    monkeypatch.setattr("kushluk.setup_web.check_queue", inspect)
    server = local_server
    status, page = request(server)
    assert status == 200
    assert "Discover local printer queues" in page
    assert calls == []
    assert not server.profile_file.exists()
    assert not server.registry_file.exists()
    csrf = token(page)
    # Faked queue selection before actual user scan must never call CUPS.
    status, page = request(server, "POST", "/printer/check",
                           {"csrf": csrf, "queue": "Queue_A"})
    assert status == 422 and calls == []

    status, page = request(server, "POST", "/printer/scan", {"csrf": csrf})
    assert status == 200
    assert "Queue_A" in page and "no print job sent" in page
    assert calls == ["scan"]
    status, page = request(server, "POST", "/printer/check",
                           {"csrf": csrf, "queue": "Queue_A"})
    assert status == 200
    assert "A4 advertised: yes" in page
    assert "A3 advertised: not confirmed" in page
    assert calls == ["scan", ("check", "Queue_A", ("Queue_A",))]
    assert not server.profile_file.exists()
    assert not server.registry_file.exists()


def test_printer_actions_reject_csrf_cross_origin_bad_hosts(local_server, monkeypatch):
    calls = []
    monkeypatch.setattr("kushluk.setup_web.discover_queues",
                        lambda: calls.append("scan"))
    status, page = request(local_server)
    assert status == 200
    t = token(page)
    for fields, headers in [
        ({"csrf": "wrong"}, {}),
        ({"csrf": t}, {"Origin": "https://evil.example"}),
        ({"csrf": t}, {"Host": "localhost:7890"}),
        ({"csrf": t, "unrecognized": "x"}, {}),
    ]:
        status, _ = request(local_server, "POST", "/printer/scan", fields, headers)
        assert status in {400, 403, 404}
    assert calls == []


def test_queue_name_escaped_when_rendered():
    inventory = preflight.PrinterInventory("found", ("<script>alert(1)</script>",), "check")
    html = preflight.render_printer_review(inventory, None, csrf="safe")
    assert "<script>" not in html
    assert "&lt;script&gt;" in html


def test_browser_save_checked_queue_requires_consent_and_existing_profile(local_server, monkeypatch):
    server = local_server
    def discover():
        return preflight.PrinterInventory("found", ("DeskJet_2820e", "Other"), "Found")
    def check(name, inventory):
        return preflight.PrinterReadiness(name, "reported-ready", True, False, False, "Advisory only.")
    monkeypatch.setattr("kushluk.setup_web.discover_queues", discover)
    monkeypatch.setattr("kushluk.setup_web.check_queue", check)
    _, page = request(server)
    csrf = token(page)
    save = {"csrf": csrf, "queue": "DeskJet_2820e", "consent": "yes"}
    assert request(server, "POST", "/printer/save", save)[0] == 422
    request(server, "POST", "/printer/scan", {"csrf": csrf})
    assert request(server, "POST", "/printer/save", save)[0] == 422
    request(server, "POST", "/printer/check", {"csrf": csrf, "queue": "DeskJet_2820e"})
    assert request(server, "POST", "/printer/save", save)[0] == 422
    assert not server.profile_file.exists()

    write_local_profile(server.profile_file, home_name="Reader", latitude=50.9,
                        longitude=6.9, timezone="Europe/Berlin")
    original = read_local_profile(server.profile_file)
    assert request(server, "POST", "/printer/save", {**save, "consent": "no"})[0] == 422
    assert request(server, "POST", "/printer/save", {"csrf": csrf, "queue": "DeskJet_2820e"})[0] == 400
    assert read_local_profile(server.profile_file) == original
    status, html = request(server, "POST", "/printer/save", save)
    assert status == 200
    assert "Printer preference saved locally" in html
    profile = read_local_profile(server.profile_file)
    assert profile["printer"] == "DeskJet_2820e"
    assert profile["home_name"] == "Reader"
    status, html = request(server)
    assert status == 200 and "DeskJet_2820e" in html
    assert "No print job has been sent" in html
    assert not server.registry_file.exists()
    request(server, "POST", "/printer/scan", {"csrf": csrf})
    assert request(server, "POST", "/printer/save", save)[0] == 422
    assert read_local_profile(server.profile_file) == profile


def test_save_printer_rejects_wrong_queue_csrf_origin_host_and_stale_check(local_server, monkeypatch):
    server = local_server
    write_local_profile(server.profile_file, home_name="Reader", latitude=50.9,
                        longitude=6.9, timezone="Europe/Berlin")
    monkeypatch.setattr("kushluk.setup_web.discover_queues",
                        lambda: preflight.PrinterInventory("found", ("Safe_A", "Safe_B"), "OK"))
    monkeypatch.setattr("kushluk.setup_web.check_queue",
                        lambda name, inv: preflight.PrinterReadiness(name, "unconfirmed", False, False, False, "Offline"))
    csrf = token(request(server)[1])
    request(server, "POST", "/printer/scan", {"csrf": csrf})
    request(server, "POST", "/printer/check", {"csrf": csrf, "queue": "Safe_A"})
    good = {"csrf": csrf, "queue": "Safe_A", "consent": "yes"}
    for fields, headers in [
        ({**good, "queue": "Safe_B"}, None),
        ({**good, "queue": "../Safe_A"}, None),
        ({**good, "csrf": "invalid"}, None),
        (good, {"Origin": "https://evil.invalid"}),
        (good, {"Host": "localhost:8080"}),
        ({**good, "consent": "1"}, None),
        ({**good, "unexpected": "x"}, None),
    ]:
        assert request(server, "POST", "/printer/save", fields, headers)[0] in (400, 403, 404, 422)
    assert read_local_profile(server.profile_file)["printer"] is None
    assert request(server, "POST", "/printer/save", good)[0] == 200
    # Availability metadata can be unconfirmed; saved selection != printer acceptance.
    assert read_local_profile(server.profile_file)["printer"] == "Safe_A"
