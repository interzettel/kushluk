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
    server = SetupHTTPServer(
        tmp_path / "private" / "profile.json",
        registry=tmp_path / "private" / "approved-sources.json",
    )
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


def _post(server, body, headers=None, *, path="/"):
    base = {"Origin": server.origin,
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": str(len(body))}
    base.update(headers or {})
    return _request(server, "POST", path, headers=base, body=body)


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


# SOURCE REVIEW: all of these operations must be offline and individually consented.
def _opml_sample():
    return (
        '<opml version="2.0"><body>'
        '<outline text="Public &amp; useful" xmlUrl="https://news.example.org/rss"/>'
        '<outline xmlUrl="https://feed.example.org/private?token=DO_NOT_ECHO"/>'
        '</body></opml>'
    )


def _source_form(server, path, values, *, token=None, headers=None):
    if token is None:
        _, _, page = _request(server, path="/sources")
        token = _token(page)
    payload = urlencode({"csrf": token, **values}).encode("utf-8")
    return _post(server, payload, headers=headers, path=path)


def test_source_review_import_is_inert_private_and_html_escaped(setup_server):
    server = setup_server
    status, head, page = _request(server, path="/sources")
    assert status == 200
    assert "Choose what belongs in your paper" in page
    assert "name=\"opml\"" in page
    assert head["Cache-Control"].startswith("no-store")
    assert not server.registry_file.exists()

    status, _, page = _source_form(server, "/sources/import", {"opml": _opml_sample()})
    assert status == 200
    assert "2 feeds proposed for review" in page
    assert "Public &amp; useful" in page
    assert "DO_NOT_ECHO" not in page
    assert "Feed from feed.example.org" in page
    assert not server.registry_file.exists()
    assert len(server.pending_feeds) == 2
    assert not server.profile_file.exists()

    # No consent supplied: browser's required checkbox is backed by a server check.
    status, _, _ = _source_form(server, "/sources/approve", {"index": "1"})
    assert status == 400
    assert not server.registry_file.exists()
    status, _, page = _source_form(
        server, "/sources/approve", {"index": "1", "consent": "no"}
    )
    assert status == 422
    assert not server.registry_file.exists()

    status, _, page = _source_form(
        server, "/sources/approve", {"index": "2", "consent": "yes"}
    )
    assert status == 200
    assert "One source approved" in page
    from kushluk.source_registry import read_registry
    rows = read_registry(server.registry_file)
    assert len(rows) == 1
    assert rows[0]["mode"] == "reference-only"
    assert rows[0]["enabled"] is True
    assert rows[0]["url"].endswith("DO_NOT_ECHO")
    assert "DO_NOT_ECHO" not in page
    assert "article bodies" in page
    assert not server.profile_file.exists()


def test_browser_mode_pause_resume_requires_new_permission(setup_server):
    server = setup_server
    assert _source_form(server, "/sources/import", {"opml": _opml_sample()})[0] == 200
    assert _source_form(
        server, "/sources/approve", {"index": "1", "consent": "yes"}
    )[0] == 200
    from kushluk.source_registry import read_registry
    identifier = read_registry(server.registry_file)[0]["id"]
    assert _source_form(
        server, "/sources/mode", {"id": identifier, "mode": "ignore"}
    )[0] == 200
    assert read_registry(server.registry_file)[0]["enabled"] is False

    assert _source_form(
        server, "/sources/mode", {"id": identifier, "mode": "reference-only"}
    )[0] == 422
    assert read_registry(server.registry_file)[0]["enabled"] is False
    assert _source_form(
        server, "/sources/mode",
        {"id": identifier, "mode": "private-direct", "consent": "yes"}
    )[0] == 422
    assert read_registry(server.registry_file)[0]["enabled"] is False
    assert _source_form(
        server, "/sources/mode",
        {"id": identifier, "mode": "reference-only", "consent": "yes"}
    )[0] == 200
    assert read_registry(server.registry_file)[0]["enabled"] is True


def test_browser_source_csrf_origin_exact_fields_and_no_hidden_activation(setup_server):
    server = setup_server
    assert _source_form(server, "/sources/import", {"opml": _opml_sample()})[0] == 200
    for path, values in [
        ("/sources/approve", {"index": "1", "consent": "yes"}),
        ("/sources/import", {"opml": _opml_sample()}),
    ]:
        status, _, _ = _source_form(server, path, values, token="bad-csrf")
        assert status == 403
        status, _, _ = _source_form(
            server, path, values, headers={"Origin": "https://attacker.test"}
        )
        assert status == 403
        status, _, _ = _source_form(
            server, path, values, headers={"Host": "attacker.test"}
        )
        assert status == 404
    status, _, _ = _source_form(
        server, "/sources/approve",
        {"index": "1", "consent": "yes", "mode": "private-direct"}
    )
    assert status == 400
    assert not server.registry_file.exists()


def test_browser_rejects_oversized_or_entity_OPML_without_activation(setup_server):
    server = setup_server
    bad = '<!DOCTYPE opml [<!ENTITY x SYSTEM "file:///etc/passwd">]>' + _opml_sample()
    assert _source_form(server, "/sources/import", {"opml": bad})[0] == 422
    assert len(server.pending_feeds) == 0
    assert not server.registry_file.exists()
    long_opml = _opml_sample() + (" " * 150_000)
    try:
        status, _, _ = _source_form(server, "/sources/import", {"opml": long_opml})
        assert status == 413
    except (ConnectionResetError, BrokenPipeError):
        # A server rejecting Content-Length without consuming an oversized
        # POST may close the socket before the HTTP client has finished writing.
        # macOS can surface TCP RST instead of the already-sent 413 response.
        pass
    assert _request(server, path="/sources")[0] == 200
    assert not server.registry_file.exists()


def test_source_review_cannot_use_unapproved_proposal_after_restart(setup_server):
    server = setup_server
    assert _source_form(server, "/sources/import", {"opml": _opml_sample()})[0] == 200
    server.pending_feeds = ()
    assert _source_form(
        server, "/sources/approve", {"index": "1", "consent": "yes"}
    )[0] == 422
    assert not server.registry_file.exists()


def test_source_review_does_not_fetch_or_publish(setup_server, monkeypatch, tmp_path):
    import kushluk.feed_network as network
    import kushluk.setup_web as setup_module

    monkeypatch.setattr(network, "fetch_public_xml", lambda *_: pytest.fail("network"))
    monkeypatch.setattr(setup_module.webbrowser, "open", lambda *_: pytest.fail("browser"))
    server = setup_server
    assert _source_form(server, "/sources/import", {"opml": _opml_sample()})[0] == 200
    assert _source_form(
        server, "/sources/approve", {"index": "1", "consent": "yes"}
    )[0] == 200
    assert not server.profile_file.exists()
    assert not (tmp_path / "archive").exists()
