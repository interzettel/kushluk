from __future__ import annotations

import hashlib
from urllib.parse import urlsplit, urlunsplit

from kushluk.models import Candidate, Story, StoryCluster, StoryProvenance
from kushluk.feed_network import public_article_link


def cluster_candidates(candidates: list[Candidate]) -> list[tuple[StoryCluster, list[Candidate]]]:
    """Cluster near-duplicate candidates with transparent URL/title heuristics."""
    clusters: list[list[Candidate]] = []
    for candidate in sorted(candidates, key=lambda item: item.score, reverse=True):
        for cluster in clusters:
            if _same_story(candidate, cluster[0]):
                cluster.append(candidate)
                break
        else:
            clusters.append([candidate])

    result: list[tuple[StoryCluster, list[Candidate]]] = []
    for items in clusters:
        representative = max(items, key=lambda item: item.score)
        identity = "|".join(sorted(item.id for item in items))
        cluster_id = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16]
        result.append(
            (
                StoryCluster(
                    id=cluster_id,
                    representative_id=representative.id,
                    candidate_ids=[item.id for item in items],
                    source_names=list(dict.fromkeys(item.source.name for item in items)),
                ),
                items,
            )
        )
    return result


def select_stories(candidates: list[Candidate], limit: int = 3) -> list[Story]:
    clusters = cluster_candidates(candidates)
    clusters.sort(
        key=lambda cluster_and_items: max(item.score for item in cluster_and_items[1]),
        reverse=True,
    )

    stories: list[Story] = []
    for cluster, items in clusters[:limit]:
        candidate = max(items, key=lambda item: item.score)
        coverage = (
            f"; {len(cluster.source_names)} source(s) in cluster"
            if len(cluster.candidate_ids) > 1
            else ""
        )
        def provenance(entry: Candidate) -> StoryProvenance:
            origin = entry.metadata.get("origin_id")
            return StoryProvenance(
                candidate_id=entry.id,
                origin_ref=origin[:160] if isinstance(origin, str) else None,
                source_name=entry.source.name[:100],
                source_kind=entry.source.kind,
                url=public_article_link(entry.url),
                published_at=entry.published_at,
                retrieved_at=entry.source.retrieved_at,
                transform_mode="source-pointer",
                rights_mode="reference-only",
            )

        evidence = [provenance(entry) for entry in items[:12]]
        # Multiple near-duplicate titles do not establish independent fact-checking.
        titles = {" ".join(entry.title.casefold().split()) for entry in items}
        verification = (
            "unverified-source-pointer" if len(evidence) == 1
            else "potential-title-conflict" if len(titles) > 1
            else "multi-source-unverified"
        )
        stories.append(
            Story(
                id=cluster.id,
                headline=candidate.title,
                deck=candidate.summary or "Open the source for the full story.",
                source_name=candidate.source.name,
                source_url=public_article_link(candidate.url),
                provenance=evidence,
                verification_state=verification,
                cluster_size=len(cluster.candidate_ids),
                why_selected=(
                    f"score {candidate.score:.2f}: relevance {candidate.relevance:.2f}, "
                    f"importance {candidate.importance:.2f}, freshness {candidate.freshness:.2f}, "
                    f"novelty {candidate.novelty:.2f}{coverage}"
                ),
            )
        )
    return stories


def _same_story(left: Candidate, right: Candidate) -> bool:
    if left.url and right.url and _canonical_url(left.url) == _canonical_url(right.url):
        return True
    left_tokens = _title_tokens(left.title)
    right_tokens = _title_tokens(right.title)
    if not left_tokens or not right_tokens:
        return False
    overlap = len(left_tokens & right_tokens)
    union = len(left_tokens | right_tokens)
    return union > 0 and overlap / union >= 0.72


def _canonical_url(value: str) -> str:
    parts = urlsplit(value)
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip("/"), "", ""))


def _title_tokens(title: str) -> set[str]:
    normalized = " ".join(
        "".join(ch.lower() if ch.isalnum() else " " for ch in title).split()
    )
    return {token for token in normalized.split() if len(token) > 2}
