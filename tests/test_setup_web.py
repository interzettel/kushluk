"""A local, privacy-first setup page: HTTP integration and negative security tests."""
from http.client import HTTPConnection
from threading import Thread
from urllib.parse import urlencode
import re

import pytest

from kushluk.cli import main
from kushluk.local_profile import read_local_profile
from kushluk.setup_web import SetupHTTPServer


@pytest.fixture
def setup_server(tmp_path):
    server = SetupHTTPServer(tmp_path / "private" / "profile.json")
    worker = Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01},
                    daemon=True)
    worker.start()
    try:
        yield server
    finally:
        server.shutdown()
        worker.join(timeout=3)
        server.server_close()


def _request(server, method="GET", path="/", *, headers=None, body=None):
    connection = HTTPConnection("127.0.0.1", server.server_port, timeout=3)
    try:
        connection.request(method, path, body=body, headers=headers or {})
        result = connection.getresponse()
        return result.status, dict(result.getheaders()), result.read().decode("utf-8")
    finally:
        connection.close()


def _token(markup):
    match = re.search(r'name="csrf" value="([^"]+)"', markup)
    assert match
    return match.group(1)


def _form(token, **changes):
    values = {
        "csrf": token, "home_name": "Household", "latitude": "50.9",
        "longitude": "6.9", "timezone": "Europe/Berlin", "printer": "",
    }
    values.update(changes)
    return urlencode(values).encode("utf-8")


def _post(server, body, headers=None):
    base = {"Origin": server.origin,
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": str(len(body))}
    base.update(headers or {})
    return _request(server, "POST", headers=base, body=body)


def test_only_loopback_listener_and_private_creation(setup_server):
    server = setup_server
    assert server.server_address[0] == "127.0.0.1"
    status, headers, html = _request(server)
    assert status == 200
    assert 'name="home_name"' in html
    assert "Kuşluk" in html
    assert "Save my local profile" in html
    assert "default-src 'none'" in headers["Content-Security-Policy"]
    assert headers["Cache-Control"].startswith("no-store")
    assert headers["Referrer-Policy"] == "no-referrer"
    assert not server.profile_file.exists()

    status, headers, html = _post(server, _form(_token(html)))
    assert status == 201
    assert "saved in a private file" in html
    assert server.profile_file.exists()
    assert read_local_profile(server.profile_file)["home_name"] == "Household"

    status, _, html = _request(server)
    assert status == 409
    assert "already exists" in html
    assert "50.9" not in html


@pytest.mark.parametrize("wrong_headers", [
    {"Origin": "http://localhost:5555"},
    {"Origin": "null"},
    {"Sec-Fetch-Site": "cross-site"},
    {"Content-Type": "text/plain"},
])
def test_reject_cross_origin_or_unsupported_posts(setup_server, wrong_headers):
    _, _, markup = _request(setup_server)
    status, _, _ = _post(
        setup_server, _form(_token(markup)), wrong_headers,
    )
    assert status in (403, 415)
    assert not setup_server.profile_file.exists()


def test_form_requires_csrf_and_exact_host(setup_server):
    _, _, html = _request(setup_server)
    token = _token(html)
    status, _, _ = _post(setup_server, _form("fake-csrf"))
    assert status == 403
    status, _, _ = _request(setup_server, headers={"Host": "evil.example"})
    assert status == 404
    status, _, _ = _post(
        setup_server, _form(token),
        {"Host": "evil.example", "Origin": setup_server.origin},
    )
    assert status == 404
    assert not setup_server.profile_file.exists()


@pytest.mark.parametrize("override", [
    {"latitude": "nan"},
    {"latitude": "99.5"},
    {"longitude": "-190"},
    {"timezone": "Not_A_Valid_Zone"},
    {"home_name": "<script>alert(1)</script>\n"},
])
def test_invalid_input_never_writes_or_echoes_user_input(setup_server, override):
    _, _, html = _request(setup_server)
    status, _, content = _post(setup_server, _form(_token(html), **override))
    assert status == 422
    assert not setup_server.profile_file.exists()
    assert "<script>" not in content


def test_reject_unknown_duplicate_and_oversized_forms(setup_server):
    _, _, html = _request(setup_server)
    body = _form(_token(html))
    for payload in (
        body + b"&secret_key=never-accept",
        body + b"&timezone=UTC",
        b"x" * 4097,
    ):
        status, _, _ = _post(setup_server, payload)
        assert status in (400, 413)
    assert not setup_server.profile_file.exists()


def test_existing_profile_never_overwritten(setup_server):
    server = setup_server
    _, _, html = _request(server)
    assert _post(server, _form(_token(html)))[0] == 201
    original = server.profile_file.read_bytes()
    status, _, _ = _post(server, _form(_token(html), home_name="Another name"))
    assert status == 422
    assert server.profile_file.read_bytes() == original


def test_not_making_external_requests_or_activating_sources(
        setup_server, tmp_path, monkeypatch):
    import socket
    import kushluk.setup_web as module

    original = socket.create_connection

    def reject_remote(address, *args, **kwargs):
        assert address[0] in ("127.0.0.1",)
        return original(address, *args, **kwargs)

    monkeypatch.setattr(socket, "create_connection", reject_remote)
    monkeypatch.setattr(module.webbrowser, "open", lambda *_: pytest.fail("Browser opened"))
    _, _, html = _request(setup_server)
    assert _post(setup_server, _form(_token(html)))[0] == 201
    assert not (tmp_path / "approved-sources.json").exists()
    assert not (tmp_path / "archive").exists()


def test_cli_setup_web_is_separate_from_settings_and_no_external_binding(
        monkeypatch, tmp_path):
    invoked = []
    monkeypatch.setattr(
        "kushluk.cli.run_setup_web",
        lambda *, path, open_browser: invoked.append((path, open_browser)),
    )
    path = tmp_path / "planned.json"
    assert main(["setup-web", "--no-open", "--output", str(path)]) == 0
    assert invoked == [(path, False)]
    assert not path.exists()


def test_non_ascii_csrf_is_rejected_without_server_error(setup_server):
    _, _, html = _request(setup_server)
    status, _, _ = _post(setup_server, _form(_token(html) + "★"))
    assert status == 403
    assert not setup_server.profile_file.exists()
