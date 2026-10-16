from datetime import date

from kushluk.models import PracticalItem, Story
from kushluk.publication import build_publication, publication_markdown


def test_publication_has_stable_machine_id_and_markdown():
    publication = build_publication(
        target_date=date(2026, 9, 23),
        timezone="Europe/Berlin",
        location_name="Cologne",
        practical=[PracticalItem(label="09:30", value="Meeting")],
        stories=[Story(id="s1", headline="Story", deck="Deck", source_name="Source")],
        serial=42,
    )
    assert publication.edition_id == "20260923-042"
    assert publication.schema_version == 2
    assert [page.number for page in publication.pages] == [1, 2, 3, 4]
    assert [page.kind for page in publication.pages] == ["front", "day", "stories", "sources"]
    assert publication.pages[0].story_ids == ["s1"]
    assert publication.to_dict()["pages"][0]["number"] == 1
    markdown = publication_markdown(publication)
    assert "# Kushluk" in markdown
    assert "## Today" in markdown
    assert "## For You" in markdown
