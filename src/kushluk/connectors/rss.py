from __future__ import annotations

import hashlib
import html
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.request import Request, urlopen

from kushluk.models import Candidate, SourceRef


class RSSConnector:
    def __init__(self, urls: tuple[str, ...], per_feed: int = 12,
                 reference_only_urls: tuple[str, ...] = ()) -> None:
        self.urls = urls
        self.per_feed = per_feed
        self.reference_only_urls = frozenset(reference_only_urls)

    def fetch(self) -> list[Candidate]:
        candidates: list[Candidate] = []
        for url in self.urls:
            request = Request(
                url,
                headers={
                    "User-Agent": "Kushluk/0.1 (+https://github.com/yigit-denktas/kushluk)"
                },
            )
            # The URL comes from explicit Kushluk configuration.
            with urlopen(request, timeout=12) as response:
                xml_bytes = response.read()
            root = ET.fromstring(xml_bytes)
            source_name = _feed_title(root) or url
            source = SourceRef(
                kind="rss",
                name=source_name,
                url=url,
                retrieved_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            )
            for raw in _entries(root)[: self.per_feed]:
                title = _clean(raw.get("title") or "Untitled")
                link = raw.get("link") or ""
                # Reference-only feeds must not ingest, summarize or embed
                # publisher-provided article body/description in a newspaper.
                summary = ("" if url in self.reference_only_urls
                           else _clean(raw.get("summary") or ""))
                published_iso = _parse_time(raw.get("published"))
                identity = link or f"{source_name}:{title}"
                candidate_id = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16]
                candidates.append(
                    Candidate(
                        id=candidate_id,
                        title=title,
                        summary=summary[:500],
                        source=source,
                        published_at=published_iso,
                        url=link or None,
                        relevance=0.55,
                        importance=0.55,
                        freshness=_freshness(published_iso),
                        novelty=0.7,
                    )
                )
        return candidates


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def _feed_title(root: ET.Element) -> str | None:
    for child in root.iter():
        if _local(child.tag) == "title" and child.text:
            return child.text.strip()
    return None


def _entries(root: ET.Element) -> list[dict[str, str]]:
    nodes = [node for node in root.iter() if _local(node.tag) in {"item", "entry"}]
    result: list[dict[str, str]] = []
    for node in nodes:
        item: dict[str, str] = {}
        for child in node:
            name = _local(child.tag)
            text = "".join(child.itertext()).strip()
            if name == "title":
                item["title"] = text
            elif name in {"description", "summary", "content"}:
                item.setdefault("summary", text)
            elif name in {"pubdate", "published", "updated"}:
                item.setdefault("published", text)
            elif name == "link":
                item.setdefault("link", child.attrib.get("href") or text)
        result.append(item)
    return result


def _clean(text: str) -> str:
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    return " ".join(text.split())


def _parse_time(value: str | None) -> str | None:
    if not value:
        return None
    try:
        dt = parsedate_to_datetime(value)
    except (TypeError, ValueError, OverflowError):
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat(timespec="seconds")


def _freshness(published_iso: str | None) -> float:
    if not published_iso:
        return 0.5
    try:
        dt = datetime.fromisoformat(published_iso)
        hours = max(0.0, (datetime.now(timezone.utc) - dt).total_seconds() / 3600)
    except ValueError:
        return 0.5
    if hours <= 12:
        return 1.0
    if hours <= 24:
        return 0.85
    if hours <= 72:
        return 0.65
    return 0.4
