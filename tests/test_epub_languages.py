"""Publication language is deliberate and persists in EPUB metadata and XHTML."""
from datetime import date
import json
from zipfile import ZipFile
import xml.etree.ElementTree as ET

import pytest

from kushluk.cli import main
from kushluk.epub import EpubError, export_archived_epub
from kushluk.models import PracticalItem, Story
from kushluk.publication import build_publication


DAY = date(2026, 10, 17)
LANG_NS = "http://www.w3.org/XML/1998/namespace"
DC_NS = "http://purl.org/dc/elements/1.1/"


def _archive(tmp_path):
    root = tmp_path / "archive"
    folder = root / "20261017-001"
    folder.mkdir(parents=True)
    publication = build_publication(
        target_date=DAY, timezone="Europe/Berlin", location_name="Synthetic",
        practical=[PracticalItem("Task", "Synthetic morning")],
        stories=[
            Story("s1", "A made-up headline", "A synthetic short blurb",
                  "Own source", source_url="https://example.org/one"),
        ],
    )
    (folder / "metadata.json").write_text(json.dumps(publication.to_dict()))
    return root


@pytest.mark.parametrize("language,second_title", [
    ("und", "Today"), ("en", "Today"), ("en-GB", "Today"),
    ("de", "Heute"), ("de-DE", "Heute"),
    ("tr", "Bugün"), ("tr-TR", "Bugün"),
])
def test_xhtml_opf_and_nav_agree_on_explicit_language(tmp_path, language, second_title):
    root = _archive(tmp_path)
    output = tmp_path / "edition.epub"
    result = export_archived_epub(root, DAY, output, language=language)
    assert result["language"] == language
    assert result["reader_hardware_verified"] is False
    with ZipFile(output) as zipped:
        package = ET.fromstring(zipped.read("OEBPS/package.opf"))
        dc = package.find(f".//{{{DC_NS}}}language")
        assert dc is not None and dc.text == language
        assert package.attrib[f"{{{LANG_NS}}}lang"] == language
        nav = ET.fromstring(zipped.read("OEBPS/nav.xhtml"))
        page = ET.fromstring(zipped.read("OEBPS/page-2.xhtml"))
        for document in (nav, page):
            assert document.attrib["lang"] == language
            assert document.attrib[f"{{{LANG_NS}}}lang"] == language
        assert second_title.encode("utf-8") in zipped.read("OEBPS/nav.xhtml")
        assert second_title.encode("utf-8") in zipped.read("OEBPS/page-2.xhtml")


@pytest.mark.parametrize("language", [
    "", "unknown language", "e_", "de"><script>", "en\n",
    "de@DE", "abcdef", "a", "en-",
    "x" * 40, None,
])
def test_bad_language_rejected_before_output_created(tmp_path, language):
    root = _archive(tmp_path)
    output = tmp_path / "invalid.epub"
    with pytest.raises(EpubError, match="language"):
        export_archived_epub(root, DAY, output, language=language)
    assert not output.exists()


def test_cli_optional_language_and_no_implicit_translation(tmp_path, monkeypatch, capsys):
    root = _archive(tmp_path)
    monkeypatch.setenv("KUSHLUK_ARCHIVE_DIR", str(root))
    out = tmp_path / "german.epub"
    args = ["export-epub", "--date", DAY.isoformat(),
            "--language", "de", "--output", str(out)]
    assert main(args) == 0
    response = json.loads(capsys.readouterr().out)
    assert response["language"] == "de"
    assert response["reader_hardware_verified"] is False
    with ZipFile(out) as zipped:
        page = zipped.read("OEBPS/page-2.xhtml")
        assert b"lang=\"de\"" in page
        assert b"A made-up headline" in zipped.read("OEBPS/page-1.xhtml")

    bad = tmp_path / "bad.epub"
    assert main([
        "export-epub", "--date", DAY.isoformat(), "--language", "not_a_tag",
        "--output", str(bad),
    ]) == 2
    assert json.loads(capsys.readouterr().out)["status"] == "rejected"
    assert not bad.exists()
