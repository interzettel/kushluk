"""Bounded offline discovery from a consented *metadata-only* mailbox export.

Not a Gmail/IMAP connector. It stores no message bodies, sender addresses,
message IDs or token-bearing unsubscribe URLs. Discovery never grants rights.
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from email.utils import parseaddr
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import tempfile

MAX_BYTES = 262144
MAX_HEADERS = 250
MAX_DISCOVERY_DAYS = 60
MODES = frozenset(("ignore", "reference-only", "derivative", "private-direct"))


class NewsletterError(ValueError):
    """Privacy-safe reason codes; never include email header values."""


def _private_json(path: Path, *, max_bytes: int = MAX_BYTES) -> dict:
    try:
        if (path.is_symlink() or not path.is_file() or
                path.stat().st_size > max_bytes):
            raise NewsletterError("invalid_local_mail_snapshot")
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError) as exc:
        raise NewsletterError("invalid_local_mail_snapshot") from exc
    if not isinstance(data, dict):
        raise NewsletterError("invalid_local_mail_snapshot")
    return data


def discover(
    path: Path, *, days: int = 30, now: datetime | None = None,
) -> list[dict]:
    """Owner-exported headers; require repeated sender with newsletter signal."""
    data = _private_json(path)
    if data.get("schema_version") != 1:
        raise NewsletterError("invalid_mail_header_schema")
    return discover_headers(data.get("headers"), days=days, now=now)


def discover_headers(
    rows: object, *, days: int = 30, now: datetime | None = None,
) -> list[dict]:
    """No storage of Gmail header values; same validation for live/local input."""
    if type(days) is not int or not 1 <= days <= MAX_DISCOVERY_DAYS:
        raise NewsletterError("invalid_mail_window")
    if not isinstance(rows, list) or len(rows) > MAX_HEADERS:
        raise NewsletterError("invalid_mail_header_schema")
    reference = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    cutoff = reference - timedelta(days=days)
    groups: dict[str, dict] = {}
    for entry in rows:
        if not isinstance(entry, dict) or set(entry) != {
            "sender", "date", "list_id", "subject"
        }:
            raise NewsletterError("invalid_mail_header")
        sender, created, list_id, subject = (entry[k] for k in (
            "sender", "date", "list_id", "subject"
        ))
        if (not isinstance(sender, str) or len(sender) > 200 or
                not isinstance(list_id, str) or len(list_id) > 150 or
                not isinstance(subject, str) or len(subject) > 200):
            raise NewsletterError("invalid_mail_header")
        try:
            stamp = datetime.fromisoformat(created)
            if stamp.tzinfo is None:
                raise ValueError
            stamp = stamp.astimezone(timezone.utc)
        except (ValueError, TypeError, AttributeError) as exc:
            raise NewsletterError("invalid_mail_header_date") from exc
        if stamp < cutoff or stamp > reference:
            continue
        address = parseaddr(sender)[1].lower()
        if (not re.fullmatch(r"[^@\s]+@(?:[a-z0-9-]+\.)+[a-z]{2,}", address)
                or not list_id.strip()):
            continue
        # Require exact list identity, not merely a brand name in a private email.
        key = address + "|" + list_id.strip().lower()
        identifier = sha256(key.encode()).hexdigest()[:20]
        group = groups.setdefault(identifier, {
            "id": identifier, "sender_domain": address.rsplit("@", 1)[1],
            "message_count": 0, "distinct_days": set(),
            "mode": "ignore", "ingestion_enabled": False,
            "rights_status": "unreviewed",
        })
        group["message_count"] += 1
        group["distinct_days"].add(stamp.date().isoformat())
    return [
        {**item, "distinct_days": len(item["distinct_days"])}
        for item in sorted(groups.values(), key=lambda e: (-e["message_count"], e["id"]))
        if len(item["distinct_days"]) >= 2
    ][:50]


def _save(path: Path, body: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if path.is_symlink():
        raise NewsletterError("unsafe_newsletter_registry")
    fd, temp = tempfile.mkstemp(prefix=".newsletter-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            os.fchmod(stream.fileno(), 0o600)
            json.dump(body, stream, sort_keys=True, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        Path(temp).unlink(missing_ok=True)


def save_proposals(path: Path, candidates: list[dict]) -> None:
    if path.exists() or path.is_symlink():
        raise NewsletterError("newsletter_proposals_already_exist")
    _save(path, {"schema_version": 1, "sources": candidates})


def set_mode(
    path: Path, *, newsletter_id: str, mode: str, acknowledge: bool = False,
) -> dict:
    """User intent is persisted; ingestion stays disabled for every mode."""
    if mode not in MODES or not re.fullmatch(r"[0-9a-f]{20}", newsletter_id):
        raise NewsletterError("invalid_newsletter_mode")
    if not acknowledge:
        raise NewsletterError("explicit_newsletter_review_required")
    data = _private_json(path)
    entries = data.get("sources")
    if data.get("schema_version") != 1 or not isinstance(entries, list):
        raise NewsletterError("invalid_newsletter_proposal")
    selected = None
    for item in entries:
        if not isinstance(item, dict) or item.get("id") is None:
            raise NewsletterError("invalid_newsletter_proposal")
        if item["id"] == newsletter_id:
            selected = item
    if selected is None:
        raise NewsletterError("newsletter_not_found")
    # This module has no mailbox reader, derivative renderer or direct-copy
    # grant evaluator. Even reference-only mode stays inactive.
    selected["mode"] = mode
    selected["ingestion_enabled"] = False
    selected["rights_status"] = "requires_provider_review" if mode in (
        "derivative", "private-direct"
    ) else "reference_intent_only"
    _save(path, data)
    return {"id": newsletter_id, "mode": mode,
            "ingestion_enabled": False, "rights_status": selected["rights_status"]}
