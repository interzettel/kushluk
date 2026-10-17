"""Frozen semantic-layout contracts, multilingual cuts and offline PDF proofs."""
from datetime import date

import pytest

from kushluk.composition import (
    CompositionCapacityError, choose_archetype, compose, fit_text,
)
from kushluk.models import PracticalItem, SourceRef, Story
from kushluk.publication import build_publication
from kushluk.renderer import render_html
from kushluk.validation import validate_publication


def stories(number=5, deck="A grounded report from one source."):
    return [
        Story(str(i), f"Editorial headline {i}", deck,
              "Independent source", source_url=f"https://example.org/{i}")
        for i in range(number)
    ]


def practical(number=5):
    return [PracticalItem(f"Reminder {i}", f"Task {i}") for i in range(number)]


def test_deterministic_archetype_selection_from_manifest_not_theme():
    assert choose_archetype(practical(5), stories(1)) == "practical-heavy"
    assert choose_archetype(practical(2), stories(4)) == "news-heavy"
    assert choose_archetype(practical(3), stories(3)) == "balanced"
    assert choose_archetype(practical(3), stories(3)) == "balanced"


@pytest.mark.parametrize("archetype,front_p,front_s,day_s,total", [
    ("balanced", 3, 1, 0, 4),
    ("news-heavy", 2, 2, 0, 5),
    ("practical-heavy", 4, 0, 1, 4),
])
def test_three_archetypes_share_four_canonical_pages_with_explicit_budgets(
    archetype, front_p, front_s, day_s, total,
):
    publication = build_publication(
        target_date=date(2026, 10, 17), timezone="Europe/Berlin", location_name="Berlin",
        practical=practical(5), stories=stories(6), archetype=archetype,
    )
    assert publication.archetype == archetype
    assert [p.kind for p in publication.pages] == ["front", "day", "stories", "sources"]
    assert len(publication.pages[0].practical_indices) == front_p
    assert len(publication.pages[0].story_ids) == front_s
    assert len(publication.pages[1].story_ids) == day_s
    assert len(publication.stories) == total
    assert len(publication.pages[3].blocks) == len(publication.stories)
    all_story_ids = [sid for page in publication.pages[:3] for sid in page.story_ids]
    assert all_story_ids == [s.id for s in publication.stories]
    assert all(b.budget.image_slots == 0 for p in publication.pages for b in p.blocks)
    assert all(b.budget.deck_chars > 0 for p in publication.pages
               for b in p.blocks if b.kind in ("lead", "brief"))
    assert all(b.budget.detail_chars == 118 for p in publication.pages
               for b in p.blocks if b.kind == "practical")
    assert any(x.action == "omit" for x in publication.composition_decisions)
    assert validate_publication(publication).ok


def test_long_german_turkish_compounds_are_clamped_without_resizing_type(tmp_path):
    long_word = "Donaudampfschifffahrtsgesellschaftskapitänlık" * 30
    deck = ("Rücktrittsmöglichkeiten und bağımsızlık hakkında " + long_word) * 25
    long_story = Story("long", long_word, deck, "Synthetic source")
    p = build_publication(
        target_date=date(2026, 10, 17), timezone="Europe/Berlin", location_name="Berlin",
        practical=[PracticalItem(long_word, long_word, long_word)],
        stories=[long_story],
    )
    assert len(p.stories[0].headline) <= 96
    assert len(p.stories[0].deck) <= 500
    assert p.stories[0].headline.endswith("…")
    assert p.practical[0].value.endswith("…")
    assert any(d.action == "shorten" for d in p.composition_decisions)
    html = render_html(p, tmp_path / "multilingual.html").read_text()
    assert "repeat(6, minmax(0, 1fr))" in html
    assert "overflow-wrap: anywhere" in html
    assert "font-size: 7pt" in html
    assert "data-archetype" in html


def test_no_image_is_fetched_or_fabricated_for_unverified_candidate():
    original = Story(
        "s1", "Headline", "Deck", "Source", image_asset_id="unlicensed-asset",
        image_caption="Attribution pending",
    )
    p = build_publication(
        target_date=date(2026, 10, 17), timezone="Europe/Berlin", location_name="Berlin",
        practical=[], stories=[original],
    )
    assert p.stories[0].image_asset_id is None
    assert p.stories[0].image_caption is None
    assert original.image_asset_id == "unlicensed-asset"
    assert any(d.action == "remove_image" for d in p.composition_decisions)


def test_replacement_uses_next_ranked_valid_attributed_story():
    candidates = [
        Story("invalid", "Headline", "Deck", ""),
        Story("candidate2", "Second headline", "Deck", "Publisher"),
        Story("candidate3", "Third headline", "Deck", "Publisher"),
    ]
    _, selected, pages, _, decisions = compose([], candidates)
    assert [x.id for x in selected] == ["candidate2", "candidate3"]
    assert any(x.action == "replace" and x.ref == "invalid" for x in decisions)
    assert pages[0].story_ids == ["candidate2"]


def test_unbounded_required_calendar_is_refused_not_silently_dropped():
    calendar = SourceRef("calendar", "private mock source")
    items = [PracticalItem("Calendar", f"Meeting {n}", source=calendar)
             for n in range(9)]
    with pytest.raises(CompositionCapacityError, match="required_practical_over_capacity"):
        compose(items, stories(1), archetype="practical-heavy")


def test_calendar_priority_over_optional_items_and_move_audit():
    c = PracticalItem("Appointment", "Deadline", source=SourceRef("calendar", "Offline"))
    items = practical(8) + [c]
    chosen, _, _, _, actions = compose(items, stories(2), archetype="practical-heavy")
    assert c in chosen
    assert len(chosen) == 8
    assert any(d.action == "omit" and d.ref.startswith("practical:") for d in actions)
    assert any(d.action == "move" and d.to_page == 2 for d in actions)


def test_whitespace_shortening_is_repeatable():
    text = "One two three four five six seven eight nine ten"
    assert fit_text(text, 20) == fit_text(text, 20)
    assert len(fit_text(text, 20)) <= 20
    assert fit_text("ü" * 80, 18) == "ü" * 17 + "…"


def test_source_reference_preserved_after_composition():
    p = build_publication(
        target_date=date(2026, 10, 17), timezone="Europe/Berlin", location_name="Cologne",
        practical=practical(4), stories=stories(4), archetype="practical-heavy",
    )
    assert {s.source_url for s in p.stories} == {
        f"https://example.org/{i}" for i in range(4)
    }
    assert all(b.ref in {s.id for s in p.stories} for b in p.pages[3].blocks)


def test_visual_proofs_three_pdfs_are_offline_and_each_have_four_marked_pages(tmp_path):
    pytest.importorskip("weasyprint")
    pytest.importorskip("pypdf")
    from tools.layout_compare import build_proofs
    manifest = build_proofs(tmp_path / "proof")
    assert manifest["no_live_sources"] is True
    assert manifest["physical_verified"] is False
    assert set(manifest["archetypes"]) == {
        "balanced", "news-heavy", "practical-heavy",
    }
    for kind, entry in manifest["archetypes"].items():
        assert entry["passed"], (kind, entry)
        assert entry["pages"] == 4
        assert entry["geometry_errors"] == []
        assert entry["pdf_errors"] == []
        assert (tmp_path / "proof" / entry["pdf"]).stat().st_size > 1000
        assert len(entry["source_names"]) == len(entry["included_story_ids"])
    # Same edition content, different placements, no new source claims.
    baseline = manifest["archetypes"]["balanced"]
    other = manifest["archetypes"]["practical-heavy"]
    assert baseline["included_story_ids"] == other["included_story_ids"]
    assert baseline["pages_detail"][0]["story_ids"] != other["pages_detail"][0]["story_ids"]


def test_excess_practical_over_balanced_bounds_never_publishes_a_missing_calendar():
    calendar = SourceRef("calendar", "Offline fixtures")
    many = [PracticalItem("Meeting", str(i), source=calendar) for i in range(7)]
    with pytest.raises(CompositionCapacityError):
        compose(many, stories(2), archetype="balanced")
