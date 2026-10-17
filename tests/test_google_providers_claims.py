"""Hermetic provider and bibliographic checking tests; never use a real inbox."""
from datetime import date, datetime, timezone
import json

import pytest

from kushluk.claims import ClaimCheckError, check_crossref_claim
from kushluk.connectors.google_local import (
    GoogleProviderError, _get, _read_private, _session, _write_private,
    discover_gmail, fetch_google_tasks,
)


NOW = datetime(2026, 10, 17, 12, tzinfo=timezone.utc)


class Response:
    status_code = 200
    headers = {}

    def __init__(self, data, status=200):
        self.data, self.status_code = data, status
        self.closed = False

    def iter_content(self, chunk_size):
        yield json.dumps(self.data).encode()

    def close(self):
        self.closed = True


class Session:
    def __init__(self, payloads):
        self.payloads = list(payloads)
        self.calls = []

    def get(self, url, *, params, timeout, allow_redirects, stream):
        self.calls.append((url, params))
        assert allow_redirects is False
        assert stream is True
        assert timeout == 12
        return Response(self.payloads.pop(0))


def message(days_ago):
    when = NOW.timestamp() - days_ago * 86400
    return {
        "internalDate": str(round(when * 1000)),
        "payload": {"headers": [
            {"name": "From", "value": "Editor <editor@journal.example>"},
            {"name": "List-ID", "value": "<digest.journal.example>"},
            {"name": "Subject", "value": "PRIVATE NOTE MUST NOT LEAK"},
        ]},
        "body": {"data": "SUBSCRIBER BODY NEVER SAVED"},
    }


def test_consent_gated_gmail_headers_only_with_no_private_content(tmp_path):
    s = Session([
        {"messages": [{"id": "aaa"}, {"id": "bbb"}]},
        message(1), message(2),
    ])
    result = discover_gmail(tmp_path, days=30, now=NOW, session=s)
    assert result["scanned_messages"] == 2
    assert len(result["sources"]) == 1
    assert result["sources"][0]["message_count"] == 2
    assert result["sources"][0]["sender_domain"] == "journal.example"
    assert result["ingestion_enabled"] is False
    assert result["partial_scan"] is False
    serialized = json.dumps(result)
    assert "editor@" not in serialized
    assert "PRIVATE NOTE" not in serialized and "SUBSCRIBER BODY" not in serialized
    details = [p for u, p in s.calls if u.endswith(("/aaa", "/bbb"))]
    assert len(details) == 2
    for params in details:
        assert params["format"] == "metadata"
        assert params["metadataHeaders"] == ["From", "List-ID", "Date"]
        assert "q" not in params
        assert "full" not in str(params).lower()


def test_gmail_hard_message_cap_and_partial_scan(tmp_path):
    s = Session([
        {"messages": [{"id": "a1"}, {"id": "a2"}],
         "nextPageToken": "private-page-token"}, message(1), message(2),
    ])
    result = discover_gmail(tmp_path, days=30, now=NOW, session=s, max_messages=2)
    assert result["partial_scan"] is True
    assert len(s.calls) == 3
    assert "private-page-token" not in json.dumps(result)


def test_gmail_provider_outages_are_fixed_no_raw_private_error(tmp_path):
    class Bad:
        def get(self, *_args, **_kwargs):
            raise RuntimeError("token=super-secret; user@example.org")
    with pytest.raises(GoogleProviderError, match="google_provider_unavailable") as err:
        discover_gmail(tmp_path, now=NOW, session=Bad())
    assert "super-secret" not in str(err.value)


def test_gmail_no_message_body_or_subject_can_create_newsletter_rights(tmp_path):
    s = Session([
        {"messages": [{"id": "aaa"}, {"id": "bbb"}]},
        message(1), message(1),
    ])
    result = discover_gmail(tmp_path, days=30, now=NOW, session=s)
    assert result["sources"] == []  # Repeated messages on one day aren't recurrence.
    assert not result["ingestion_enabled"]


def test_google_tasks_specific_readonly_provider(tmp_path):
    s = Session([
        {"items": [{"id": "listA"}]},
        {"items": [
            {"id": "1", "title": "Overdue", "status": "needsAction",
             "due": "2026-10-16T00:00:00.000Z"},
            {"id": "2", "title": "Today", "status": "needsAction",
             "due": "2026-10-17T00:00:00.000Z"},
            {"id": "3", "title": "Tomorrow", "status": "needsAction",
             "due": "2026-10-18T00:00:00.000Z"},
            {"id": "4", "title": "Finished", "status": "completed",
             "due": "2026-10-16T00:00:00.000Z"},
            {"id": "5", "title": "Undated", "status": "needsAction"},
        ]},
    ])
    items = fetch_google_tasks(tmp_path, target_date=date(2026, 10, 17), session=s)
    assert [x.value for x in items] == ["Overdue", "Today"]
    assert all(x.source.name == "Google Tasks (read-only)" for x in items)
    assert s.calls[1][1]["showCompleted"] == "false"
    assert all("gmail" not in call[0] for call in s.calls)


def test_google_provider_credentials_are_private_and_scopes_differ(tmp_path):
    vault = tmp_path / "vault"
    file = vault / "gmail-token.json"
    _write_private(file, {"scopes": ["https://www.googleapis.com/auth/gmail.metadata"]})
    assert file.stat().st_mode & 0o777 == 0o600
    assert _read_private(file)["scopes"] == [
        "https://www.googleapis.com/auth/gmail.metadata"
    ]
    file.chmod(0o644)
    with pytest.raises(GoogleProviderError, match="unsafe_google_credentials"):
        _read_private(file)
    file.unlink()
    file.symlink_to(tmp_path / "secret")
    with pytest.raises(GoogleProviderError):
        _read_private(file)


def test_wrong_scope_cannot_be_used_for_tasks_even_if_credentials_exist(tmp_path):
    vault = tmp_path / "vault"
    _write_private(vault / "tasks-token.json",
                   {"scopes": ["https://www.googleapis.com/auth/gmail.metadata"]})
    with pytest.raises(GoogleProviderError, match="oauth_scope_mismatch"):
        _session("tasks", vault)


def test_google_json_fetch_rejects_any_unauthorized_domain_or_redirect():
    with pytest.raises(GoogleProviderError, match="unapproved_google_endpoint"):
        _get(None, "https://gmail.googleapis.com.attacker.example/anything")
    class Redirect:
        def get(self, *_args, **_kwargs):
            return Response({}, status=302)
    with pytest.raises(GoogleProviderError, match="google_provider_unavailable"):
        _get(Redirect(), "https://gmail.googleapis.com/gmail/v1/users/me/messages")


def test_crossref_exact_bibliographic_match_is_not_factual_study_verification(monkeypatch):
    from kushluk import claims
    def fake(url, *, expected_host):
        assert expected_host == "api.crossref.org"
        assert "/works/" in url
        return json.dumps({"message": {
            "DOI": "10.1038/example", "title": ["About Climate and Cities"],
            "published": {"date-parts": [[2022, 5, 1]]},
            "abstract": "A paywalled abstract must not be published.",
        }}).encode()
    monkeypatch.setattr(claims, "fetch_public_json", fake)
    check = check_crossref_claim(
        "10.1038/example", asserted_title="About Climate and Cities",
        asserted_year=2022,
    )
    assert check.state == "bibliographic-match-claims-unverified"
    assert check.claims_about_study_findings_verified is False
    assert "paywalled" not in str(check.as_dict())
    mismatch = check_crossref_claim(
        "10.1038/example", asserted_title="False title", asserted_year=2022,
    )
    assert mismatch.state == "bibliographic-conflict"


def test_crossref_missing_or_failed_provider_abstains(monkeypatch):
    from kushluk import claims
    monkeypatch.setattr(claims, "fetch_public_json",
                        lambda *_args, **_kwargs: b'{"message":{"DOI":"10.1/wrong"}}')
    got = check_crossref_claim("10.1038/example", asserted_title="One")
    assert got.state == "abstain-unmatched-doi"
    monkeypatch.setattr(claims, "fetch_public_json",
                        lambda *_args, **_kwargs: (_ for _ in ()).throw(
                            ValueError("private live API token")))
    got = check_crossref_claim("10.1038/example", asserted_title="One")
    assert got.state == "abstain-provider-unavailable"
    assert "token" not in json.dumps(got.as_dict())
    with pytest.raises(ClaimCheckError):
        check_crossref_claim("javascript:alert(1)", asserted_title="One")


def test_bibliographic_cli_outputs_only_mapped_confidence(monkeypatch, capsys):
    from kushluk import cli
    from kushluk.claims import ClaimCheck
    monkeypatch.setattr(cli, "check_crossref_claim", lambda *_a, **_kw: ClaimCheck(
        doi="10.1234/a", asserted_title="Public title", asserted_year=2024,
        state="bibliographic-match-claims-unverified",
        checked_at="2026-10-17T12:00:00+00:00", evidence_url="https://doi.org/10.1234/a",
    ))
    assert cli.main(["crossref-check", "--doi", "10.1234/a", "--title", "Public title",
                     "--year", "2024"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["claims_about_study_findings_verified"] is False
