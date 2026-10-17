"""Produce a tiny synthetic edition for independent W3C EPUBCheck CI.

All content is invented: this fixture contains no reader emails, private sources,
provider credentials, or external article bodies.
"""
from datetime import date
import json
import os
from pathlib import Path

from kushluk.epub import export_archived_epub
from kushluk.models import PracticalItem, Story
from kushluk.publication import build_publication

day = date(2026, 10, 17)
archive = Path(os.environ["KUSHLUK_ARCHIVE_DIR"])
folder = archive / "20261017-001"
folder.mkdir(parents=True, exist_ok=True)
edition = build_publication(
    target_date=day,
    timezone="Europe/Berlin",
    location_name="SYNTHETIC EPUB VALIDATION — NOT NEWS",
    practical=[PracticalItem("Calendar", "A fictional appointment")],
    stories=[
        Story(
            id="sample",
            headline="Original synthetic demonstration",
            deck="This is wholly invented test content for EPUB conformance.",
            source_name="Kushluk test fixture",
            source_url="https://example.org/",
        )
    ],
)
(folder / "metadata.json").write_text(
    json.dumps(edition.to_dict(), ensure_ascii=False), encoding="utf-8"
)
output = Path(os.environ["KUSHLUK_EPUB_TEST_OUTPUT"])
print(export_archived_epub(archive, day, output, language="en"))
# A second synthetic localized navigation package exercises metadata semantics.
print(export_archived_epub(
    archive, day, output.with_name("synthetic-de.epub"), language="de"
))
