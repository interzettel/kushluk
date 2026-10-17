"""Privacy-preserving, opt-in health checks of reader-approved RSS sources.

Default is offline inventory. Only an explicit --network check contacts providers.
This is a diagnostic, never a grant to publish or a modification of the registry.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from kushluk.connectors.rss import RSSConnector
from kushluk.source_registry import read_registry


class SourcePreflightError(ValueError):
    """Error text never contains the feed URL or article excerpts."""


def check_sources(*, path: Path | None = None, network: bool = False,
                  limit: int = 5) -> dict[str, Any]:
    if type(limit) is not int or not 1 <= limit <= 10:
        raise SourcePreflightError("Source check limit must be 1–10")
    registry = read_registry(path)
    active = [item for item in registry if item["enabled"] and item["mode"] == "reference-only"]
    report: dict[str, Any] = {
        "schema_version": 1,
        "type": "source_preflight",
        "network_requested": network,
        "archive_modified": False,
        "sources_modified": False,
        "editions_created": 0,
        "registered_sources": len(registry),
        "active_sources": len(active),
        "checked_sources": 0,
        "remaining_active_sources": max(0, len(active) - limit) if network else len(active),
        "sources": [],
    }
    for item in registry:
        if not item["enabled"]:
            report["sources"].append({
                "id": item["id"], "mode": item["mode"],
                "status": "disabled", "checked": False,
            })
    if network:
        for item in active[:limit]:
            connector = RSSConnector((item["url"],), reference_only_urls=(item["url"],))
            try:
                candidates = connector.fetch()
                if connector.failed_feeds:
                    status = connector.failed_feeds[0]["reason"]
                elif not candidates:
                    status = "empty"
                else:
                    status = "reachable"
            except Exception:
                # Do not echo exception or private feed token; fail that source.
                status = "unexpected_failure"
            report["sources"].append({
                "id": item["id"],
                "mode": "reference-only",
                "status": status,
                "checked": True,
                "candidate_headlines": len(candidates) if status in {"reachable", "empty"} else 0,
                "body_copying_permitted": False,
            })
            report["checked_sources"] += 1
        for item in active[limit:]:
            report["sources"].append({
                "id": item["id"], "mode": "reference-only",
                "status": "not_checked", "checked": False,
            })
    else:
        report["sources"].extend({
            "id": item["id"], "mode": "reference-only",
            "status": "network_not_requested", "checked": False,
        } for item in active)
    report["reachable_sources"] = sum(
        row["status"] == "reachable" for row in report["sources"]
    )
    report["failed_sources"] = sum(
        row["checked"] and row["status"] not in {"reachable", "empty"}
        for row in report["sources"]
    )
    report["status"] = (
        "offline_inventory" if not network
        else "no_approved_sources" if not active
        else "healthy" if report["failed_sources"] == 0 and
        report["checked_sources"] == len(active) and report["reachable_sources"]
        else "partial_or_unavailable"
    )
    report["rights_verified"] = False
    report["permission_for_article_copying"] = False
    return report


def save_private_preflight(report: dict[str, Any], output: Path) -> None:
    """Optional create-only diagnostic, without raw URL/secret-bearing fields."""
    output.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        fd = os.open(output, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise SourcePreflightError("Diagnostic already exists; choose a new filename") from exc
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        output.unlink(missing_ok=True)
        raise
