import json
from datetime import date

import pytest

from kushluk import recovery
from kushluk.config import Settings
from kushluk.models import DeliveryResult
from kushluk.printing import PrintResult
from kushluk.validation import ValidationResult


TARGET = date(2026, 9, 23)


def archive_fixture(tmp_path, monkeypatch):
    cfg = Settings(
        archive_dir=tmp_path / "archive", output_dir=tmp_path / "output",
        smtp_host="smtp.example.test", smtp_from="test@example.test",
        email_to="reader@example.test",
    )
    folder = cfg.archive_dir / "20260923-001"
    folder.mkdir(parents=True)
    metadata = {
        "edition_id": "20260923-001", "target_date": TARGET.isoformat(),
        "schema_version": 2, "timezone": "Europe/Berlin",
        "generated_at": "2026-09-23T06:00:00+02:00", "location_name": "Test",
        "pages": [{"number": number} for number in range(1, 5)],
    }
    (folder / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    (folder / "edition.html").write_text("<h1>Archived edition</h1>", encoding="utf-8")
    (folder / "edition.pdf").write_bytes(b"frozen-original-four-page-pdf")
    (folder / "edition.a3-folded.pdf").write_bytes(b"frozen-original-a3-imposition")
    monkeypatch.setattr(recovery, "validate_pdf", lambda pdf: ValidationResult([], [], 4))
    monkeypatch.setattr(recovery, "validate_a3_booklet", lambda pdf: [])
    return cfg, folder


def resend(cfg, **kw):
    return recovery.deliver_archived(
        cfg, target_date=TARGET, channel="print", request_id="inspection-001",
        acknowledge_possible_duplicate=True, **kw,
    )


def test_explicit_print_delivery_never_regenerates_and_deduplicates(tmp_path, monkeypatch):
    cfg, folder = archive_fixture(tmp_path, monkeypatch)
    before = (folder / "edition.pdf").read_bytes()
    calls = []

    def print_stub(pdf, printer, **kwargs):
        calls.append((pdf, kwargs))
        return PrintResult(True, True, "Accepted by CUPS", printer=printer)

    monkeypatch.setattr(recovery, "print_pdf", print_stub)
    first = resend(cfg)
    again = resend(cfg)
    assert first.status == "submitted"
    assert again.status == "already_attempted"
    assert len(calls) == 1
    assert calls[0][0] == folder / "edition.pdf"
    assert calls[0][1]["media"] == "A4"
    assert (folder / "edition.pdf").read_bytes() == before
    receipt = json.loads(
        (folder / "manual-print-inspection-001.json").read_text(encoding="utf-8")
    )
    assert receipt["pdf_sha256"]
    assert receipt["status"] == "submitted"


def test_crash_or_timeout_does_not_resubmit_and_does_not_leak_secrets(tmp_path, monkeypatch):
    cfg, folder = archive_fixture(tmp_path, monkeypatch)
    calls = []

    def crash(*args, **kwargs):
        calls.append(True)
        raise TimeoutError("secret/private/calendar?token=hidden")

    monkeypatch.setattr(recovery, "print_pdf", crash)
    first = resend(cfg)
    second = resend(cfg)
    assert first.status == "needs_review"
    assert second.status == "already_attempted"
    assert len(calls) == 1
    receipt = (folder / "manual-print-inspection-001.json").read_text()
    assert "hidden" not in receipt
    assert "TimeoutError" in receipt


def test_without_acknowledgement_never_contacts_printer(tmp_path, monkeypatch):
    cfg, folder = archive_fixture(tmp_path, monkeypatch)
    monkeypatch.setattr(
        recovery, "print_pdf",
        lambda *a, **k: pytest.fail("Printing must require explicit acknowledgement"),
    )
    result = recovery.deliver_archived(
        cfg, target_date=TARGET, channel="print", request_id="inspection-001"
    )
    assert result.status == "blocked"
    assert not (folder / "manual-print-inspection-001.json").exists()


def test_invalid_archive_cannot_be_sent(tmp_path, monkeypatch):
    cfg, folder = archive_fixture(tmp_path, monkeypatch)
    (folder / "metadata.json").write_text(
        '{"edition_id":"other","schema_version":2,"pages":[]}', encoding="utf-8"
    )
    monkeypatch.setattr(
        recovery, "print_pdf", lambda *a, **k: pytest.fail("Invalid archive cannot print"),
    )
    assert resend(cfg).status == "blocked"
    assert not (folder / "manual-print-inspection-001.json").exists()


def test_a3_uses_only_the_archived_booklet_pdf(tmp_path, monkeypatch):
    cfg, folder = archive_fixture(tmp_path, monkeypatch)
    calls = []

    def print_stub(pdf, printer, **kwargs):
        calls.append((pdf, kwargs))
        return PrintResult(True, True, "Submitted")

    monkeypatch.setattr(recovery, "print_pdf", print_stub)
    result = resend(cfg, print_profile="a3-folded")
    assert result.status == "submitted"
    assert calls[0][0] == folder / "edition.a3-folded.pdf"
    assert calls[0][1]["media"] == "A3"
    assert calls[0][1]["require_duplex"] is True


def test_resend_from_archive_email_no_editorial_regeneration(tmp_path, monkeypatch):
    cfg, folder = archive_fixture(tmp_path, monkeypatch)
    sent = []

    def smtp_stub(pub, **kwargs):
        sent.append((pub, kwargs))
        return DeliveryResult("email", "sent", "ok")

    monkeypatch.setattr(recovery, "send_email_edition", smtp_stub)
    data = dict(
        settings=cfg, target_date=TARGET, channel="email",
        request_id="manual-mail-01", acknowledge_possible_duplicate=True,
    )
    first = recovery.deliver_archived(**data)
    again = recovery.deliver_archived(**data)
    assert first.status == "submitted"
    assert again.status == "already_attempted"
    assert len(sent) == 1
    assert sent[0][0].edition_id == "20260923-001"
    assert sent[0][1]["html_path"] == folder / "edition.html"
    assert sent[0][1]["pdf_path"] == folder / "edition.pdf"


def test_operator_request_id_is_path_safe(tmp_path, monkeypatch):
    cfg, _ = archive_fixture(tmp_path, monkeypatch)
    with pytest.raises(ValueError, match="Request ID"):
        recovery.deliver_archived(
            cfg, target_date=TARGET, channel="print",
            request_id="../other", acknowledge_possible_duplicate=True,
        )


def test_recursive_same_request_is_rejected_before_side_effect(tmp_path, monkeypatch):
    cfg, _ = archive_fixture(tmp_path, monkeypatch)
    nested = []

    def print_stub(pdf, printer, **kwargs):
        nested.append(resend(cfg))
        return PrintResult(True, True, "ok")

    monkeypatch.setattr(recovery, "print_pdf", print_stub)
    assert resend(cfg).status == "submitted"
    assert nested[0].status == "already_attempted"


@pytest.mark.parametrize("name,channel,profile", [
    ("metadata.json", "print", "a4-home"),
    ("edition.pdf", "print", "a4-home"),
    ("edition.a3-folded.pdf", "print", "a3-folded"),
    ("edition.html", "email", "a4-home"),
])
def test_recovery_refuses_symlink_archive_components_before_delivery(
    tmp_path, monkeypatch, name, channel, profile,
):
    cfg, folder = archive_fixture(tmp_path, monkeypatch)
    original = folder / name
    external = tmp_path / f"private-{name}"
    external.write_bytes(original.read_bytes())
    original.unlink()
    original.symlink_to(external)
    monkeypatch.setattr(recovery, "print_pdf",
                        lambda *a, **kw: pytest.fail("No print on unsafe archive"))
    monkeypatch.setattr(recovery, "send_email_edition",
                        lambda *a, **kw: pytest.fail("No email on unsafe archive"))
    result = recovery.deliver_archived(
        cfg, target_date=TARGET, channel=channel, request_id="symlink-trial",
        acknowledge_possible_duplicate=True, print_profile=profile,
    )
    assert result.status == "blocked"
    assert result.failure_code.startswith("archive_preflight_")
    assert not (folder / f"manual-{channel}-symlink-trial.json").exists()


def test_recovery_refuses_symlinked_edition_directory(tmp_path, monkeypatch):
    cfg, folder = archive_fixture(tmp_path, monkeypatch)
    original_location = folder.with_name("real-edition")
    folder.rename(original_location)
    folder.symlink_to(original_location, target_is_directory=True)
    monkeypatch.setattr(recovery, "print_pdf",
                        lambda *a, **kw: pytest.fail("No symlink print"))
    result = resend(cfg)
    assert result.status == "blocked"
    assert not (original_location / "manual-print-inspection-001.json").exists()


@pytest.mark.parametrize("name,channel", [
    ("metadata.json", "print"),
    ("edition.pdf", "print"),
    ("edition.html", "email"),
])
def test_recovery_rejects_oversized_inputs_without_sending(
    tmp_path, monkeypatch, name, channel,
):
    cfg, folder = archive_fixture(tmp_path, monkeypatch)
    limit = {
        "metadata.json": 2 * 1024 * 1024,
        "edition.pdf": 30 * 1024 * 1024,
        "edition.html": 5 * 1024 * 1024,
    }[name]
    # Sparse file: avoid storing 30 MiB of fixture data.
    with (folder / name).open("wb") as stream:
        stream.truncate(limit + 1)
    monkeypatch.setattr(recovery, "print_pdf",
                        lambda *a, **kw: pytest.fail("No print of oversized input"))
    monkeypatch.setattr(recovery, "send_email_edition",
                        lambda *a, **kw: pytest.fail("No email of oversized input"))
    result = recovery.deliver_archived(
        cfg, target_date=TARGET, channel=channel, request_id="oversize",
        acknowledge_possible_duplicate=True,
    )
    assert result.status == "blocked"
    assert not (folder / f"manual-{channel}-oversize.json").exists()


def test_archived_letter_reprint_uses_only_verified_letter_pdf(tmp_path, monkeypatch):
    cfg, folder = archive_fixture(tmp_path, monkeypatch)
    letter = folder / "edition.letter.pdf"
    letter.write_bytes(b"synthetic-four-page-letter")
    monkeypatch.setattr(recovery, "validate_letter_home", lambda p: [])
    printed = []

    def fake_print(path, printer, **kwargs):
        printed.append((path, kwargs))
        return PrintResult(True, True, "CUPS accepted only")

    monkeypatch.setattr(recovery, "print_pdf", fake_print)
    response = resend(cfg, print_profile="letter-home")
    assert response.status == "submitted"
    assert printed[0][0] == letter
    assert printed[0][1]["media"] == "Letter"
    assert printed[0][1]["duplex_edge"] == "long"
    assert resend(cfg, print_profile="letter-home").status == "already_attempted"
    assert len(printed) == 1
    saved = json.loads((folder / "manual-print-inspection-001.json").read_text())
    assert saved["print_profile"] == "letter-home"
    assert saved["pdf_sha256"]


def test_archived_letter_preflight_fails_closed_on_missing_or_invalid_media(
    tmp_path, monkeypatch,
):
    cfg, folder = archive_fixture(tmp_path, monkeypatch)
    monkeypatch.setattr(recovery, "print_pdf",
                        lambda *_a, **_kw: pytest.fail("Never print missing Letter"))
    assert resend(cfg, print_profile="letter-home").status == "blocked"
    letter = folder / "edition.letter.pdf"
    letter.write_bytes(b"invalid-letter-file")
    monkeypatch.setattr(recovery, "validate_letter_home",
                        lambda p: ["Missing correct page geometry"])
    assert resend(cfg, print_profile="letter-home").status == "blocked"
    assert not (folder / "manual-print-inspection-001.json").exists()
