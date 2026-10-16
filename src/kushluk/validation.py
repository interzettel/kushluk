from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
import re
from urllib.parse import urlparse

from kushluk.models import PracticalItem, Publication, Story
from kushluk.publication import plan_pages


@dataclass(slots=True)
class ValidationResult:
    errors: list[str]
    warnings: list[str]
    page_count: int | None = None

    @property
    def ok(self) -> bool:
        return not self.errors


def validate_publication(publication: Publication) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    if not publication.edition_id.strip():
        errors.append("Edition ID is required.")
    if not publication.target_date.strip():
        errors.append("Target date is required.")
    if publication.schema_version != 2:
        errors.append("Publication schema must be version 2.")
    if len(publication.pages) != 4 or publication.pages != plan_pages(
        publication.practical, publication.stories
    ):
        errors.append("Edition must contain four canonical, correctly ordered logical A4 pages.")
    if len({story.id for story in publication.stories}) != len(publication.stories):
        errors.append("Story IDs must be unique across the edition.")
    if not publication.location_name.strip():
        warnings.append("Location name is empty.")
    if len(publication.practical) > 6:
        warnings.append("More than six practical items may overflow the A4 layout.")
    if len(publication.stories) > 3:
        warnings.append("More than three stories may overflow the A4 layout.")

    for story in publication.stories:
        if story.source_url and not _is_http_url(story.source_url):
            warnings.append(f"Story '{story.headline}' has a non-HTTP source URL.")
        if len(story.deck) > 1200:
            warnings.append(f"Story '{story.headline}' has an unusually long deck.")

    return ValidationResult(errors=errors, warnings=warnings)


def compact_for_layout(publication: Publication, pass_number: int) -> Publication:
    """Return a more compact edition without shrinking typography."""
    stories = [_compact_story(story, index) for index, story in enumerate(publication.stories)]
    practical = [_compact_practical(item) for item in publication.practical[:6]]

    if pass_number >= 2 and len(stories) > 2:
        stories = stories[:2]
    if pass_number >= 3 and len(stories) > 1:
        stories = stories[:1]

    return replace(publication, practical=practical, stories=stories, pages=plan_pages(practical, stories))


def pdf_page_count(pdf_path: Path) -> int:
    from pypdf import PdfReader

    return len(PdfReader(str(pdf_path)).pages)


def validate_pdf(pdf_path: Path, expected_pages: int = 4) -> ValidationResult:
    count = pdf_page_count(pdf_path)
    errors = [] if count == expected_pages else [
        f"Expected {expected_pages} PDF page(s), got {count}."
    ]
    if not errors:
        from pypdf import PdfReader

        reader = PdfReader(str(pdf_path))
        for number, page in enumerate(reader.pages, start=1):
            box = page.mediabox
            width, height = float(box.width), float(box.height)
            # A4 portrait in PDF points = 595.28 x 841.89; allow renderer rounding.
            if abs(width - 595.28) > 2 or abs(height - 841.89) > 2:
                errors.append(
                    f"Logical page {number} is not portrait A4 ({width:.1f} x {height:.1f}pt)."
                )
            # The final page marker is embedded in each page, not just inferred
            # from PDF order. Catch swapped/missing content and blank sheets.
            content = page.extract_text() or ""
            if not re.search(rf"\b{number}\s*/\s*4\b", content):
                errors.append(f"Missing or out-of-order logical page marker on page {number}.")
    return ValidationResult(errors=errors, warnings=[], page_count=count)


def _compact_story(story: Story, index: int) -> Story:
    limit = 520 if index == 0 else 300
    return replace(story, deck=_truncate(story.deck, limit))


def _compact_practical(item: PracticalItem) -> PracticalItem:
    detail = _truncate(item.detail, 120) if item.detail else None
    return replace(item, detail=detail)


def _truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    shortened = text[: max(0, limit - 1)].rstrip()
    return shortened + "…"


def _is_http_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
