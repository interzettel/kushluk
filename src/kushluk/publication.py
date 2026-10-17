from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

from kushluk.models import EditionPage, LayoutArchetype, PracticalItem, Publication, Story
from kushluk.composition import compose, plan_composition_pages


def plan_pages(
    practical: list[PracticalItem], stories: list[Story],
    archetype: LayoutArchetype = "balanced",
) -> list[EditionPage]:
    """Four fixed A4 kinds; archetype changes semantic allocation, never sheet count."""
    return plan_composition_pages(practical, stories, archetype)


def build_publication(
    *,
    target_date: date,
    timezone: str,
    location_name: str,
    practical: list[PracticalItem],
    stories: list[Story],
    serial: int = 1,
    notes: list[str] | None = None,
    archetype: LayoutArchetype | str = "balanced",
) -> Publication:
    edition_id = f"{target_date:%Y%m%d}-{serial:03d}"
    generated_at = datetime.now(ZoneInfo(timezone)).isoformat(timespec="seconds")
    fitted_practical, fitted_stories, pages, selected, decisions = compose(
        practical, stories, archetype=archetype,
    )
    return Publication(
        edition_id=edition_id,
        target_date=target_date.isoformat(),
        timezone=timezone,
        generated_at=generated_at,
        location_name=location_name,
        practical=fitted_practical,
        stories=fitted_stories,
        notes=notes or [],
        pages=pages,
        archetype=selected,
        composition_decisions=decisions,
    )


def publication_markdown(publication: Publication) -> str:
    lines = [
        "---",
        f"edition_id: {publication.edition_id}",
        f"date: {publication.target_date}",
        f"timezone: {publication.timezone}",
        f"generated_at: {publication.generated_at}",
        f"schema_version: {publication.schema_version}",
        f"archetype: {publication.archetype}",
        f"logical_pages: {len(publication.pages)}",
        "---",
        "",
        "# Kushluk",
        "",
        f"**{publication.location_name} · {publication.target_date} · {publication.edition_id}**",
        "",
        "## Today",
        "",
    ]
    if publication.practical:
        for item in publication.practical:
            detail = f" — {item.detail}" if item.detail else ""
            lines.append(f"- **{item.label}:** {item.value}{detail}")
    else:
        lines.append("- No practical items available.")

    lines.extend(["", "## For You", ""])
    for story in publication.stories:
        lines.append(f"### {story.headline}")
        lines.append("")
        lines.append(story.deck)
        lines.append("")
        source = story.source_name
        if story.source_url:
            source = f"[{source}]({story.source_url})"
        lines.append(f"Source: {source}")
        lines.append("")
    if publication.notes:
        lines.extend(["## Notes", ""] + [f"- {note}" for note in publication.notes])
    return "\n".join(lines).rstrip() + "\n"
