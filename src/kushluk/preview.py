"""Frozen, synthetic four-page installer preview — never reads private sources.

A preview is an offline structural sample, not a physical printer test. It is
installed in the wheel and sdist so it can run without a repository checkout.
"""
from __future__ import annotations

from datetime import date
from hashlib import sha256
import json
from pathlib import Path

from kushluk.models import PracticalItem, SourceRef, Story
from kushluk.publication import build_publication, publication_markdown
from kushluk.renderer import render_html, render_pdf
from kushluk.validation import validate_pdf, validate_publication

FIXTURE_VERSION = 1
FROZEN_AT = "2026-10-17T07:00:00+02:00"
FIXTURE_DAY = date(2026, 10, 17)


class PreviewError(ValueError):
    """Fixed public error codes; no absolute private paths or private data."""


def frozen_publication():
    """Original fictitious material. No scraped text, URLs, inbox or credentials."""
    local = SourceRef(kind="other", name="Original Kushluk synthetic sample")
    practical = [
        PracticalItem(
            "Today", "09:30 — Design review",
            "Fictional appointment for an offline software demonstration",
            SourceRef("calendar", "Synthetic calendar"),
        ),
        PracticalItem(
            "To do", "Review a sample layout",
            "A fictitious task — not from any connected account",
            SourceRef("task", "Synthetic task list"),
        ),
        PracticalItem(
            "Forecast", "18°C · Light clouds",
            "Illustrative weather only, not an observation",
            SourceRef("weather", "Synthetic weather"),
        ),
        PracticalItem(
            "Later", "17:00 — Evening walk",
            "No external itinerary was read", local,
        ),
    ]
    stories = [
        Story(
            "synthetic-lead",
            "A quieter way to read the morning",
            "This four-page sample demonstrates a compact editorial rhythm. "
            "Its stories and schedules are entirely fabricated as fixture text "
            "and make no assertions about current events.",
            "Original Kushluk synthetic sample",
        ),
        Story(
            "synthetic-brief-one",
            "A deliberately finite reading list",
            "Three original test stories can exercise article and source slots "
            "without downloading or reproducing anyone else's work.",
            "Original Kushluk synthetic sample",
        ),
        Story(
            "synthetic-brief-two",
            "Paper still needs human inspection",
            "A correctly rendered PDF does not confirm duplex orientation, "
            "real printer behavior, legibility or a successful unattended run.",
            "Original Kushluk synthetic sample",
        ),
    ]
    publication = build_publication(
        target_date=FIXTURE_DAY, timezone="Europe/Berlin",
        location_name="SYNTHETIC EDITION — NOT LIVE NEWS",
        practical=practical, stories=stories,
        archetype="balanced",
        notes=["Offline synthetic preview; no external sources or devices were used."],
    )
    publication.generated_at = FROZEN_AT
    return publication


def make_preview(output_dir: Path, *, pdf: bool = False) -> dict:
    """Write a fixed preview only to a new/empty destination; no overwrite."""
    if pdf:
        try:
            import weasyprint  # noqa: F401
            import pypdf  # noqa: F401
        except (ImportError, OSError) as exc:
            raise PreviewError("pdf_dependencies_required") from exc
    if output_dir.is_symlink() or (output_dir.exists() and not output_dir.is_dir()):
        raise PreviewError("unsafe_preview_destination")
    if output_dir.exists() and any(output_dir.iterdir()):
        raise PreviewError("preview_destination_not_empty")
    output_dir.mkdir(parents=True, exist_ok=True)
    publication = frozen_publication()
    result = validate_publication(publication)
    if not result.ok:
        raise PreviewError("invalid_synthetic_publication")

    html = render_html(publication, output_dir / "kushluk-preview.html")
    markdown = output_dir / "kushluk-preview.md"
    markdown.write_text(publication_markdown(publication), encoding="utf-8")
    metadata = output_dir / "kushluk-preview-edition.json"
    metadata.write_text(
        json.dumps(publication.to_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    files = [html, markdown, metadata]
    if pdf:
        try:
            rendered = render_pdf(html, output_dir / "kushluk-preview.pdf")
            check = validate_pdf(rendered, expected_pages=4)
            if not check.ok:
                raise PreviewError("invalid_four_page_preview_pdf")
            files.append(rendered)
        except ImportError as exc:
            raise PreviewError("pdf_dependencies_required") from exc
        except RuntimeError as exc:
            raise PreviewError("pdf_dependencies_required") from exc
    manifest = {
        "schema_version": 1,
        "fixture_version": FIXTURE_VERSION,
        "fixture_date": FIXTURE_DAY.isoformat(),
        "fixture_generated_at": FROZEN_AT,
        "edition_id": publication.edition_id,
        "four_logical_a4_pages": len(publication.pages) == 4,
        "pdf_validated": pdf,
        "network_requests": 0,
        "printer_submissions": 0,
        "mail_submissions": 0,
        "synthetic_only": True,
        "physical_verified": False,
        "files": {p.name: sha256(p.read_bytes()).hexdigest() for p in files},
    }
    (output_dir / "preview-manifest.json").write_text(
        json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8",
    )
    return manifest
