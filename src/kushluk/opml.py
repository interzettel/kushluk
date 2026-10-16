"""Local-only OPML subscription proposals. No fetching, activating or contacting providers."""
from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
from urllib.parse import urlsplit, urlunsplit
import xml.etree.ElementTree as ET
from xml.sax.saxutils import quoteattr


_MAX_XML_BYTES = 1_048_576
_MAX_FEEDS = 500
_REJECT_XML = re.compile(rb"<!\s*(?:DOCTYPE|ENTITY)\b", re.IGNORECASE)


class OPMLImportError(ValueError):
    """Invalid or unsafe OPML input without exposing source content."""


@dataclass(frozen=True)
class FeedProposal:
    title: str
    url: str
    mode: str = "reference-only"
    enabled: bool = False

    def to_dict(self) -> dict[str, str | bool]:
        return {
            "title": self.title,
            "url": self.url,
            "mode": self.mode,
            "enabled": self.enabled,
        }


def _valid_feed_url(value: str) -> tuple[str, str]:
    value = value.strip()
    if not value or len(value) > 2048:
        raise OPMLImportError("A feed URL is empty or too long")
    if any(ord(ch) < 32 or ch == "\x7f" for ch in value):
        raise OPMLImportError("A feed URL contains control characters")
    try:
        p = urlsplit(value)
        host = p.hostname
        port = p.port  # Also checks malformed port syntax.
    except ValueError as exc:
        raise OPMLImportError("Malformed feed URL") from exc
    if p.scheme.lower() not in {"http", "https"} or not host:
        raise OPMLImportError("Only absolute HTTP(S) feeds are eligible")
    if p.username is not None or p.password is not None:
        raise OPMLImportError("Feed URL must not embed account credentials")
    if any(ch.isspace() for ch in value) or any(ch in host for ch in "\\/#?"):
        raise OPMLImportError("Feed URL contains forbidden whitespace or hostname characters")
    if not re.fullmatch(r"[a-z0-9.\-:\[\]]+", host.lower()):
        raise OPMLImportError("Feed hostname contains unsupported characters")
    scheme = p.scheme.lower()
    netloc = host.lower()
    if ":" in netloc and not netloc.startswith("["):
        netloc = f"[{netloc}]"
    if port is not None and not (1 <= port <= 65535):
        raise OPMLImportError("Feed URL has invalid port")
    if port is not None and (scheme, port) not in {("http", 80), ("https", 443)}:
        netloc += f":{port}"
    canonical = urlunsplit((scheme, netloc, p.path or "/", p.query, ""))
    return value, canonical


def parse_opml(data: bytes) -> list[FeedProposal]:
    """Parse OPML v1/v2 XML, deduplicating feed URLs but never accessing network.

    External entities / DTDs are explicitly forbidden before ElementTree parses,
    preventing entity expansion and keeping the input deterministic.
    """
    if len(data) > _MAX_XML_BYTES:
        raise OPMLImportError("OPML file exceeds the 1 MiB limit")
    if _REJECT_XML.search(data):
        raise OPMLImportError("DTDs and XML entities are not accepted in feed imports")
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        raise OPMLImportError("Invalid OPML XML") from exc
    if root.tag.lower() != "opml" or root.get("version") not in {"1.0", "1.1", "2.0"}:
        raise OPMLImportError("Expected OPML 1.0, 1.1 or 2.0")
    body = root.find("body")
    if body is None:
        raise OPMLImportError("OPML body is missing")
    seen: set[str] = set()
    feeds: list[FeedProposal] = []
    for node in body.iter("outline"):
        raw = node.attrib.get("xmlUrl")
        if raw is None:
            continue
        url, key = _valid_feed_url(raw)
        if key in seen:
            continue
        seen.add(key)
        if len(feeds) >= _MAX_FEEDS:
            raise OPMLImportError("More than 500 distinct feeds")
        title = (node.get("title") or node.get("text") or url).strip()
        title = " ".join(title.split())[:160] or url
        feeds.append(FeedProposal(title=title, url=url))
    return feeds


def read_opml(path: Path) -> list[FeedProposal]:
    try:
        with path.open("rb") as stream:
            data = stream.read(_MAX_XML_BYTES + 1)
    except OSError as exc:
        raise OPMLImportError("Cannot open the local OPML input file") from exc
    return parse_opml(data)


def proposal_document(feeds: list[FeedProposal]) -> dict:
    return {
        "schema_version": 1,
        "state": "proposed-only",
        "activation": "requires-explicit-user-approval",
        "feeds": [f.to_dict() for f in feeds],
    }


def write_private_file(path: Path, data: bytes) -> None:
    """Create only, mode 0600, no network, no overwriting existing proposals."""
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise OPMLImportError("Output exists; choose a new file") from exc
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def write_proposal(path: Path, feeds: list[FeedProposal]) -> None:
    payload = json.dumps(proposal_document(feeds), ensure_ascii=False, indent=2)
    write_private_file(path, (payload + "\n").encode("utf-8"))


def read_proposal(path: Path) -> list[FeedProposal]:
    try:
        data = path.read_bytes()
        if len(data) > _MAX_XML_BYTES * 2:
            raise OPMLImportError("Proposal exceeds allowed size")
        doc = json.loads(data)
        if not isinstance(doc, dict) or doc.get("schema_version") != 1:
            raise OPMLImportError("Expected a v1 source proposal")
        if doc.get("state") != "proposed-only" or not isinstance(doc.get("feeds"), list):
            raise OPMLImportError("Only an unactivated source proposal may be exported")
        feeds = []
        for item in doc["feeds"]:
            if not isinstance(item, dict):
                raise OPMLImportError("Invalid feed record")
            if item.get("enabled") is not False or item.get("mode") != "reference-only":
                raise OPMLImportError("An activated or promoted feed requires separate approval")
            title = item.get("title")
            if not isinstance(title, str) or not title.strip():
                raise OPMLImportError("Feed title is missing")
            url = item.get("url")
            if not isinstance(url, str):
                raise OPMLImportError("Feed URL is invalid")
            _valid_feed_url(url)
            feeds.append(FeedProposal(title=title[:160], url=url))
        if len(feeds) > _MAX_FEEDS:
            raise OPMLImportError("Too many feeds")
        return feeds
    except (OSError, json.JSONDecodeError) as exc:
        raise OPMLImportError("Cannot read a valid local source proposal") from exc


def render_opml(feeds: list[FeedProposal]) -> bytes:
    """Export only proposal URLs with safe XML escaping."""
    if len(feeds) > _MAX_FEEDS:
        raise OPMLImportError("Too many feeds")
    outlines = []
    for feed in feeds:
        url, _ = _valid_feed_url(feed.url)
        if feed.enabled or feed.mode != "reference-only":
            raise OPMLImportError("Activated sources cannot be auto-exported")
        outlines.append(
            f"    <outline type=\"rss\" text={quoteattr(feed.title)} "
            f"title={quoteattr(feed.title)} xmlUrl={quoteattr(url)} />"
        )
    xml = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<opml version="2.0">\n  <head><title>Kushluk Proposed Sources</title></head>\n'
        "  <body>\n" + "\n".join(outlines) + "\n  </body>\n</opml>\n"
    )
    return xml.encode("utf-8")
