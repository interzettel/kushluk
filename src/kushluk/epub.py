"""Offline EPUB3 export of the exact archived *semantic* four-page edition.

No fetch, re-ranking, re-rendering, provider access or third-party runtime packages.
This is an experimental e-reader adapter, not proof of physical reader compatibility.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from hashlib import sha256
from html import escape
import json
import os
import re
from pathlib import Path
from kushluk.feed_network import public_article_link
from zipfile import ZipFile, ZIP_DEFLATED, ZIP_STORED
import xml.etree.ElementTree as ET


class EpubError(ValueError):
    """Public error with no private archive content included."""


# Only publication-level language is known in archived v2 content.
_LABELS = {
    "en": ("Front", "Today", "For You", "Sources"),
    "de": ("Titelseite", "Heute", "Für dich", "Quellen"),
    "tr": ("Kapak", "Bugün", "Senin için", "Kaynaklar"),
}


def _language_tag(value: str) -> str:
    """Validate a conservative IETF BCP47 language-tag subset."""
    if not isinstance(value, str) or len(value) > 35 or not re.fullmatch(
        r"[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8}){0,4}", value, re.ASCII
    ):
        raise EpubError("Invalid EPUB language tag")
    return value


def _labels(language: str) -> tuple[str, str, str, str]:
    return _LABELS.get(language.split("-", 1)[0].lower(), _LABELS["en"])


def _e(text: object) -> str:
    return escape(str(text if text is not None else ""), quote=True)


def _metadata(archive: Path, target_date: date) -> dict:
    path = archive / "metadata.json"
    try:
        if path.is_symlink() or path.stat().st_size > 2_097_152:
            raise EpubError("Metadata is unavailable or oversized")
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError) as exc:
        raise EpubError("Cannot read a valid archived edition") from exc
    if not isinstance(payload, dict):
        raise EpubError("Archive must contain a publication object")
    edition_id = f"{target_date:%Y%m%d}-001"
    if (payload.get("schema_version") != 2
            or payload.get("edition_id") != edition_id
            or payload.get("target_date") != target_date.isoformat()):
        raise EpubError("Archived edition identity/schema mismatch")
    pages = payload.get("pages")
    if (not isinstance(pages, list) or len(pages) != 4 or
            [page.get("number") for page in pages if isinstance(page, dict)]
            != [1, 2, 3, 4]):
        raise EpubError("Archive is not the canonical four-page edition")
    practical = payload.get("practical")
    stories = payload.get("stories")
    if not isinstance(practical, list) or not isinstance(stories, list):
        raise EpubError("Archived practical/stories content is invalid")
    if len(practical) > 100 or len(stories) > 100:
        raise EpubError("Archived edition exceeds e-reader safety limits")
    if any(not isinstance(item, dict) for item in practical + stories):
        raise EpubError("Malformed archived edition items")
    ids = [story.get("id") for story in stories]
    if any(not isinstance(identifier, str) for identifier in ids) or len(set(ids)) != len(ids):
        raise EpubError("Story identity mismatch")
    for page in pages:
        indices = page.get("practical_indices")
        references = page.get("story_ids")
        if not isinstance(indices, list) or not isinstance(references, list):
            raise EpubError("Malformed page references")
        if (any(type(i) is not int or not (0 <= i < len(practical)) for i in indices)
                or any(ref not in ids for ref in references)):
            raise EpubError("Page references missing editorial content")
    return payload


def _source_link(story: dict) -> str:
    label = _e(story.get("source_name") or "Source")
    address = public_article_link(story.get("source_url"))
    if not address:
        return f'<p class="source">Source: {label}</p>'
    return f'<p class="source">Source: <a href="{_e(address)}">{label}</a></p>'


def _section(page: dict, payload: dict, language: str) -> str:
    number = page["number"]
    titles = dict(enumerate(_labels(language), 1))
    body = [f"<h1>Page {number} · {titles[number]}</h1>"]
    practical = payload["practical"]
    stories = {row["id"]: row for row in payload["stories"]}
    for index in page["practical_indices"]:
        item = practical[index]
        body.append(
            "<section class=\"practical\"><h2>" + _e(item.get("label")) + "</h2>"
            + "<p>" + _e(item.get("value")) + "</p>"
            + (f'<p>{_e(item["detail"])}</p>' if item.get("detail") else "")
            + "</section>"
        )
    for story_id in page["story_ids"]:
        story = stories[story_id]
        body.append(
            "<article><h2>" + _e(story.get("headline")) + "</h2><p>"
            + _e(story.get("deck")) + "</p>" + _source_link(story) + "</article>"
        )
    if number == 4:
        if payload["stories"]:
            for story in payload["stories"]:
                body.append(_source_link(story))
        else:
            body.append("<p>No editorial sources in this edition.</p>")
        if payload.get("notes"):
            body.append("<h2>Edition notes</h2>")
            body.extend(f"<p>{_e(note)}</p>" for note in payload["notes"][:25])
    if len(body) == 1:
        body.append("<p>No content scheduled for this page.</p>")
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<!DOCTYPE html>\n'
        '<html xmlns="http://www.w3.org/1999/xhtml" ' + f'lang="{language}" xml:lang="{language}">'
        '<head><title>Kushluk · ' + _e(titles[number]) + '</title>'
        '<link rel="stylesheet" type="text/css" href="style.css" /></head>'
        '<body><main>' + "".join(body) + "</main></body></html>"
    )


def _navigation(language: str) -> str:
    items = "".join(
        f'<li><a href="page-{n}.xhtml">Page {n} · {title}</a></li>'
        for n, title in enumerate(_labels(language), 1)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml" '
        'xmlns:epub="http://www.idpf.org/2007/ops" ' + f'lang="{language}" xml:lang="{language}">'
        '<head><title>Kushluk contents</title></head><body>'
        '<nav epub:type="toc" id="toc"><h1>Contents</h1><ol>' + items
        + "</ol></nav></body></html>"
    )


def _package(payload: dict, language: str) -> str:
    edition = _e(payload["edition_id"])
    date_text = _e(payload["target_date"])
    raw = payload.get("generated_at")
    try:
        source_time = datetime.fromisoformat(str(raw))
        if source_time.tzinfo is None:
            raise ValueError("Timestamp missing offset")
        modified = source_time.astimezone(timezone.utc)
        modified_text = modified.strftime("%Y-%m-%dT%H:%M:%SZ")
    except (ValueError, TypeError):
        modified_text = date_text + "T00:00:00Z"
    manifest = ''.join(
        f'<item id="p{n}" href="page-{n}.xhtml" media-type="application/xhtml+xml"/>'
        for n in range(1, 5)
    )
    spine = ''.join(f'<itemref idref="p{n}"/>' for n in range(1, 5))
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" '
        'unique-identifier="pub-id" ' + f'xml:lang="{language}">'
        '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">'
        f'<dc:identifier id="pub-id">urn:kushluk:{edition}</dc:identifier>'
        f'<dc:title>Kushluk · {date_text}</dc:title>'
        f'<dc:language>{language}</dc:language>'
        f'<meta property="dcterms:modified">{modified_text}</meta>'
        '</metadata><manifest>'
        '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>'
        '<item id="style" href="style.css" media-type="text/css"/>'
        + manifest + '</manifest><spine>' + spine + '</spine></package>'
    )


_STYLE = """body { font-family: serif; line-height: 1.5; padding: 1em; color: #1a1a1a; }
h1 { font-size: 1.5em; } h2 { font-size: 1.15em; margin-top: 1.2em; }
article, section { margin-bottom: 1.3em; } .source { font-size: 0.85em; }
a { color: inherit; }
"""


def export_archived_epub(archive_root: Path, target_date: date, output: Path,
                         *, language: str = "und") -> dict:
    """Write a private EPUB, exclusively, from an already archived metadata.json."""
    language = _language_tag(language)
    edition_id = f"{target_date:%Y%m%d}-001"
    payload = _metadata(archive_root / edition_id, target_date)
    output.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        fd = os.open(output, os.O_CREAT | os.O_WRONLY | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise EpubError("Output already exists; archived edition will not be overwritten") from exc
    try:
        with os.fdopen(fd, "wb") as file, ZipFile(file, mode="w") as epub:
            epub.writestr("mimetype", "application/epub+zip", compress_type=ZIP_STORED)
            epub.writestr(
                "META-INF/container.xml",
                '<?xml version="1.0"?>'
                '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
                '<rootfiles><rootfile full-path="OEBPS/package.opf" '
                'media-type="application/oebps-package+xml"/>'
                '</rootfiles></container>',
                compress_type=ZIP_DEFLATED,
            )
            epub.writestr("OEBPS/package.opf", _package(payload, language), compress_type=ZIP_DEFLATED)
            epub.writestr("OEBPS/nav.xhtml", _navigation(language), compress_type=ZIP_DEFLATED)
            epub.writestr("OEBPS/style.css", _STYLE, compress_type=ZIP_DEFLATED)
            for page in payload["pages"]:
                epub.writestr(f'OEBPS/page-{page["number"]}.xhtml',
                              _section(page, payload, language), compress_type=ZIP_DEFLATED)
    except BaseException:
        output.unlink(missing_ok=True)
        raise
    # Parse all generated XML and confirm content list without requiring an EPUB reader.
    try:
        with ZipFile(output) as check:
            paths = check.namelist()
            if paths[0] != "mimetype" or check.getinfo("mimetype").compress_type != ZIP_STORED:
                raise EpubError("Invalid EPUB container layout")
            for path in ("META-INF/container.xml", "OEBPS/package.opf", "OEBPS/nav.xhtml",
                         *(f"OEBPS/page-{n}.xhtml" for n in range(1, 5))):
                ET.fromstring(check.read(path))
            if check.testzip() is not None:
                raise EpubError("EPUB ZIP integrity check failed")
    except Exception as exc:
        output.unlink(missing_ok=True)
        raise EpubError("Generated EPUB failed structural validation") from exc
    return {
        "status": "exported",
        "edition_id": edition_id,
        "chapters": 4,
        "language": language,
        "source": "archived-metadata-only",
        "epub_sha256": sha256(output.read_bytes()).hexdigest(),
        "output": str(output),
        "reader_hardware_verified": False,
    }
