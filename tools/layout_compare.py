"""Generate three side-by-side editorial proofs from one immutable synthetic edition.

Usage: python -m tools.layout_compare --output-dir output/layout-compare
Offline: never calls feeds, calendars, SMTP, printer or external image URLs.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import date
import json
from pathlib import Path

from kushluk.layout_inspection import inspect_html_fit
from kushluk.models import PracticalItem, SourceRef, Story
from kushluk.publication import build_publication
from kushluk.renderer import render_html, render_pdf
from kushluk.validation import validate_pdf


FIXED_DATE = date(2026, 10, 17)
ARCHETYPES = ("balanced", "news-heavy", "practical-heavy")


def fixed_edition():
    day_source = SourceRef(kind="calendar", name="Offline calendar")
    weather_source = SourceRef(kind="weather", name="Offline conditions")
    practical = [
        PracticalItem("Calendar", "09:00 — Design review", "A short planning session", day_source),
        PracticalItem("Deadline", "14:30 — Team update",
                      "Vierzehn-Tage-Planung und neue Bauteilanforderungen", day_source),
        PracticalItem("Weather", "Cloudy · 14°C", "Pack a light jacket", weather_source),
        PracticalItem("Tasks", "Check three drafts", "Prepare notes before lunch"),
        PracticalItem("Reminder", "Evening walk", "Remember the bag and house keys"),
    ]
    stories = [
        Story("fixed-1", "Wie Städte und digitale Planung zusammenfinden",
              "Diese Testnachricht ist kein echtes Ereignis. " * 22,
              "Synthetic publisher A", source_url="https://example.invalid/one",
              image_asset_id="no-approved-image", image_caption="Unavailable caption"),
        Story("fixed-2", "Küresel dönüşümlerde şehir tasarımının geleceği",
              "Bu metin yalnızca baskı düzenini test etmek için hazırlanmıştır. " * 17,
              "Synthetic publisher B", source_url="https://example.invalid/two"),
        Story("fixed-3", "Architecture as a network of relationships",
              "A synthetic caption-free brief about urban systems and the relevance of space.",
              "Synthetic publisher C", source_url="https://example.invalid/three"),
        Story("fixed-4", "A short useful thing",
              "A small fixed editorial story whose source remains attributable.",
              "Synthetic publisher D", source_url="https://example.invalid/four"),
        Story("fixed-5", "Lower ranked extra",
              "This story is intentionally omitted if no editorial capacity remains.",
              "Synthetic publisher E", source_url="https://example.invalid/five"),
    ]
    return practical, stories


def build_proofs(output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    practical, stories = fixed_edition()
    evidence = {"schema_version": 1, "edition_id": "20261017-001",
                "synthetic_fixture": True, "physical_verified": False,
                "no_live_sources": True, "archetypes": {}}
    for archetype in ARCHETYPES:
        stem = f"kushluk-{archetype}"
        target_html = output_dir / f"{stem}.html"
        target_pdf = output_dir / f"{stem}.pdf"
        if target_html.exists() or target_pdf.exists():
            raise FileExistsError("layout_proof_exists")
        edition = build_publication(
            target_date=FIXED_DATE, timezone="Europe/Berlin", location_name="Sample city",
            practical=practical, stories=stories, archetype=archetype,
        )
        # Identical ID, input, date and timestamp for all variants.
        edition.generated_at = "2026-10-17T07:00:00+02:00"
        render_html(edition, target_html)
        rendered = render_pdf(target_html, target_pdf)
        pdf = validate_pdf(rendered, expected_pages=4)
        boxes = inspect_html_fit(target_html)
        sample = {
            "passed": pdf.ok and boxes.ok,
            "pages": pdf.page_count,
            "pdf_errors": pdf.errors,
            "geometry_errors": boxes.issues,
            "min_font_css_px": boxes.min_text_font_css_px,
            "archetype": edition.archetype,
            "included_story_ids": [s.id for s in edition.stories],
            "source_names": [s.source_name for s in edition.stories],
            "practical_count": len(edition.practical),
            "source_attributions": len(edition.pages[3].story_ids)
                if edition.pages[3].story_ids else len(edition.pages[3].blocks),
            "pages_detail": [
                {"number": page.number, "kind": page.kind,
                 "practical_indices": page.practical_indices,
                 "story_ids": page.story_ids,
                 "blocks": [asdict(b) for b in page.blocks]}
                for page in edition.pages
            ],
            "decisions": [asdict(x) for x in edition.composition_decisions],
            "html": target_html.name,
            "pdf": target_pdf.name,
        }
        evidence["archetypes"][archetype] = sample
    (output_dir / "comparison.json").write_text(
        json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if not all(row["passed"] for row in evidence["archetypes"].values()):
        raise RuntimeError("One or more layout proofs failed geometry validation")
    return evidence


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("output/layout-compare"))
    args = parser.parse_args(argv)
    proof = build_proofs(args.output_dir)
    print(json.dumps({
        "status": "passed", "variant_count": len(proof["archetypes"]),
        "page_counts": {name: entry["pages"] for name, entry in proof["archetypes"].items()},
        "physical_verified": False,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
