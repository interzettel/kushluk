"""Render-to-delivery integration: crash, offline printer, and archived recovery."""
from datetime import date
from pathlib import Path

import pytest

from kushluk import pipeline
from kushluk.config import Settings
from kushluk.models import Candidate, DeliveryResult, PracticalItem, SourceRef
from kushluk.printing import PrintResult
from kushluk.validation import validate_pdf


DATE = date(2026, 9, 23)


def offline_sources(monkeypatch):
    monkeypatch.setattr(
        pipeline.OpenMeteoWeatherConnector, "fetch",
        lambda self: [PracticalItem("Weather", "Dry", "Offline fixture")],
    )
    monkeypatch.setattr(
        pipeline.CalendarFixtureConnector, "fetch",
        lambda self: [PracticalItem("Calendar", "Free", "Offline fixture")],
    )
    monkeypatch.setattr(
        pipeline.RSSConnector, "fetch",
        lambda self: [
            Candidate(
                id="offline-1", title="Local generated fixture", summary="Just a test.",
                source=SourceRef(kind="rss", name="CI synthetic"), required=True,
            )
        ],
    )


def config(tmp_path):
    return Settings(
        archive_dir=tmp_path / "archive", output_dir=tmp_path / "output",
        calendar_fixture=tmp_path / "unused.json", rss_urls=(),
    )


def test_archive_preserved_if_crash_at_print_submission(tmp_path, monkeypatch):
    pytest.importorskip("weasyprint")
    pytest.importorskip("pypdf")
    offline_sources(monkeypatch)
    cfg = config(tmp_path)
    seen_stages = []

    def before_print(channel):
        assert channel == "print"
        folder = cfg.archive_dir / "20260923-001"
        assert (folder / "edition.pdf").is_file()
        assert (folder / "edition.html").is_file()
        assert (folder / "metadata.json").is_file()
        assert validate_pdf(folder / "edition.pdf").ok
        raise RuntimeError("Simulate process death after persisting the archive")

    with pytest.raises(RuntimeError, match="Simulate process death"):
        pipeline.run_pipeline(
            cfg, target_date=DATE, send_to_printer=True,
            before_delivery=before_print,
            on_stage=seen_stages.append,
        )
    assert seen_stages.index("validated") < seen_stages.index("archive_ready")
    assert (cfg.archive_dir / "20260923-001" / "edition.pdf").is_file()


def test_offline_print_failure_uses_smtp_fallback_and_keeps_archive(tmp_path, monkeypatch):
    pytest.importorskip("weasyprint")
    pytest.importorskip("pypdf")
    offline_sources(monkeypatch)
    cfg = config(tmp_path)
    stages = []
    emails = []

    monkeypatch.setattr(
        pipeline, "print_pdf",
        lambda *args, **kwargs: PrintResult(True, False, "Simulated printer offline"),
    )

    def email_mock(*args, **kwargs):
        emails.append(kwargs)
        return DeliveryResult("email", "sent", "Simulated local SMTP success")

    monkeypatch.setattr(pipeline, "send_email_edition", email_mock)
    result = pipeline.run_pipeline(
        cfg, target_date=DATE, send_to_printer=True,
        email_on_print_failure=True, on_stage=stages.append,
    )
    assert result.pdf_path is not None
    assert result.print_result and not result.print_result.success
    assert result.email_result and result.email_result.status == "sent"
    assert len(emails) == 1
    assert emails[0]["pdf_path"] == result.pdf_path
    assert stages.index("archive_ready") < stages.index("print_failed")
    assert stages.index("print_failed") < stages.index("email_sent")
    assert stages[-1] == "complete"
    archive_pdf = cfg.archive_dir / "20260923-001" / "edition.pdf"
    assert validate_pdf(archive_pdf).ok
    assert "print_failed" in {failure.code for failure in result.failures}


def test_pipeline_never_attempts_delivery_without_validated_pdf(tmp_path, monkeypatch):
    offline_sources(monkeypatch)
    cfg = config(tmp_path)
    attempts = []
    monkeypatch.setattr(
        pipeline, "render_pdf",
        lambda html_path, pdf_path: (_ for _ in ()).throw(RuntimeError("No Pango")),
    )
    monkeypatch.setattr(
        pipeline, "print_pdf", lambda *args, **kwargs: attempts.append(True)
    )
    result = pipeline.run_pipeline(
        cfg, target_date=DATE, send_to_printer=True,
    )
    assert result.pdf_path is None
    assert result.print_result is not None and not result.print_result.success
    assert not attempts
    folder = Path(cfg.archive_dir / "20260923-001")
    assert (folder / "edition.html").exists()
    assert (folder / "metadata.json").exists()
    assert not (folder / "edition.pdf").exists()
