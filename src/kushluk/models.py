from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Literal


SourceKind = Literal["weather", "calendar", "task", "rss", "newsletter", "other"]
FailureSeverity = Literal["info", "degraded", "failed"]
DeliveryStatus = Literal["skipped", "sent", "failed"]


@dataclass(slots=True)
class SourceRef:
    kind: SourceKind
    name: str
    url: str | None = None
    retrieved_at: str | None = None


@dataclass(slots=True)
class Candidate:
    id: str
    title: str
    summary: str
    source: SourceRef
    published_at: str | None = None
    url: str | None = None
    relevance: float = 0.5
    importance: float = 0.5
    freshness: float = 0.5
    novelty: float = 0.5
    required: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def score(self) -> float:
        if self.required:
            return 1000.0
        return (
            0.35 * self.relevance
            + 0.30 * self.importance
            + 0.20 * self.freshness
            + 0.15 * self.novelty
        )


@dataclass(slots=True)
class StoryCluster:
    id: str
    representative_id: str
    candidate_ids: list[str]
    source_names: list[str]


@dataclass(slots=True)
class PracticalItem:
    label: str
    value: str
    detail: str | None = None
    source: SourceRef | None = None


@dataclass(slots=True)
class Story:
    id: str
    headline: str
    deck: str
    source_name: str
    source_url: str | None = None
    why_selected: str | None = None
    cluster_size: int = 1


@dataclass(slots=True)
class Failure:
    code: str
    severity: FailureSeverity
    message: str
    source: str | None = None
    recoverable: bool = True


@dataclass(slots=True)
class DeliveryResult:
    channel: str
    status: DeliveryStatus
    detail: str


@dataclass(slots=True)
class EditionPage:
    """Logical A4 page; content references canonical item IDs/indices, never copies."""
    number: int
    kind: Literal["front", "day", "stories", "sources"]
    practical_indices: list[int] = field(default_factory=list)
    story_ids: list[str] = field(default_factory=list)


@dataclass(slots=True)
class Publication:
    edition_id: str
    target_date: str
    timezone: str
    generated_at: str
    location_name: str
    practical: list[PracticalItem]
    stories: list[Story]
    lead_story_id: str | None = None
    notes: list[str] = field(default_factory=list)
    schema_version: int = 2
    pages: list[EditionPage] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def now_iso(cls) -> str:
        return datetime.now().astimezone().isoformat(timespec="seconds")
