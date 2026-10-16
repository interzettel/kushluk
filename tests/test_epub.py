"""EPUB3 archived-only export: provenance, XML/ZIP structure, and no provider calls."""
from datetime import date
import json
import os
from zipfile import ZIP_STORED, ZipFile
import xml.etree.ElementTree as ET

import pytest

from kushluk.cli import main
from kushluk.epub import EpubError, export_archived_epub
from kushluk.models import PracticalItem, Story
from kushluk.publication import build_publication


TODAY = date(2026, 10, 17)


def _archive(tmp_path):
    root = tmp_path / "archive"
    folder = root / "20261017-001"
    folder.mkdir(parents=True)
    publication = build_publication(
        target_date=TODAY, timezone="Europe/Berlin", location_name="Synthetic Test",
        practical=[
            PracticalItem("Morning plan", "Appointment at 10:00", "Read your own calendar"),
            PracticalItem("Weather", "Cool", "Umbrella recommended"),
            PracticalItem("Checklist", "Paper"),
            PracticalItem("Lunch", "12:30"),
        ],
        stories=[
            Story("s-a", "Coffee & news <safe>", "This is a synthetic news summary.",
                  "Example & Co", source_url="https://example.org/news?id=1&cat=2"),
            Story("s-b", "Later item", "Only an original, short derivative.",
                  "Public test", source_url="https://example.net/x"),
        ],
        notes=["Offline test; no real publisher content."],
    )
    (folder / "metadata.json").write_text(
        json.dumps(publication.to_dict(), ensure_ascii=False), encoding="utf-8"
    )
    return root, folder


def test_export_four_real_xhtml_chapters_and_navigation(tmp_path):
    root, folder = _archive(tmp_path)
    output = tmp_path / "private.epub"
    result = export_archived_epub(root, TODAY, output)
    assert result["chapters"] == 4
    assert result["reader_hardware_verified"] is False
    assert result["source"] == "archived-metadata-only"
    if os.name != "nt":
        assert output.stat().st_mode & 0o777 == 0o600
    with ZipFile(output) as epub:
        assert epub.namelist()[0] == "mimetype"
        assert epub.getinfo("mimetype").compress_type == ZIP_STORED
        assert epub.read("mimetype") == b"application/epub+zip"
        package = epub.read("OEBPS/package.opf")
        assert b"<spine>" in package and b"urn:kushluk:20261017-001" in package
        assert len(ET.fromstring(package).findall(".//{http://www.idpf.org/2007/opf}itemref")) == 4
        nav = epub.read("OEBPS/nav.xhtml")
        assert b"page-4.xhtml" in nav
        p1 = epub.read("OEBPS/page-1.xhtml")
        assert b"Coffee &amp; news &lt;safe&gt;" in p1
        assert b"https://example.org/news?id=1&amp;cat=2" in p1
        assert b"This is a synthetic news summary." in p1
        assert b"Later item" in epub.read("OEBPS/page-3.xhtml")
        assert b"Public test" in epub.read("OEBPS/page-4.xhtml")
        for n in range(1, 5):
            ET.fromstring(epub.read(f"OEBPS/page-{n}.xhtml"))
    assert (folder / "metadata.json").exists()
    assert not (folder / "edition.epub").exists()


def test_ineligible_archive_fails_closed_and_no_partial_file(tmp_path):
    root, folder = _archive(tmp_path)
    payload = json.loads((folder / "metadata.json").read_text())
    payload["pages"][0]["number"] = 99
    (folder / "metadata.json").write_text(json.dumps(payload))
    path = tmp_path / "bad.epub"
    with pytest.raises(EpubError, match="four-page"):
        export_archived_epub(root, TODAY, path)
    assert not path.exists()


def test_reject_bad_page_story_reference(tmp_path):
    root, folder = _archive(tmp_path)
    payload = json.loads((folder / "metadata.json").read_text())
    payload["pages"][0]["story_ids"] = ["does-not-exist"]
    (folder / "metadata.json").write_text(json.dumps(payload))
    with pytest.raises(EpubError, match="Page references"):
        export_archived_epub(root, TODAY, tmp_path / "broken.epub")


def test_never_overwrites_user_file(tmp_path):
    root, _ = _archive(tmp_path)
    out = tmp_path / "book.epub"
    out.write_bytes(b"existing private artifact")
    with pytest.raises(EpubError, match="exists"):
        export_archived_epub(root, TODAY, out)
    assert out.read_bytes() == b"existing private artifact"


def test_cli_export_is_offline_and_archive_only(tmp_path, monkeypatch, capsys):
    root, _ = _archive(tmp_path)
    monkeypatch.setenv("KUSHLUK_ARCHIVE_DIR", str(root))
    import urllib.request
    monkeypatch.setattr(
        urllib.request, "urlopen",
        lambda *_a, **_k: pytest.fail("EPUB export cannot fetch sources"),
    )
    target = tmp_path / "result.epub"
    assert main(["export-epub", "--date", str(TODAY), "--output", str(target)]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "exported"
    assert result["reader_hardware_verified"] is False
    assert target.is_file()
    assert main(["export-epub", "--date", str(TODAY), "--output", str(target)]) == 2
    assert json.loads(capsys.readouterr().out)["status"] == "rejected"


def test_original_article_html_never_brought_into_epub(tmp_path):
    root, folder = _archive(tmp_path)
    (folder / "edition.html").write_text(
        "<h1>PRIVATE RAW ARTICLE BODY ONLY IN HTML</h1>", encoding="utf-8"
    )
    (folder / "edition.md").write_text("PRIVATE EXTRA BODY", encoding="utf-8")
    dest = tmp_path / "new.epub"
    export_archived_epub(root, TODAY, dest)
    with ZipFile(dest) as epub:
        all_content = b"".join(epub.read(key) for key in epub.namelist())
    assert b"PRIVATE RAW ARTICLE BODY" not in all_content
    assert b"PRIVATE EXTRA BODY" not in all_content


def test_untrusted_non_http_source_link_is_never_rendered_as_href(tmp_path):
    root, folder = _archive(tmp_path)
    meta = json.loads((folder / "metadata.json").read_text())
    meta["stories"][0]["source_url"] = "javascript:alert(1)"
    (folder / "metadata.json").write_text(json.dumps(meta))
    output = tmp_path / "edition.epub"
    export_archived_epub(root, TODAY, output)
    with ZipFile(output) as epub:
        xhtml = epub.read("OEBPS/page-1.xhtml")
    assert b'href="javascript:' not in xhtml
    assert b"Example &amp; Co" in xhtml
