#!/usr/bin/env python3
"""Create a traceable Kushluk issue with the same native Project metadata as CI."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import tempfile

from tools.project_sync import (Client, FIELDS, PRIORITIES, REPO, STEWARD, SyncError,
                                issue_from_cli, real_call, sync_issue)

KINDS = ("bug", "feature", "task", "research", "decision")


def create(argv: list[str] | None = None) -> str:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--title", required=True)
    p.add_argument("--body-file", required=True, type=Path)
    p.add_argument("--kind", required=True, choices=KINDS)
    p.add_argument("--priority", choices=PRIORITIES, default="P2")
    p.add_argument("--workstream", choices=FIELDS["Workstream"], default="Untriaged")
    p.add_argument("--parent", type=int)
    p.add_argument("--blocked-by", type=int, action="append", default=[])
    p.add_argument("--milestone", help="Existing GitHub milestone title; optional")
    args = p.parse_args(argv)
    client = Client(real_call)
    title = args.title.strip()
    if not title:
        raise ValueError("Title cannot be blank")
    content = args.body_file.read_text(encoding="utf-8").strip()
    if not content:
        raise ValueError("Issue body cannot be empty")
    if args.parent is not None and args.parent < 1:
        raise ValueError("Parent must be a real issue number")
    if any(n < 1 for n in args.blocked_by):
        raise ValueError("Dependencies must be real issue numbers")

    # Refuse exact-title duplicates (agent must reconcile other semantic duplicates).
    existing = client.json(
        "issue", "list", "--repo", REPO, "--state", "all",
        "--limit", "500", "--json", "title,url",
    )
    for row in existing:
        if row["title"].strip().casefold() == title.casefold():
            raise ValueError(f"Existing issue with identical title: {row['url']}")

    kind_display = {"bug": "Bug", "feature": "Feature", "task": "Task",
                    "research": "Task", "decision": "Task"}[args.kind]
    # Organization Issue Types may require independent permission. Labels remain fallback.
    try:
        enabled = client.json("api", "orgs/interzettel/issue-types")
        if not isinstance(enabled, list):
            enabled = []
    except Exception:
        enabled = []
    supported = {item.get("name") for item in enabled if isinstance(item, dict)}
    metadata = (
        f"Kind: {args.kind}\nPriority: {args.priority}\n"
        f"Workstream: {args.workstream}\n"
        f"Assignee: @{STEWARD}\n"
        "Project: https://github.com/orgs/interzettel/projects/3\n"
        f"Parent: {'#' + str(args.parent) if args.parent else 'TBD'}\n"
        f"Blocked by: {', '.join('#'+str(n) for n in args.blocked_by) or 'none'}\n"
        f"Milestone: {args.milestone or 'TBD'}\n"
        "Development: not started\nEvidence: pending\n"
    )
    with tempfile.TemporaryDirectory() as directory:
        tmp = Path(directory) / "issue.md"
        tmp.write_text(metadata + "\n" + content + "\n", encoding="utf-8")
        command = [
            "issue", "create", "--repo", REPO, "--title", title,
            "--body-file", str(tmp), "--assignee", STEWARD,
            "--label", f"kind:{args.kind}",
            "--label", f"priority:{args.priority}",
            "--label", f"workstream:{args.workstream.lower()}",
        ]
        if kind_display in supported:
            command += ["--type", kind_display]
        if args.parent:
            command += ["--parent", str(args.parent)]
        for n in args.blocked_by:
            command += ["--blocked-by", str(n)]
        if args.milestone:
            command += ["--milestone", args.milestone]
        url = client.run(*command).strip().splitlines()[-1]
    match = re.fullmatch(r"https://github\.com/interzettel/kushluk/issues/(\d+)", url)
    if not match:
        raise ValueError(f"Unexpected GitHub issue URL: {url!r}")
    issue = issue_from_cli(client, match.group(1))
    # This is a real Project write, not a Markdown promise.
    sync_issue(client, issue)
    return url


def main() -> int:
    try:
        print(create())
        return 0
    except (ValueError, OSError, json.JSONDecodeError, SyncError) as error:
        print(f"Could not create or synchronize issue: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
