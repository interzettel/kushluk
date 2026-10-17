"""User-approved RSS registry: local files only, never a grant to republish articles.

OPML proposals stay inert until a human explicitly approves individual source indices.
Registry files use exclusive per-registry locking and atomic restricted-mode replacement.
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Iterator

from kushluk.opml import OPMLImportError, _valid_feed_url, read_proposal

MAX_REGISTRY_BYTES = 2_097_152
MAX_SOURCES = 500


class SourceApprovalError(ValueError):
    """Safe, non-secret-bearing validation error."""


def registry_path() -> Path:
    override = os.getenv("KUSHLUK_SOURCE_REGISTRY")
    if override:
        return Path(override).expanduser()
    config = Path(os.getenv("XDG_CONFIG_HOME", str(Path.home() / ".config")))
    return config / "kushluk" / "approved-sources.json"


def _source_id(url: str) -> str:
    _, canonical = _valid_feed_url(url)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:20]


def _source(item: object) -> dict:
    if not isinstance(item, dict) or set(item) != {
        "id", "title", "url", "mode", "enabled", "approved_at"
    }:
        raise SourceApprovalError("Invalid source registry record")
    url = item["url"]
    if not isinstance(url, str):
        raise SourceApprovalError("Invalid source registry URL")
    try:
        identifier = _source_id(url)
    except OPMLImportError as exc:
        raise SourceApprovalError("Invalid source registry URL") from exc
    if item["id"] != identifier:
        raise SourceApprovalError("Source identity does not match its URL")
    # All four requested modes can be persisted, but only reference-only may
    # currently enter the fetch pipeline. No direct copying/synthesis engine
    # exists yet, so requesting those modes must fail closed.
    mode = item["mode"]
    if mode not in {"ignore", "reference-only", "derivative", "private-direct"}:
        raise SourceApprovalError("Unsupported source rights mode")
    if type(item["enabled"]) is not bool:
        raise SourceApprovalError("Source activation flag is invalid")
    if item["enabled"] is not (mode == "reference-only"):
        raise SourceApprovalError("Unsupported source mode cannot be active")
    if not isinstance(item["title"], str) or not item["title"].strip():
        raise SourceApprovalError("Invalid source registry title")
    if not isinstance(item["approved_at"], str) or not item["approved_at"]:
        raise SourceApprovalError("Source approval timestamp is missing")
    return dict(item)


def read_registry(path: Path | None = None) -> list[dict]:
    path = path or registry_path()
    if not path.exists():
        return []
    if path.is_symlink() or not path.is_file():
        raise SourceApprovalError("Registry must be a regular local file")
    try:
        with path.open("rb") as file:
            raw = file.read(MAX_REGISTRY_BYTES + 1)
        if len(raw) > MAX_REGISTRY_BYTES:
            raise SourceApprovalError("Registry is too large")
        data = json.loads(raw)
    except (OSError, ValueError) as exc:
        raise SourceApprovalError("Cannot read valid source registry") from exc
    if not isinstance(data, dict) or data.get("version") != 1:
        raise SourceApprovalError("Unsupported source registry version")
    rows = data.get("sources")
    if not isinstance(rows, list) or len(rows) > MAX_SOURCES:
        raise SourceApprovalError("Invalid registry source list")
    validated = [_source(row) for row in rows]
    if len({row["id"] for row in validated}) != len(validated):
        raise SourceApprovalError("Duplicate source identity in registry")
    return validated


@contextmanager
def _registry_lock(path: Path) -> Iterator[None]:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if path.is_symlink():
        raise SourceApprovalError("Refusing symlink registry")
    lock = path.with_name(path.name + ".lock")
    try:
        fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise SourceApprovalError("Registry locked; resolve an interrupted edit first") from exc
    try:
        os.close(fd)
        yield
    finally:
        lock.unlink(missing_ok=True)


def _atomic_registry(path: Path, rows: list[dict]) -> None:
    data = (json.dumps({"version": 1, "sources": rows}, indent=2, ensure_ascii=False)
            + "\n").encode("utf-8")
    if len(data) > MAX_REGISTRY_BYTES:
        raise SourceApprovalError("Registry would exceed the size limit")
    fd, filename = tempfile.mkstemp(prefix=".sources-", suffix=".tmp", dir=str(path.parent))
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "wb") as file:
            file.write(data)
            file.flush()
            os.fsync(file.fileno())
        os.replace(filename, path)
    finally:
        Path(filename).unlink(missing_ok=True)


def approve_source(proposal: Path, index: int, *, acknowledge: bool,
                   path: Path | None = None) -> tuple[str, int, bool]:
    """Approve exactly one proposal by 1-based index. No network or article-body access."""
    if not acknowledge:
        raise SourceApprovalError("Explicit --acknowledge-feed-access required")
    try:
        feeds = read_proposal(proposal)
    except OPMLImportError as exc:
        raise SourceApprovalError("Invalid unactivated OPML proposal") from exc
    if not (1 <= index <= len(feeds)):
        raise SourceApprovalError("Source index outside proposal")
    candidate = feeds[index - 1]
    try:
        identifier = _source_id(candidate.url)
    except OPMLImportError as exc:
        raise SourceApprovalError("Invalid proposed feed URL") from exc
    path = path or registry_path()
    with _registry_lock(path):
        rows = read_registry(path)
        if any(row["id"] == identifier for row in rows):
            return identifier, len(rows), False
        if len(rows) >= MAX_SOURCES:
            raise SourceApprovalError("Registry holds the maximum number of feeds")
        rows.append({
            "id": identifier, "title": candidate.title, "url": candidate.url,
            "mode": "reference-only", "enabled": True,
            "approved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        })
        _atomic_registry(path, rows)
        return identifier, len(rows), True


def revoke_source(identifier: str, *, path: Path | None = None) -> tuple[int, bool]:
    path = path or registry_path()
    if not identifier or len(identifier) != 20 or any(ch not in "0123456789abcdef" for ch in identifier):
        raise SourceApprovalError("Invalid source identifier")
    with _registry_lock(path):
        rows = read_registry(path)
        filtered = [row for row in rows if row["id"] != identifier]
        changed = len(filtered) != len(rows)
        if changed:
            _atomic_registry(path, filtered)
        return len(filtered), changed


def approved_urls(path: Path | None = None) -> tuple[str, ...]:
    return tuple(
        row["url"] for row in read_registry(path)
        if row["enabled"] and row["mode"] == "reference-only"
    )


def set_source_mode(identifier: str, mode: str, *, acknowledge: bool = False,
                    path: Path | None = None) -> tuple[str, bool]:
    """Save reader intent without pretending unsupported reuse rights exist.

    'derivative' and 'private-direct' remain disabled until a separate,
    provider-specific rights check and actual renderer/adapter are implemented.
    """
    if mode not in {"ignore", "reference-only", "derivative", "private-direct"}:
        raise SourceApprovalError("Unknown rights mode")
    if mode in {"derivative", "private-direct"} and not acknowledge:
        raise SourceApprovalError("Rights-sensitive mode requires explicit acknowledgement")
    if (len(identifier) != 20 or
            any(ch not in "0123456789abcdef" for ch in identifier)):
        raise SourceApprovalError("Invalid source identifier")
    path = path or registry_path()
    with _registry_lock(path):
        rows = read_registry(path)
        for row in rows:
            if row["id"] == identifier:
                row["mode"] = mode
                row["enabled"] = mode == "reference-only"
                _atomic_registry(path, rows)
                return mode, row["enabled"]
        raise SourceApprovalError("Unknown source identifier")
