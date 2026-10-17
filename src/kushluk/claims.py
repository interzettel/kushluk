"""Narrow factual checks with explicit abstention, never generic AI fact-checking.

Exact DOI title/year are independently *retrieved* from Crossref but the
underlying bibliographic record is usually publisher-deposited. This validates
a metadata assertion, not the paper's conclusions or independent journalism.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from html import unescape
import json
import re
from urllib.parse import quote

from kushluk.feed_network import FeedNetworkError, fetch_public_json


class ClaimCheckError(ValueError):
    """Fixed safe validation errors; no fetched body or credential leaks."""


@dataclass(slots=True)
class ClaimCheck:
    doi: str
    asserted_title: str
    asserted_year: int | None
    state: str
    evidence_url: str
    checked_at: str
    method: str = "crossref-publisher-deposited-metadata"
    claims_about_study_findings_verified: bool = False

    def as_dict(self) -> dict:
        return asdict(self)


def _normal_title(value: str) -> str:
    return " ".join(
        re.sub(r"[^\w]+", " ", unescape(re.sub("<[^>]+>", " ", value)).casefold()).split()
    )


def check_crossref_claim(
    doi: str, *, asserted_title: str, asserted_year: int | None = None,
) -> ClaimCheck:
    if (not isinstance(doi, str) or len(doi) > 160
            or not re.fullmatch(r"10\.\d{4,9}/[^\s?#]+", doi)):
        raise ClaimCheckError("invalid_doi")
    if (not isinstance(asserted_title, str) or not 1 <= len(asserted_title) <= 300
            or not _normal_title(asserted_title)):
        raise ClaimCheckError("invalid_claim_title")
    if asserted_year is not None and (
        type(asserted_year) is not int or not 1800 <= asserted_year <= 2100
    ):
        raise ClaimCheckError("invalid_claim_year")
    pointer = "https://doi.org/" + quote(doi, safe="/")
    base = dict(
        doi=doi.lower(), asserted_title=asserted_title, asserted_year=asserted_year,
        evidence_url=pointer, checked_at=datetime.now(timezone.utc).isoformat(),
    )
    try:
        url = "https://api.crossref.org/works/" + quote(doi, safe="")
        payload = json.loads(fetch_public_json(url, expected_host="api.crossref.org"))
        entry = payload.get("message")
        if (not isinstance(entry, dict) or not isinstance(entry.get("DOI"), str)
                or entry["DOI"].lower() != doi.lower()):
            return ClaimCheck(state="abstain-unmatched-doi", **base)
        title = entry.get("title")
        if not isinstance(title, list) or not title or not isinstance(title[0], str):
            return ClaimCheck(state="abstain-no-title", **base)
        equal = _normal_title(title[0]) == _normal_title(asserted_title)
        if asserted_year is None:
            same_year = True
        else:
            dates = entry.get("published", {}).get("date-parts", [])
            if not (isinstance(dates, list) and dates and
                    isinstance(dates[0], list) and dates[0] and
                    type(dates[0][0]) is int):
                return ClaimCheck(state="abstain-no-year", **base)
            same_year = dates[0][0] == asserted_year
        return ClaimCheck(
            state="bibliographic-match-claims-unverified" if equal and same_year
            else "bibliographic-conflict",
            **base,
        )
    except (FeedNetworkError, ValueError, TypeError, KeyError, UnicodeError, AttributeError):
        # Remote outages, 429 and unparseable records are abstentions, not truth.
        return ClaimCheck(state="abstain-provider-unavailable", **base)
