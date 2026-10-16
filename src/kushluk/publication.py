from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

from kushluk.models import EditionPage, PracticalItem, Publication, Story


def plan_pages(practical: list[PracticalItem], stories: list[Story]) -> list[EditionPage]:
    """Deterministic four-page reading order independent of printer and imposition."""
    return [
        EditionPage(1, "front", list(range(min(3, len(practical)))), [s.id for s in stories[:1]]),
        EditionPage(2, "day", list(range(3, len(practical)))),
        EditionPage(3, "stories", story_ids=[s.id for s in stories[1:]]),
        EditionPage(4, "sources"),
    ]


def build_publication(
    *,
    target_date: date,
    timezone: str,
    location_name: str,
    practical: list[PracticalItem],
    stories: list[Story],
    serial: int = 1,
    notes: list[str] | None = None,
) -> Publication:
    edition_id = f"{target_date:%Y%m%d}-{serial:03d}"
    generated_at = datetime.now(ZoneInfo(timezone)).isoformat(timespec="seconds")
    return Publication(
        edition_id=edition_id,
        target_date=target_date.isoformat(),
        timezone=timezone,
        generated_at=generated_at,
        location_name=location_name,
        practical=practical,
        stories=stories,
        notes=notes or [],
        pages=plan_pages(practical, stories),
    )


def publication_markdown(publication: Publication) -> str:
    lines = [
        "---",
        f"edition_id: {publication.edition_id}",
        f"date: {publication.target_date}",
        f"timezone: {publication.timezone}",
        f"generated_at: {publication.generated_at}",
        f"schema_version: {publication.schema_version}",
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
