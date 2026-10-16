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
