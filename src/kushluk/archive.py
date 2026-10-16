from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from kushluk.models import Publication
from kushluk.publication import publication_markdown


def archive_publication(
    publication: Publication,
    archive_root: Path,
    *,
    html_path: Path | None = None,
    pdf_path: Path | None = None,
    imposed_pdf_path: Path | None = None,
    run_summary: dict[str, Any] | None = None,
) -> Path:
    edition_dir = archive_root / publication.edition_id
    edition_dir.mkdir(parents=True, exist_ok=True)
    (edition_dir / "edition.md").write_text(publication_markdown(publication), encoding="utf-8")
    (edition_dir / "metadata.json").write_text(
        json.dumps(publication.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    if run_summary is not None:
        (edition_dir / "run.json").write_text(
            json.dumps(run_summary, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    if html_path and html_path.exists():
        html = html_path.read_text(encoding="utf-8")
        (edition_dir / "edition.html").write_text(html, encoding="utf-8")
    if pdf_path and pdf_path.exists():
        (edition_dir / "edition.pdf").write_bytes(pdf_path.read_bytes())
    if imposed_pdf_path and imposed_pdf_path.exists():
        (edition_dir / "edition.a3-folded.pdf").write_bytes(imposed_pdf_path.read_bytes())
    return edition_dir


def list_editions(archive_root: Path, limit: int = 20) -> list[dict[str, Any]]:
    if not archive_root.exists():
        return []
    editions: list[dict[str, Any]] = []
    for directory in sorted(
        (path for path in archive_root.iterdir() if path.is_dir()),
        key=lambda path: path.name,
        reverse=True,
    ):
        metadata = directory / "metadata.json"
        if not metadata.exists():
            continue
        try:
            payload = json.loads(metadata.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        editions.append(
            {
                "edition_id": payload.get("edition_id", directory.name),
                "target_date": payload.get("target_date"),
                "location_name": payload.get("location_name"),
                "path": str(directory),
            }
        )
        if len(editions) >= limit:
            break
    return editions
