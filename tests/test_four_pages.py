from dataclasses import replace
from datetime import date

import pytest

from kushluk.models import PracticalItem, Story
from kushluk.publication import build_publication, plan_pages
from kushluk.renderer import render_html, render_pdf
from kushluk.validation import compact_for_layout, validate_pdf, validate_publication


def edition(stories=None, practical=None):
    return build_publication(
        target_date=date(2026, 9, 23),
        timezone="Europe/Berlin",
        location_name="Cologne",
        practical=practical if practical is not None else [
            PracticalItem("08:30", "Morning routine"),
            PracticalItem("11:00", "Meeting"),
            PracticalItem("14:00", "Read"),
            PracticalItem("18:00", "Dinner"),
        ],
        stories=stories if stories is not None else [
            Story(str(i), f"Headline {i}", f"Useful short summary for story {i}.", "Source")
            for i in range(3)
        ],
    )


def test_page_plan_covers_content_exactly_once():
    pub = edition()
    assert [p.number for p in pub.pages] == [1, 2, 3, 4]
    assert [p.kind for p in pub.pages] == ["front", "day", "stories", "sources"]
    assert [i for page in pub.pages for i in page.practical_indices] == list(
        range(len(pub.practical))
    )
    assert [sid for page in pub.pages for sid in page.story_ids] == [
        story.id for story in pub.stories
    ]
    assert validate_publication(pub).ok


def test_html_renders_four_explicit_sheets_without_missing_story(tmp_path):
    pub = edition()
    html = render_html(pub, tmp_path / "edition.html").read_text(encoding="utf-8")
    assert html.count('class="sheet ') == 4
    for i in range(1, 5):
        assert f'data-page="{i}"' in html
        assert f" {i} / 4" in html
    for story in pub.stories:
        assert html.count(story.headline) == 2  # editorial + source index
    assert "Dinner" in html


def test_empty_source_edition_still_has_four_defined_pages(tmp_path):
    pub = edition(stories=[], practical=[])
    assert validate_publication(pub).ok
    html = render_html(pub, tmp_path / "empty.html").read_text(encoding="utf-8")
    assert html.count('class="sheet ') == 4
    assert "No further stories" in html


def test_stale_page_plan_and_duplicate_story_ids_are_rejected():
    pub = edition()
    assert not validate_publication(replace(pub, pages=[])).ok
    duplicates = replace(pub, stories=[pub.stories[0], pub.stories[0]])
    assert not validate_publication(duplicates).ok


def test_compaction_rebuilds_page_references():
    pub = edition(stories=[
        Story(str(i), f"Headline {i}", "Summary " * 150, "Source") for i in range(3)
    ])
    compacted = compact_for_layout(pub, 2)
    assert len(compacted.stories) == 2
    assert compacted.pages == plan_pages(compacted.practical, compacted.stories)
    assert validate_publication(compacted).ok


@pytest.mark.parametrize("with_stories", [True, False])
def test_weasyprint_pdf_is_exactly_four_portrait_a4_pages(tmp_path, with_stories):
    pytest.importorskip("weasyprint")
    pytest.importorskip("pypdf")
    pub = edition() if with_stories else edition(stories=[], practical=[])
    html_path = render_html(pub, tmp_path / "edition.html")
    pdf_path = render_pdf(html_path, tmp_path / "edition.pdf")
    result = validate_pdf(pdf_path)
    assert result.ok, result.errors
    assert result.page_count == 4


def test_pdf_validator_rejects_swapped_pages(tmp_path):
    pytest.importorskip("weasyprint")
    pypdf = pytest.importorskip("pypdf")
    html_path = render_html(edition(), tmp_path / "edition.html")
    original = render_pdf(html_path, tmp_path / "edition.pdf")
    reader = pypdf.PdfReader(str(original))
    writer = pypdf.PdfWriter()
    for index in [1, 0, 2, 3]:
        writer.add_page(reader.pages[index])
    swapped = tmp_path / "swapped.pdf"
    with swapped.open("wb") as stream:
        writer.write(stream)
    result = validate_pdf(swapped)
    assert not result.ok
    assert any("out-of-order" in error for error in result.errors)


def test_multilingual_long_headlines_render_on_four_pages(tmp_path):
    pytest.importorskip("weasyprint")
    pytest.importorskip("pypdf")
    stories = [
        Story("de", "Stadtentwicklung und die Zukunft unserer gemeinsamen Räume",
              "Eine aktuelle Meldung aus dem Bereich Planung und Gesellschaft.", "Quelle"),
        Story("tr", "Kent yaşamında kamusal alanların dönüşümü ve yeni yaklaşımlar",
              "Kısa bir özet, kaynağı belirtilen bir haberden derlenmiştir.", "Kaynak"),
        Story("mix", "Today's overlooked developments across the city",
              "A short summary with the original source retained.", "Publisher"),
    ]
    pub = edition(stories=stories)
    html = render_html(pub, tmp_path / "multi.html")
    result = validate_pdf(render_pdf(html, tmp_path / "multi.pdf"))
    assert result.ok, result.errors
