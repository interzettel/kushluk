from datetime import date

from kushluk.models import Publication, Story
from kushluk.publication import plan_pages
from kushluk.validation import compact_for_layout, validate_publication


def publication(stories):
    return Publication(
        edition_id="20260923-001",
        target_date=date(2026, 9, 23).isoformat(),
        timezone="Europe/Berlin",
        generated_at="2026-09-23T08:00:00+02:00",
        location_name="Cologne",
        practical=[],
        stories=stories,
        pages=plan_pages([], stories),
    )


def test_compaction_shortens_copy_before_dropping_stories():
    stories = [
        Story(str(i), f"Story {i}", "x" * 900, "Source", "https://example.com")
        for i in range(3)
    ]
    first = compact_for_layout(publication(stories), 1)
    assert len(first.stories) == 3
    assert len(first.stories[0].deck) <= 520
    second = compact_for_layout(first, 2)
    assert len(second.stories) == 2


def test_validation_warns_about_bad_source_url():
    item = Story("1", "Story", "Deck", "Source", "mailto:test@example.com")
    result = validate_publication(publication([item]))
    assert result.ok
    assert any("non-HTTP" in warning for warning in result.warnings)
