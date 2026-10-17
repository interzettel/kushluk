"""Finite, deterministic editorial composition; independent of theme and paper profile.

Never fetches media or silently removes calendar/task commitments. The archive
stores the chosen archetype and explicit shorten/move/demote/omit decisions.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Literal

from kushluk.models import (
    CompositionBlock, CompositionDecision, EditionPage, LayoutArchetype,
    PracticalItem, SlotBudget, Story,
)


class CompositionCapacityError(ValueError):
    """Cannot fit non-optional user obligations into this four-page edition."""


# A4 logical slots. These are copy budgets, NOT measured WeasyPrint pixel boxes.
# No image can be approved for a print slot until local rights/resolution preflight
# from #50 exists; never fetch arbitrary image URLs during PDF rendering.
RULES = {
    "balanced": {"front_practical": 3, "day_practical": 3, "front_stories": 1,
                 "day_stories": 0, "brief_stories": 3, "lead_deck": 500},
    "news-heavy": {"front_practical": 2, "day_practical": 4, "front_stories": 2,
                   "day_stories": 0, "brief_stories": 3, "lead_deck": 270},
    "practical-heavy": {"front_practical": 4, "day_practical": 4, "front_stories": 0,
                        "day_stories": 1, "brief_stories": 3, "lead_deck": 360},
}
PRACTICAL = SlotBudget(label_chars=34, value_chars=70, detail_chars=118, image_slots=0)
BRIEF = SlotBudget(headline_chars=96, deck_chars=330, image_slots=0)


def choose_archetype(practical: list[PracticalItem], stories: list[Story]) -> LayoutArchetype:
    """Traceable thresholds; no randomness, runtime AI, output theme or printer inputs."""
    relevant = sum(bool(s.headline.strip() and s.source_name.strip()) for s in stories)
    obligations = len(practical)
    if obligations >= 4 and obligations >= relevant + 2:
        return "practical-heavy"
    if relevant >= 3 and obligations <= 2:
        return "news-heavy"
    return "balanced"


def plan_composition_pages(
    practical: list[PracticalItem], stories: list[Story],
    archetype: LayoutArchetype = "balanced",
) -> list[EditionPage]:
    if archetype not in RULES:
        raise ValueError("unknown_archetype")
    rule = RULES[archetype]
    a = min(rule["front_practical"], len(practical))
    b = min(a + rule["day_practical"], len(practical))
    f = min(rule["front_stories"], len(stories))
    d = min(f + rule["day_stories"], len(stories))
    s = min(d + rule["brief_stories"], len(stories))
    pages = [
        EditionPage(1, "front", list(range(a)), [x.id for x in stories[:f]]),
        EditionPage(2, "day", list(range(a, b)), [x.id for x in stories[f:d]]),
        EditionPage(3, "stories", [], [x.id for x in stories[d:s]]),
        EditionPage(4, "sources"),
    ]
    for page in pages[:3]:
        page.blocks = [
            CompositionBlock("practical", str(index), PRACTICAL)
            for index in page.practical_indices
        ]
        for story_id in page.story_ids:
            role = "brief" if page.kind == "stories" else "lead"
            budget = (BRIEF if role == "brief" else SlotBudget(
                headline_chars=96, deck_chars=rule["lead_deck"], image_slots=0,
            ))
            page.blocks.append(CompositionBlock(role, story_id, budget))
    pages[-1].blocks = [
        CompositionBlock("source-index", story.id,
                         SlotBudget(headline_chars=96, value_chars=55, image_slots=0))
        for story in stories[:s]
    ]
    return pages


def fit_text(text: str, limit: int) -> str:
    """Shorten at a whitespace boundary when possible; also handles long unspaced words."""
    normalized = " ".join(text.split())
    if len(normalized) <= limit:
        return normalized
    if limit < 2:
        return "…" if limit else ""
    candidate = normalized[:limit - 1]
    cut = candidate.rfind(" ")
    if cut >= max(12, int(limit * 0.55)):
        candidate = candidate[:cut]
    return candidate.rstrip(" ,;:.-") + "…"


def _practical_rank(item: PracticalItem) -> int:
    kind = item.source.kind if item.source else "other"
    return {"calendar": 0, "task": 1, "weather": 2}.get(kind, 3)


def compose(
    practical: list[PracticalItem], stories: list[Story], *,
    archetype: LayoutArchetype | Literal["auto"] = "auto",
) -> tuple[list[PracticalItem], list[Story], list[EditionPage],
           LayoutArchetype, list[CompositionDecision]]:
    """Fit within slot budgets, preserve included source IDs and explain cuts."""
    selected = choose_archetype(practical, stories) if archetype == "auto" else archetype
    if selected not in RULES:
        raise ValueError("unknown_archetype")
    rule = RULES[selected]
    actions: list[CompositionDecision] = []
    capacity = rule["front_practical"] + rule["day_practical"]
    indexed = sorted(enumerate(practical), key=lambda pair: (_practical_rank(pair[1]), pair[0]))
    required = [x for _, x in indexed if _practical_rank(x) in (0, 1)]
    if len(required) > capacity:
        raise CompositionCapacityError("required_practical_over_capacity")
    retained = indexed[:capacity]
    retained_indices = {i for i, _ in retained}
    for i, _ in enumerate(practical):
        if i not in retained_indices:
            actions.append(CompositionDecision("omit", f"practical:{i}",
                                               "lower-priority optional item over capacity"))
    fitted_practical = []
    for position, (original_index, item) in enumerate(retained):
        label = fit_text(item.label, PRACTICAL.label_chars)
        value = fit_text(item.value, PRACTICAL.value_chars)
        detail = fit_text(item.detail, PRACTICAL.detail_chars) if item.detail else None
        if (label, value, detail) != (item.label, item.value, item.detail):
            actions.append(CompositionDecision(
                "shorten", f"practical:{original_index}", "practical copy budget"))
        if position >= rule["front_practical"]:
            actions.append(CompositionDecision(
                "move", f"practical:{original_index}", "front practical capacity", 1, 2))
        fitted_practical.append(replace(item, label=label, value=value, detail=detail))
    story_cap = rule["front_stories"] + rule["day_stories"] + rule["brief_stories"]
    unique_ids: set[str] = set()
    fitted_stories: list[Story] = []
    for candidate in stories:
        if candidate.id in unique_ids:
            actions.append(CompositionDecision("omit", candidate.id, "duplicate story ID"))
            continue
        unique_ids.add(candidate.id)
        if not candidate.headline.strip() or not candidate.source_name.strip():
            actions.append(CompositionDecision(
                "replace", candidate.id, "invalid or unattributed story; use next ranked candidate"))
            continue
        if len(fitted_stories) >= story_cap:
            actions.append(CompositionDecision(
                "omit", candidate.id, "lower-ranked optional story over four-page capacity"))
            continue
        slot = len(fitted_stories)
        lead = slot < rule["front_stories"] + rule["day_stories"]
        page = (1 if slot < rule["front_stories"]
                else 2 if slot < rule["front_stories"] + rule["day_stories"] else 3)
        headline = fit_text(candidate.headline, BRIEF.headline_chars)
        deck = fit_text(candidate.deck, rule["lead_deck"] if lead else BRIEF.deck_chars)
        source_name = fit_text(candidate.source_name, 55)
        if (headline, deck, source_name) != (
            candidate.headline, candidate.deck, candidate.source_name
        ):
            actions.append(CompositionDecision(
                "shorten", candidate.id, "headline, source or deck slot capacity",
                to_page=page))
        if candidate.image_asset_id:
            actions.append(CompositionDecision(
                "remove_image", candidate.id, "no print-cleared local image slot", to_page=page))
        if page == 3:
            actions.append(CompositionDecision(
                "demote", candidate.id, "secondary story assigned to briefs", 1, 3))
        fitted_stories.append(replace(
            candidate, headline=headline, deck=deck, source_name=source_name,
            image_asset_id=None, image_caption=None,
        ))
    pages = plan_composition_pages(fitted_practical, fitted_stories, selected)
    return fitted_practical, fitted_stories, pages, selected, actions
