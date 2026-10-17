from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from datetime import date
from pathlib import Path
from typing import Callable

from kushluk.archive import archive_publication
from kushluk.config import Settings
from kushluk.connectors.calendar_fixture import CalendarFixtureConnector
from kushluk.connectors.calendar_ics import ICSCalendarConnector
from kushluk.connectors.rss import RSSConnector
from kushluk.connectors.weather import OpenMeteoWeatherConnector
from kushluk.delivery import send_email_edition
from kushluk.editor import select_stories
from kushluk.models import DeliveryResult, Failure, FailureSeverity, Publication
from kushluk.printing import PrintResult, print_pdf
from kushluk.print_profiles import impose_a3_folded
from kushluk.publication import build_publication, publication_markdown
from kushluk.renderer import render_html, render_pdf
from kushluk.validation import compact_for_layout, validate_pdf, validate_publication


@dataclass(slots=True)
class PipelineResult:
    publication: Publication
    markdown_path: Path
    html_path: Path
    pdf_path: Path | None
    printable_pdf_path: Path | None
    archive_dir: Path
    print_result: PrintResult | None
    email_result: DeliveryResult | None
    failures: list[Failure]

    @property
    def warnings(self) -> list[str]:
        return [failure.message for failure in self.failures if failure.severity != "info"]


def run_pipeline(
    settings: Settings,
    *,
    target_date: date,
    make_pdf: bool = True,
    send_to_printer: bool = False,
    send_email: bool = False,
    email_on_print_failure: bool = False,
    print_profile: str = "a4-home",
    before_delivery: Callable[[str], None] | None = None,
    on_stage: Callable[[str], None] | None = None,
) -> PipelineResult:
    if print_profile not in {"a4-home", "a3-folded"}:
        raise ValueError(f"Unknown print profile: {print_profile}")
    failures: list[Failure] = []
    practical = []

    try:
        practical.extend(
            OpenMeteoWeatherConnector(
                settings.latitude,
                settings.longitude,
                settings.timezone,
                settings.home_name,
            ).fetch()
        )
    except Exception as exc:
        failures.append(_failure("weather_unavailable", "degraded", exc, "weather"))

    if settings.calendar_ics:
        try:
            practical.extend(
                ICSCalendarConnector(
                    settings.calendar_ics,
                    target_date,
                    settings.timezone,
                ).fetch()
            )
        except Exception as exc:
            failures.append(_failure("calendar_ics_unavailable", "degraded", exc, "calendar"))
            _load_calendar_fixture(settings, practical, failures)
    else:
        _load_calendar_fixture(settings, practical, failures)

    candidates = []
    rss_connector = RSSConnector(
        settings.rss_urls, reference_only_urls=settings.reference_only_rss_urls,
    )
    try:
        candidates.extend(rss_connector.fetch())
    except Exception as exc:
        failures.append(_failure("rss_unavailable", "degraded", exc, "rss"))
    for rejected in rss_connector.failed_feeds:
        failures.append(Failure(
            code="rss_feed_unavailable",
            severity="degraded",
            message=(
                f"RSS source {rejected['feed_number']} skipped "
                f"({rejected['reason']})."
            ),
            source="rss",
        ))

    if on_stage is not None:
        on_stage("sources_complete")

    # Keep a larger ranked candidate pool so the composer can replace unfit leads.
    stories = select_stories(candidates, limit=6)
    if not stories:
        failures.append(
            Failure(
                code="no_editorial_stories",
                severity="degraded",
                message="No editorial stories were selected.",
                source="editorial",
            )
        )

    publication = build_publication(
        target_date=target_date,
        timezone=settings.timezone,
        location_name=settings.home_name,
        practical=practical,
        stories=stories,
        archetype="auto",
        media_store=settings.media_dir,
        notes=[failure.message for failure in failures if failure.severity != "info"],
    )

    if on_stage is not None:
        on_stage("editorial_complete")

    preflight = validate_publication(publication)
    for message in preflight.errors:
        failures.append(
            Failure("publication_invalid", "failed", message, source="validation", recoverable=False)
        )
    for message in preflight.warnings:
        failures.append(Failure("publication_warning", "info", message, source="validation"))

    settings.output_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = settings.output_dir / f"{publication.edition_id}.md"
    html_path = settings.output_dir / f"{publication.edition_id}.html"
    pdf_path = settings.output_dir / f"{publication.edition_id}.pdf"

    rendered_pdf: Path | None = None
    if make_pdf and preflight.ok:
        working = publication
        for attempt in range(4):
            if on_stage is not None:
                on_stage("rendering")
            render_html(working, html_path, media_store=settings.media_dir)
            try:
                candidate_pdf = render_pdf(html_path, pdf_path)
                if on_stage is not None:
                    on_stage("rendered")
                pdf_validation = validate_pdf(candidate_pdf, expected_pages=4)
            except Exception as exc:
                failures.append(_failure("pdf_unavailable", "degraded", exc, "renderer"))
                break

            if pdf_validation.ok:
                publication = working
                rendered_pdf = candidate_pdf
                if on_stage is not None:
                    on_stage("validated")
                break

            if attempt == 3:
                failures.append(
                    Failure(
                        code="layout_overflow",
                        severity="failed",
                        message=pdf_validation.errors[0],
                        source="renderer",
                        recoverable=False,
                    )
                )
                overflow_path = pdf_path.with_suffix(".overflow.pdf")
                if candidate_pdf.exists():
                    candidate_pdf.replace(overflow_path)
                publication = working
                break

            failures.append(
                Failure(
                    code="layout_compacted",
                    severity="info",
                    message=(
                        f"PDF rendered to {pdf_validation.page_count} pages; "
                        f"applying editorial cut pass {attempt + 1}."
                    ),
                    source="renderer",
                )
            )
            working = compact_for_layout(working, attempt + 1)
    else:
        if on_stage is not None:
            on_stage("rendering")
        render_html(publication, html_path, media_store=settings.media_dir)
        if on_stage is not None:
            on_stage("rendered")

    publication = replace(
        publication,
        notes=[failure.message for failure in failures if failure.severity == "degraded"],
    )
    markdown_path.write_text(publication_markdown(publication), encoding="utf-8")

    if rendered_pdf is None:
        render_html(publication, html_path, media_store=settings.media_dir)

    printable_pdf: Path | None = rendered_pdf
    if print_profile == "a3-folded" and rendered_pdf:
        try:
            printable_pdf = impose_a3_folded(
                rendered_pdf, settings.output_dir / f"{publication.edition_id}.a3-folded.pdf"
            )
        except (ValueError, OSError, ImportError) as exc:
            printable_pdf = None
            failures.append(_failure("imposition_failed", "failed", exc, "imposition"))

    # Persist the validated editorial snapshot BEFORE any external side effect.
    # A process may die inside CUPS/SMTP; the original edition must survive.
    archive_publication(
        publication,
        settings.archive_dir,
        html_path=html_path,
        pdf_path=rendered_pdf,
        imposed_pdf_path=printable_pdf if print_profile == "a3-folded" else None,
        media_store=settings.media_dir,
        run_summary={
            "stage": "prepared",
            "validated_pdf": bool(rendered_pdf),
            "print_profile": print_profile,
            "printable_pdf": printable_pdf.name if printable_pdf else None,
        },
    )
    if on_stage is not None:
        on_stage("archive_ready")

    print_result: PrintResult | None = None
    if send_to_printer:
        if printable_pdf:
            if before_delivery is not None:
                before_delivery("print")
            print_result = print_pdf(
                printable_pdf, settings.printer, execute=True,
                media="A3" if print_profile == "a3-folded" else "A4",
                duplex_edge="short" if print_profile == "a3-folded" else "long",
                require_duplex=print_profile == "a3-folded",
            )
            if on_stage is not None:
                on_stage("print_submitted" if print_result.success else "print_failed")
            if not print_result.success:
                failures.append(
                    Failure(
                        code="print_failed",
                        severity="failed",
                        message=print_result.detail,
                        source="printer",
                    )
                )
        else:
            print_result = PrintResult(
                True, False, "Print skipped: validated PDF or requested imposed print profile is unavailable."
            )
            failures.append(
                Failure(
                    code="print_skipped",
                    severity="failed",
                    message=print_result.detail,
                    source="printer",
                )
            )

    should_email = send_email or (
        email_on_print_failure and print_result is not None and not print_result.success
    )
    email_result: DeliveryResult | None = None
    if should_email:
        if before_delivery is not None:
            before_delivery("email")
        email_result = send_email_edition(
            publication,
            host=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_username,
            password=settings.smtp_password,
            sender=settings.smtp_from,
            recipient=settings.email_to,
            starttls=settings.smtp_starttls,
            html_path=html_path,
            pdf_path=rendered_pdf,
        )
        if on_stage is not None:
            on_stage("email_sent" if email_result.status == "sent" else "email_failed")
        if email_result.status == "failed":
            failures.append(
                Failure(
                    code="email_failed",
                    severity="failed",
                    message=email_result.detail,
                    source="email",
                )
            )

    run_summary = {
        "failures": [asdict(failure) for failure in failures],
        "print": asdict(print_result) if print_result else None,
        "email": asdict(email_result) if email_result else None,
        "validated_pdf": bool(rendered_pdf),
        "print_profile": print_profile,
        "printable_pdf": printable_pdf.name if printable_pdf else None,
    }
    archive_dir = archive_publication(
        publication,
        settings.archive_dir,
        html_path=html_path,
        pdf_path=rendered_pdf,
        imposed_pdf_path=printable_pdf if print_profile == "a3-folded" else None,
        run_summary=run_summary,
    )
    if on_stage is not None:
        on_stage("complete")
    return PipelineResult(
        publication=publication,
        markdown_path=markdown_path,
        html_path=html_path,
        pdf_path=rendered_pdf,
        printable_pdf_path=printable_pdf,
        archive_dir=archive_dir,
        print_result=print_result,
        email_result=email_result,
        failures=failures,
    )


def _load_calendar_fixture(
    settings: Settings,
    practical: list,
    failures: list[Failure],
) -> None:
    try:
        practical.extend(CalendarFixtureConnector(settings.calendar_fixture).fetch())
    except Exception as exc:
        failures.append(_failure("calendar_unavailable", "degraded", exc, "calendar"))


def _failure(
    code: str,
    severity: FailureSeverity,
    exc: Exception,
    source: str,
) -> Failure:
    return Failure(
        code=code,
        severity=severity,
        message=f"{source} unavailable ({code}). Check local diagnostics; private provider errors are never archived.",
        source=source,
    )
