"""Bounded, read-only edition metadata compatibility inventory.

This does not silently migrate a legacy archive or approve its PDF for
delivery. An older edition must remain untouched until an explicit, tested
migration specification is accepted.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import re

MAX_METADATA_BYTES = 2 * 1024 * 1024
MAX_ARCHIVES = 1000
EDITION = re.compile(r"^[0-9]{8}-[0-9]{3}$")


class ArchiveCompatError(ValueError):
    """Fixed public error code with no private archive titles or paths."""


def _inspect_one(folder: Path) -> str:
    if folder.is_symlink() or not folder.is_dir():
        return "unsafe_archive_path"
    metadata = folder / "metadata.json"
    if metadata.is_symlink():
        return "unsafe_archive_metadata"
    if not metadata.is_file():
        return "missing_metadata"
    try:
        if metadata.stat().st_size > MAX_METADATA_BYTES:
            return "oversized_metadata"
        payload = json.loads(metadata.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError):
        return "invalid_metadata_json"
    if not isinstance(payload, dict):
        return "invalid_metadata_json"
    version = payload.get("schema_version")
    if type(version) is not int:
        return "unknown_schema"
    if version == 1:
        # Legacy one-sheet/early editions are not safely convertible by
        # guessing missing editorial content or rewriting printed artifacts.
        return "legacy_v1_requires_migration"
    if version != 2:
        return "unsupported_schema"
    if (payload.get("edition_id") != folder.name
            or not EDITION.fullmatch(folder.name)
            or payload.get("target_date") != (
                f"{folder.name[:4]}-{folder.name[4:6]}-{folder.name[6:8]}"
            )):
        return "invalid_edition_identity"
    pages = payload.get("pages")
    practical = payload.get("practical")
    stories = payload.get("stories")
    if (not isinstance(pages, list) or not isinstance(practical, list)
            or not isinstance(stories, list) or len(pages) != 4
            or len(practical) > 100 or len(stories) > 100
            or any(not isinstance(v, dict) for v in pages + stories + practical)):
        return "invalid_v2_references"
    if ([p.get("number") for p in pages] != [1, 2, 3, 4]
            or [p.get("kind") for p in pages]
            != ["front", "day", "stories", "sources"]):
        return "invalid_v2_references"
    ids = [s.get("id") for s in stories]
    if (any(not isinstance(key, str) or not key for key in ids)
            or len(set(ids)) != len(ids)):
        return "invalid_v2_references"
    for page in pages:
        indices = page.get("practical_indices")
        references = page.get("story_ids")
        if not isinstance(indices, list) or not isinstance(references, list):
            return "invalid_v2_references"
        if any(type(i) is not int or i < 0 or i >= len(practical) for i in indices):
            return "invalid_v2_references"
        if any(not isinstance(ref, str) or ref not in ids for ref in references):
            return "invalid_v2_references"
    return "readable_v2_metadata"


def inspect_archive_root(root: Path, *, limit: int = 100) -> dict:
    """Counts only: no private titles, absolute paths, metadata, or filenames."""
    if type(limit) is not int or not 1 <= limit <= MAX_ARCHIVES:
        raise ArchiveCompatError("invalid_compat_limit")
    if root.is_symlink() or (root.exists() and not root.is_dir()):
        raise ArchiveCompatError("unsafe_archive_root")
    if not root.exists():
        return {
            "schema_version": 1, "checked": 0, "total_found": 0,
            "truncated": False, "categories": {},
            "migration_performed": False, "delivery_approved": False,
        }
    try:
        entries = sorted(
            (entry for entry in root.iterdir() if entry.is_dir() or entry.is_symlink()),
            key=lambda p: p.name,
        )
    except OSError as exc:
        raise ArchiveCompatError("archive_root_unreadable") from exc
    selected = entries[:limit]
    counts = Counter(_inspect_one(path) for path in selected)
    return {
        "schema_version": 1, "checked": len(selected),
        "total_found": len(entries), "truncated": len(entries) > limit,
        "categories": dict(sorted(counts.items())),
        "migration_performed": False, "delivery_approved": False,
    }
