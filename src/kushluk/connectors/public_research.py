"""Opt-in Crossref public scholarly *metadata* adapter, not article acquisition.

Crossref metadata is not proof of a finding and publisher abstracts may have
separate copyright. We never retrieve abstracts, full text or paywalled pages.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from html import unescape
import json
import re
from urllib.parse import urlencode

from kushluk.feed_network import FeedNetworkError, fetch_public_json, public_article_link
from kushluk.models import Candidate, SourceRef


class ResearchError(ValueError):
    """Only fixed, non-secret-bearing errors leave this adapter."""


class CrossrefMetadataConnector:
    def __init__(self, query: str, *, limit: int = 5):
        if (not isinstance(query, str) or not 3 <= len(query.strip()) <= 80
                or any(ord(c) < 32 for c in query) or limit not in range(1, 6)):
            raise ResearchError("invalid_public_research_query")
        self.query = query.strip()
        self.limit = limit

    def fetch(self) -> list[Candidate]:
        url = "https://api.crossref.org/works?" + urlencode({
            "query.title": self.query, "rows": self.limit,
            "select": "DOI,title,published,URL,type",
        })
        try:
            data = json.loads(fetch_public_json(url, expected_host="api.crossref.org"))
        except (FeedNetworkError, ValueError, UnicodeError) as exc:
            raise ResearchError("public_research_unavailable") from exc
        if (not isinstance(data, dict) or not isinstance(data.get("message"), dict)
                or not isinstance(data["message"].get("items"), list)
                or len(data["message"]["items"]) > self.limit):
            raise ResearchError("invalid_public_research_response")
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        seen: set[str] = set()
        results = []
        for item in data["message"]["items"]:
            if not isinstance(item, dict):
                continue
            doi = item.get("DOI")
            title_list = item.get("title")
            if (not isinstance(doi, str) or not 1 <= len(doi) <= 160
                    or not re.fullmatch(r"10\.\d{4,9}/\S+", doi)
                    or not isinstance(title_list, list) or not title_list
                    or not isinstance(title_list[0], str)):
                continue
            doi_lower = doi.lower()
            if doi_lower in seen:
                continue
            title = " ".join(unescape(re.sub(r"<[^>]*>", " ", title_list[0])).split())
            if not title or len(title) > 180:
                continue
            pointer = public_article_link("https://doi.org/" + doi)
            if not pointer:
                continue
            seen.add(doi_lower)
            parts = item.get("published")
            published = None
            if isinstance(parts, dict):
                dates = parts.get("date-parts")
                if isinstance(dates, list) and dates and isinstance(dates[0], list):
                    values = dates[0]
                    try:
                        if 1 <= len(values) <= 3 and all(type(v) is int for v in values):
                            published = datetime(*list(values + [1] * (3 - len(values))),
                                                 tzinfo=timezone.utc).isoformat()
                    except (TypeError, ValueError):
                        pass
            results.append(Candidate(
                id=sha256(doi_lower.encode()).hexdigest()[:16],
                title=title, summary="", source=SourceRef(
                    kind="other", name="Crossref scholarly metadata",
                    retrieved_at=now,
                ),
                published_at=published, url=pointer,
                relevance=0.4, importance=0.4, freshness=0.4, novelty=0.5,
                metadata={
                    "origin_id": doi_lower, "rights_mode": "reference-only",
                    "transform_mode": "source-pointer",
                    "verification": "unverified-metadata",
                },
            ))
        return results
