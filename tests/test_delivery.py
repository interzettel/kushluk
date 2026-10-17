from kushluk.delivery import build_email_message
from kushluk.models import Publication


def test_build_email_message_includes_html(tmp_path):
    html = tmp_path / "edition.html"
    html.write_text("<h1>Kushluk</h1>", encoding="utf-8")
    publication = Publication(
        edition_id="20260923-001",
        target_date="2026-09-23",
        timezone="Europe/Berlin",
        generated_at="2026-09-23T08:00:00+02:00",
        location_name="Cologne",
        practical=[],
        stories=[],
    )
    message = build_email_message(
        publication,
        sender="from@example.com",
        recipient="to@example.com",
        html_path=html,
    )
    assert "Kushluk" in message["Subject"]
    assert message["To"] == "to@example.com"
    assert len(message.get_payload()) == 2


def test_smtp_exception_and_recipient_never_appear_in_status(tmp_path, monkeypatch):
    from kushluk import delivery

    token = "SECRET-SMTP-CREDENTIAL"
    html = tmp_path / "edition.html"
    html.write_text("<h1>Edition</h1>", encoding="utf-8")
    publication = Publication("20260923-001", "2026-09-23", "Europe/Berlin",
                              "2026-09-23T08:00:00+02:00", "Test", [], [])
    class FailingSMTP:
        def __init__(self, *_args, **_kw):
            raise OSError(f"SMTP login secret {token}")

    monkeypatch.setattr(delivery.smtplib, "SMTP", FailingSMTP)
    receipt = delivery.send_email_edition(
        publication, host="smtp.invalid", port=587,
        username="test", password=token, sender="from@example.test",
        recipient="private-reader@example.test", starttls=True, html_path=html,
    )
    assert receipt.status == "failed"
    assert "OSError" in receipt.detail
    assert token not in receipt.detail
    assert "private-reader" not in receipt.detail
