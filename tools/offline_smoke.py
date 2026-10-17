"""Hermetic four-page CLI smoke test.

Synthetic inputs only. No RSS/weather host, CUPS device, SMTP service or host
credentials are contacted. Successful output is software proof, not paper proof.
"""
from __future__ import annotations

import argparse
from contextlib import ExitStack
from datetime import date
import json
import os
from pathlib import Path
import socket
import tempfile
from unittest.mock import patch

from kushluk.cli import main
from kushluk.models import Candidate, PracticalItem, SourceRef


def run(*, pdf: bool = False) -> dict:
    with tempfile.TemporaryDirectory(prefix="kushluk-offline-smoke-") as root:
        directory = Path(root)
        env = {
            "KUSHLUK_PROFILE_FILE": str(directory / "no-profile.json"),
            "KUSHLUK_SOURCE_REGISTRY": str(directory / "no-registry.json"),
            "KUSHLUK_RSS_URLS": "",
            "KUSHLUK_CALENDAR_ICS": "",
            "KUSHLUK_CALENDAR_FIXTURE": str(directory / "calendar.json"),
            "KUSHLUK_ARCHIVE_DIR": str(directory / "archive"),
            "KUSHLUK_OUTPUT_DIR": str(directory / "output"),
            "KUSHLUK_HOME_NAME": "Synthetic city",
            "KUSHLUK_LATITUDE": "50.9",
            "KUSHLUK_LONGITUDE": "6.9",
            "KUSHLUK_TIMEZONE": "Europe/Berlin",
        }
        (directory / "calendar.json").write_text(
            json.dumps({"events": [{"time": "10:00", "title": "Synthetic appointment"}]}),
            encoding="utf-8",
        )
        weather = [PracticalItem(
            "Synthetic weather", "18 °C", "Synthetic forecast; not a live reading",
            SourceRef("weather", "Offline fixture"),
        )]
        story = Candidate(
            id="offline-story", title="Synthetic local newspaper test",
            summary="Fixture content only; no article body was fetched.",
            source=SourceRef("rss", "Offline fixture"),
            required=True,
        )

        # Any unmocked network attempt is an immediate CI failure.
        def deny_network(*_args, **_kwargs):
            raise AssertionError("Offline smoke attempted a network connection")

        with ExitStack() as stack:
            stack.enter_context(patch.dict(os.environ, env, clear=False))
            stack.enter_context(
                patch("kushluk.pipeline.OpenMeteoWeatherConnector.fetch",
                      return_value=weather)
            )
            stack.enter_context(
                patch("kushluk.pipeline.RSSConnector.fetch", return_value=[story])
            )
            stack.enter_context(patch.object(socket.socket, "connect", deny_network))
            stack.enter_context(patch.object(socket.socket, "connect_ex", deny_network))
            stack.enter_context(patch("socket.create_connection", deny_network))
            stack.enter_context(patch(
                "kushluk.pipeline.print_pdf",
                side_effect=AssertionError("Offline smoke attempted physical printing"),
            ))
            stack.enter_context(patch(
                "kushluk.pipeline.send_email_edition",
                side_effect=AssertionError("Offline smoke attempted email delivery"),
            ))
            arguments = ["generate", "--date", "2026-09-23"]
            if not pdf:
                arguments.append("--no-pdf")
            status = main(arguments)
            assert status == 0, f"CLI returned {status}"

        archive = directory / "archive" / "20260923-001"
        metadata = json.loads((archive / "metadata.json").read_text(encoding="utf-8"))
        receipt = json.loads((archive / "run.json").read_text(encoding="utf-8"))
        assert metadata["schema_version"] == 2
        assert [page["number"] for page in metadata["pages"]] == [1, 2, 3, 4]
        assert metadata["stories"] and metadata["stories"][0]["source_name"] == "Offline fixture"
        assert (archive / "edition.html").exists()
        assert (archive / "edition.md").exists()
        assert receipt["print"] is None and receipt["email"] is None
        assert not receipt["failures"], receipt["failures"]
        if pdf:
            from kushluk.validation import validate_pdf
            rendered = archive / "edition.pdf"
            assert rendered.is_file(), "No archived PDF"
            assert validate_pdf(rendered).ok, "Four-page PDF validation failed"
        else:
            assert not (archive / "edition.pdf").exists()
        return {
            "status": "synthetic_offline_smoke_passed",
            "canonical_pages": 4,
            "pdf_validated": pdf,
            "network_or_delivery": False,
            "physical_verified": False,
        }


def cli() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run(pdf=args.pdf)))
    return 0


if __name__ == "__main__":
    raise SystemExit(cli())
