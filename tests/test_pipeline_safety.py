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


def test_end_to_end_crash_then_explicit_archive_only_recovery(tmp_path, monkeypatch):
    pytest.importorskip("weasyprint")
    pytest.importorskip("pypdf")
    from kushluk import recovery, scheduled

    offline_sources(monkeypatch)
    cfg = config(tmp_path)
    first_calls = []

    def timeout_after_submission(*args, **kwargs):
        first_calls.append(True)
        raise TimeoutError("Uncertain CUPS submission")

    monkeypatch.setattr(pipeline, "print_pdf", timeout_after_submission)
    result = scheduled.run_once(cfg, target_date=DATE, send_to_printer=True)
    assert result.status == "needs_review"
    assert len(first_calls) == 1
    archived = cfg.archive_dir / "20260923-001" / "edition.pdf"
    assert validate_pdf(archived).ok
    original = archived.read_bytes()

    # Deliberately break all sources: recovery MUST NEVER fetch/rebuild.
    def fail_fetch(*args, **kwargs):
        raise AssertionError("Recovery must never call the publication pipeline")

    monkeypatch.setattr(pipeline.OpenMeteoWeatherConnector, "fetch", fail_fetch)
    monkeypatch.setattr(pipeline.CalendarFixtureConnector, "fetch", fail_fetch)
    monkeypatch.setattr(pipeline.RSSConnector, "fetch", fail_fetch)
    submitted = []
    def approve_print(pdf, printer, **kwargs):
        submitted.append(pdf)
        return PrintResult(True, True, "Accepted locally")

    monkeypatch.setattr(recovery, "print_pdf", approve_print)
    retry = recovery.deliver_archived(
        cfg, target_date=DATE, channel="print", request_id="owner-review-001",
        acknowledge_possible_duplicate=True,
    )
    repeated = recovery.deliver_archived(
        cfg, target_date=DATE, channel="print", request_id="owner-review-001",
        acknowledge_possible_duplicate=True,
    )
    assert retry.status == "submitted"
    assert repeated.status == "already_attempted"
    assert submitted == [archived]
    assert archived.read_bytes() == original


def test_sensitive_connector_errors_never_enter_edition_or_archived_receipts(
    tmp_path, monkeypatch, capsys,
):
    import json
    from kushluk.cli import main

    cfg = config(tmp_path)
    secret = "SECRET_TOKEN_DO_NOT_ARCHIVE"
    private_calendar = f"https://calendar.example.test/?token={secret}"

    def deny_weather(_self):
        raise RuntimeError(f"Weather API rejected key {secret}")

    def deny_calendar(_self):
        raise OSError(f"Cannot read {private_calendar}")

    def deny_rss(_self):
        raise ValueError(f"RSS contains private credential {secret}")

    monkeypatch.setattr(pipeline.OpenMeteoWeatherConnector, "fetch", deny_weather)
    monkeypatch.setattr(pipeline.CalendarFixtureConnector, "fetch", deny_calendar)
    monkeypatch.setattr(pipeline.RSSConnector, "fetch", deny_rss)
    monkeypatch.setenv("KUSHLUK_OUTPUT_DIR", str(cfg.output_dir))
    monkeypatch.setenv("KUSHLUK_ARCHIVE_DIR", str(cfg.archive_dir))
    monkeypatch.setenv("KUSHLUK_CALENDAR_FIXTURE", str(cfg.calendar_fixture))
    monkeypatch.setenv("KUSHLUK_RSS_URLS", "")
    monkeypatch.setenv("KUSHLUK_PROFILE_FILE", str(tmp_path / "no-profile.json"))
    monkeypatch.setenv("KUSHLUK_SOURCE_REGISTRY", str(tmp_path / "no-registry.json"))
    assert main(["generate", "--date", str(DATE), "--no-pdf"]) == 0
    displayed = capsys.readouterr().out
    assert "weather_unavailable" in displayed
    assert "calendar_unavailable" in displayed
    assert "rss_unavailable" in displayed
    assert secret not in displayed
    for extension in ("run.json", "metadata.json", "edition.md", "edition.html"):
        artifact = cfg.archive_dir / "20260923-001" / extension
        assert artifact.exists()
        assert secret not in artifact.read_text(encoding="utf-8")
    receipt = json.loads((cfg.archive_dir / "20260923-001" / "run.json").read_text())
    assert {r["code"] for r in receipt["failures"]} >= {
        "weather_unavailable", "calendar_unavailable", "rss_unavailable",
    }


def test_renderer_exception_redacted_from_archived_publication(tmp_path, monkeypatch):
    offline_sources(monkeypatch)
    secret = "SMALL_PRIVATE_URL_TOKEN"
    monkeypatch.setattr(
        pipeline, "render_pdf",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            OSError(f"Could not open /home/reader/calendar/{secret}")
        ),
    )
    result = pipeline.run_pipeline(config(tmp_path), target_date=DATE)
    assert result.pdf_path is None
    assert any(x.code == "pdf_unavailable" for x in result.failures)
    for path in result.archive_dir.iterdir():
        if path.suffix in {".md", ".json", ".html"}:
            assert secret not in path.read_text(encoding="utf-8")


def test_letter_selected_in_setup_generates_archived_letter_and_matching_cups_media(
    tmp_path, monkeypatch,
):
    pytest.importorskip("weasyprint")
    pytest.importorskip("pypdf")
    from kushluk.print_profiles import validate_letter_home
    import json

    offline_sources(monkeypatch)
    cfg = config(tmp_path)
    cfg.paper_size = "letter"
    called = []

    def mock_cups(file, printer, **kwargs):
        called.append((file, kwargs))
        assert validate_letter_home(file) == []
        return PrintResult(True, True, "Synthetic CUPS acceptance only")

    monkeypatch.setattr(pipeline, "print_pdf", mock_cups)
    result = pipeline.run_pipeline(cfg, target_date=DATE, send_to_printer=True)
    assert result.print_result and result.print_result.success
    assert len(called) == 1
    assert called[0][1]["media"] == "Letter"
    assert called[0][0] == result.printable_pdf_path
    assert result.pdf_path != result.printable_pdf_path
    assert validate_pdf(result.pdf_path).ok
    letter_archive = cfg.archive_dir / "20260923-001" / "edition.letter.pdf"
    assert letter_archive.read_bytes() == result.printable_pdf_path.read_bytes()
    assert validate_letter_home(letter_archive) == []
    assert validate_pdf(cfg.archive_dir / "20260923-001" / "edition.pdf").ok
    summary = json.loads((cfg.archive_dir / "20260923-001" / "run.json").read_text())
    assert summary["print_profile"] == "letter-home"


def test_explicit_a4_override_preserves_a4_on_letter_profile(tmp_path, monkeypatch):
    pytest.importorskip("weasyprint")
    pytest.importorskip("pypdf")
    offline_sources(monkeypatch)
    cfg = config(tmp_path)
    cfg.paper_size = "letter"
    called = []
    monkeypatch.setattr(
        pipeline, "print_pdf",
        lambda path, printer, **kwargs: (
            called.append((path, kwargs))
            or PrintResult(True, True, "Synthetic queue acceptance")
        ),
    )
    result = pipeline.run_pipeline(cfg, target_date=DATE, send_to_printer=True,
                                   print_profile="a4-home")
    assert called[0][1]["media"] == "A4"
    assert called[0][0] == result.pdf_path
    assert not (cfg.archive_dir / "20260923-001" / "edition.letter.pdf").exists()
