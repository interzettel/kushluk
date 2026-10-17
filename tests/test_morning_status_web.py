"""Browser morning status is strictly local, read-only and content-free."""
from datetime import date
import json
from http.client import HTTPConnection
from threading import Thread

import pytest

from kushluk.config import Settings
from kushluk.morning_status_web import morning_status, render_morning_status
from kushluk.setup_web import SetupHTTPServer


def cfg(tmp_path):
    return Settings(archive_dir=tmp_path / "archive", output_dir=tmp_path / "output")


def request(server, path="/status", method="GET", headers=None):
    connection = HTTPConnection("127.0.0.1", server.server_port, timeout=3)
    try:
        connection.request(method, path, headers=headers or {})
        result = connection.getresponse()
        return result.status, dict(result.getheaders()), result.read().decode("utf-8")
    finally:
        connection.close()


@pytest.fixture
def status_server(tmp_path):
    settings = cfg(tmp_path)
    server = SetupHTTPServer(
        tmp_path / "config" / "profile.json",
        registry=tmp_path / "config" / "sources.json",
        status_settings=settings,
    )
    thread = Thread(target=server.serve_forever,
                    kwargs={"poll_interval": 0.01}, daemon=True)
    thread.start()
    try:
        yield server, settings
    finally:
        server.shutdown()
        thread.join(timeout=3)
        server.server_close()


def test_local_browser_status_is_read_only_without_a_receipt(status_server):
    server, settings = status_server
    code, headers, page = request(server)
    assert code == 200
    assert "<h1>Morning status</h1>" in page
    assert "Not started" in page
    assert "Validated archive not established" in page
    assert "Not requested" in page
    assert 'href="/printer"' in page
    assert "No run receipt exists" in page
    assert "physical" in page.lower()
    assert "default-src 'none'" in headers["Content-Security-Policy"]
    assert headers["Cache-Control"].startswith("no-store")
    assert server.server_address[0] == "127.0.0.1"
    assert not settings.archive_dir.exists()
    assert not server.profile_file.exists()


def test_status_route_rejects_bad_host_and_all_posts(status_server):
    server, settings = status_server
    assert request(server, headers={"Host": "malicious.local"})[0] == 404
    assert request(server, method="POST")[0] in {403, 413, 415}
    assert not settings.archive_dir.exists()


@pytest.mark.parametrize("state,label", [
    ("completed", "Edition prepared"),
    ("needs_review", "Needs your attention"),
    ("in_progress", "Run in progress"),
    ("paused", "Paused"),
    ("not_run", "Not started"),
])
def test_fixed_labels_are_accessible_and_never_claim_hardware(state, label):
    sample = {
        "date": "2026-10-17", "state": state,
        "archive_reported_ready": state == "completed",
        "print_state": "submission_accepted",
        "email_state": "not_requested",
        "notice_code": "printer_queue_not_physical_proof",
        "physical_verified": False, "recipient_verified": False,
    }
    html = render_morning_status(sample)
    assert label in html
    assert "Submitted to queue; delivery not verified" in html
    assert "Check actual paper and duplex separately." in html
    assert "An accepted email does not prove arrival." in html
    assert "aria-labelledby" in html
    assert "<script" not in html


def test_injected_receipt_text_can_never_reach_status_html(tmp_path, monkeypatch):
    from kushluk import morning_status_web as web
    secret = "private://reader/home?password=MY_VERY_PRIVATE_KEY"
    monkeypatch.setattr(web, "run_report", lambda *a, **kw: {
        "status": secret,
        "delivery": {"print": secret, "email": secret},
        "timing": {"validated_archived": True},
    })
    monkeypatch.setattr(web, "build_incident_report", lambda *a, **kw: {
        "error_code": secret,
    })
    summary = morning_status(cfg(tmp_path), target_date=date(2026, 10, 17))
    markup = render_morning_status(summary)
    assert secret not in json.dumps(summary)
    assert secret not in markup
    assert "Needs your attention" in markup
    assert "Not established" in markup


def test_status_page_is_not_a_delivery_command(status_server, monkeypatch):
    server, settings = status_server
    monkeypatch.setattr("kushluk.printing.print_pdf",
                        lambda *a, **k: pytest.fail("No printing from GET"))
    for _ in range(3):
        assert request(server)[0] == 200
    assert not settings.archive_dir.exists()
