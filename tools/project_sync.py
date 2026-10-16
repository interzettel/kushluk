#!/usr/bin/env python3
"""Manage real GitHub Project #3 fields with an authenticated GitHub CLI.

This code runs inside GitHub Actions using the owner's narrowly scoped token.
Never elevate a user-authored claim to verified delivery or overwrite curated
Project fields with default guesses.
"""
from __future__ import annotations

import argparse
from collections.abc import Callable
from dataclasses import dataclass
import json
import os
import re
import subprocess
import sys
from typing import Any

OWNER = "interzettel"
REPO = "interzettel/kushluk"
PROJECT = "3"
STEWARD = "yigit-denktas"
FIELDS = {
    "Priority": ["P0", "P1", "P2", "P3"],
    "Workstream": [*list("ABCDEFGH"), "Untriaged"],
    "Maturity": ["Idea", "Research", "Accepted", "Implemented", "Verified"],
    "Evidence": ["Missing", "Partial", "Verified"],
}
KINDS = ("bug", "feature", "task", "research", "decision")


class SyncError(Exception):
    """An operation cannot safely establish the requested GitHub metadata."""


@dataclass
class Client:
    call: Callable[[list[str]], str]

    def run(self, *args: str) -> str:
        return self.call(["gh", *args])

    def json(self, *args: str) -> Any:
        raw = self.run(*args)
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise SyncError(f"Invalid GitHub CLI response from {args[:3]}") from exc


def real_call(args: list[str]) -> str:
    result = subprocess.run(args, text=True, capture_output=True, check=False)
    if result.returncode:
        raise SyncError(
            f"{' '.join(args[:4])}: {result.stderr.strip() or 'nonzero exit'}"
        )
    return result.stdout


def require_token() -> None:
    if not os.environ.get("GH_TOKEN"):
        raise SyncError(
            "GH_TOKEN missing. Add KUSHLUK_PROJECT_TOKEN in repository Actions "
            "secrets, with organization Projects read/write and repository "
            "Issues read/write. Never paste the token in issues or chat."
        )


def project_fields(client: Client) -> set[str]:
    data = client.json(
        "project", "field-list", PROJECT, "--owner", OWNER, "--format", "json"
    )
    if not isinstance(data, dict) or not isinstance(data.get("fields"), list):
        raise SyncError("Cannot inspect Project schema")
    return {
        x["name"] for x in data["fields"]
        if isinstance(x, dict) and x.get("name")
    }


def bootstrap(client: Client) -> list[str]:
    existing = project_fields(client)
    if "Status" not in existing:
        raise SyncError("Missing native Status; do not create a duplicate Stage")
    created: list[str] = []
    for name, options in FIELDS.items():
        if name not in existing:
            client.run(
                "project", "field-create", PROJECT, "--owner", OWNER,
                "--name", name, "--data-type", "SINGLE_SELECT",
                "--single-select-options", ",".join(options),
            )
            created.append(name)

    existing_labels = client.json(
        "label", "list", "--repo", REPO, "--limit", "200", "--json", "name"
    )
    label_names = {
        x["name"] for x in existing_labels if isinstance(x, dict)
    }
    definitions = {
        **{
            f"priority:{p}": ("F3D77B", "Triage priority, not delivery evidence")
            for p in FIELDS["Priority"]
        },
        **{
            f"workstream:{w.lower()}": ("E8C9B8", "Primary project workstream")
            for w in FIELDS["Workstream"]
        },
        **{
            f"kind:{k}": ("9A958D", "Issue kind, not delivery status")
            for k in KINDS
        },
    }
    for name, (color, description) in definitions.items():
        if name not in label_names:
            client.run(
                "label", "create", name, "--repo", REPO,
                "--color", color, "--description", description,
            )
    return created


def project_items(client: Client) -> dict[str, dict]:
    data = client.json(
        "project", "item-list", PROJECT, "--owner", OWNER,
        "--limit", "500", "--format", "json",
        "--field", "Status", "--field", "Priority",
        "--field", "Workstream", "--field", "Maturity", "--field", "Evidence",
    )
    if not isinstance(data, dict) or not isinstance(data.get("items"), list):
        raise SyncError("Cannot inspect Project membership")
    result = {}
    for item in data["items"]:
        content = item.get("content") or {}
        url = content.get("url") if isinstance(content, dict) else None
        if url:
            result[url.rstrip("/")] = item
    return result


def desired_metadata(issue: dict) -> dict[str, str]:
    labels = {
        x.get("name", "") for x in issue.get("labels", []) if isinstance(x, dict)
    }
    body = issue.get("body") or ""
    author = issue.get("user") or issue.get("author") or {}
    trusted_author = isinstance(author, dict) and author.get("login") == STEWARD

    def body_field(name: str) -> str | None:
        match = re.search(
            r"^\s*(?:[-*]\s*)?" + name + r"\s*:\s*([\w-]+)\s*$",
            body, re.I | re.M
        )
        return match.group(1) if match else None

    title = (issue.get("title") or "").lower()
    raw_kind = (body_field("Kind") or "").lower() if trusted_author else ""
    kind = raw_kind if raw_kind in KINDS else (
        "bug" if title.startswith("[bug") else
        "research" if title.startswith("[research") or "rfc" in title[:18] else
        "decision" if title.startswith("[decision") else
        "feature" if title.startswith("[feature") else "task"
    )

    labeled_priority = [
        x.split(":", 1)[1] for x in labels if x.lower().startswith("priority:")
    ]
    raw_priority = body_field("Priority") if trusted_author else None
    priority = (
        next((x for x in labeled_priority if x in FIELDS["Priority"]), None)
        or (raw_priority if raw_priority in FIELDS["Priority"] else "P2")
    )

    labeled_area = [
        x.split(":", 1)[1] for x in labels if x.lower().startswith("workstream:")
    ]
    raw_area = body_field("Workstream") if trusted_author else None
    area = (
        next((x.upper() for x in labeled_area if x.upper() in "ABCDEFGH"), None)
        or (raw_area if raw_area in FIELDS["Workstream"] else "Untriaged")
    )
    return {
        "kind": kind,
        "Status": "Done" if str(issue.get("state", "")).lower() == "closed"
                  else "Backlog",
        "Priority": priority,
        "Workstream": area,
        "Maturity": "Research" if kind in ("research", "decision") else "Idea",
        "Evidence": "Missing",  # NEVER infer Verified from issue prose
    }


def sync_issue(
    client: Client, issue: dict, known_items: dict[str, dict] | None = None
) -> dict:
    url = issue.get("html_url") or issue.get("url")
    if not isinstance(url, str) or not re.fullmatch(
        r"https://github\.com/interzettel/kushluk/issues/\d+", url
    ):
        raise SyncError("Issue URL is not under interzettel/kushluk")
    number = url.rsplit("/", 1)[-1]
    if known_items is None:
        known_items = project_items(client)
    record = known_items.get(url)
    if record is None:
        client.run(
            "project", "item-add", PROJECT, "--owner", OWNER, "--url", url
        )
        record = {"content": {"url": url}}
        known_items[url] = record

    present = project_fields(client)
    missing = (set(FIELDS) | {"Status"}) - present
    if missing:
        raise SyncError(
            f"Missing Project fields: {sorted(missing)}. Run bootstrap first."
        )
    wanted = desired_metadata(issue)
    assignees = {
        x.get("login") for x in issue.get("assignees", [])
        if isinstance(x, dict)
    }
    labels = {
        x.get("name", "") for x in issue.get("labels", [])
        if isinstance(x, dict)
    }

    if STEWARD not in assignees:
        client.run(
            "issue", "edit", number, "--repo", REPO,
            "--add-assignee", STEWARD
        )
    required_labels = (
        ("kind:", f"kind:{wanted['kind']}"),
        ("priority:", f"priority:{wanted['Priority']}"),
        ("workstream:", f"workstream:{wanted['Workstream'].lower()}"),
    )
    for prefix, label in required_labels:
        if not any(x.startswith(prefix) for x in labels):
            client.run(
                "issue", "edit", number, "--repo", REPO,
                "--add-label", label
            )

    # Native issue type, when enabled. Never overwrite types on bulk backfill:
    # CLI issue list lacks the full current type for many versions.
    if "type" in issue and not issue["type"]:
        try:
            enabled = client.json("api", f"orgs/{OWNER}/issue-types")
        except SyncError:
            enabled = []
        known = {
            x.get("name") for x in enabled if isinstance(x, dict)
        } if isinstance(enabled, list) else set()
        candidate = {
            "bug": "Bug", "feature": "Feature", "task": "Task",
            "research": "Task", "decision": "Task",
        }[wanted["kind"]]
        if candidate in known:
            client.run(
                "issue", "edit", number, "--repo", REPO,
                "--type", candidate
            )

    # Defaults only fill missing values. Manual triage remains authoritative.
    for field in ("Status", *FIELDS):
        existing = record.get(field.lower(), record.get(field))
        if existing is None or existing == "":
            client.run(
                "project", "item-edit", PROJECT, "--owner", OWNER,
                "--url", url, "--field", field, "--value", wanted[field]
            )
    return {
        "issue": number,
        "url": url,
        "kind": wanted["kind"],
        "proposed_defaults": {
            x: wanted[x] for x in ("Status", *FIELDS)
        },
    }


def issue_from_cli(client: Client, number: str) -> dict:
    issue = client.json(
        "issue", "view", number, "--repo", REPO,
        "--json", "url,title,body,labels,assignees,state,author,issueType",
    )
    return {**issue, "html_url": issue.get("url"),
            "type": issue.get("issueType") or None}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action", choices=("bootstrap", "sync", "audit", "backfill")
    )
    parser.add_argument("--issue", help="Issue number for sync")
    parser.add_argument("--event-file", help="GitHub issues event file")
    args = parser.parse_args(argv)
    try:
        require_token()
        client = Client(real_call)
        if args.action == "bootstrap":
            result = {
                "created_fields": bootstrap(client),
                "project": f"https://github.com/orgs/{OWNER}/projects/{PROJECT}",
            }
        elif args.action == "sync":
            if args.event_file:
                with open(args.event_file, encoding="utf-8") as file:
                    issue = json.load(file)["issue"]
            elif args.issue:
                issue = issue_from_cli(client, args.issue)
            else:
                raise SyncError("sync requires --issue or --event-file")
            result = sync_issue(client, issue)
        else:
            members = project_items(client)
            all_issues = client.json(
                "issue", "list", "--repo", REPO, "--state", "all",
                "--limit", "300", "--json",
                "url,title,body,labels,assignees,state,author",
            )
            if not isinstance(all_issues, list):
                raise SyncError("Cannot list repository issues")
            absent = [
                issue for issue in all_issues if issue["url"] not in members
            ]
            if args.action == "backfill":
                if set(FIELDS) - project_fields(client):
                    raise SyncError("Run bootstrap before backfill")
                for issue in all_issues:
                    sync_issue(
                        client, {**issue, "html_url": issue["url"]}, members
                    )
            result = {
                "issues": len(all_issues),
                "already_in_project": len(all_issues) - len(absent),
                "missing_issue_urls": [i["url"] for i in absent],
                "mode": args.action,
            }
        print(json.dumps(result, indent=2))
    except (SyncError, KeyError, OSError, ValueError) as exc:
        print(f"Kushluk Project sync ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
