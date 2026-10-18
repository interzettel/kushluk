"""Read-only live portfolio audit: findings are NOT acceptance or release authority."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
import tomllib

from tools.project_health import analyze
from tools.project_sync import FIELDS, REPO, OWNER, PROJECT, field_value, needs_sync


class AuditError(ValueError):
    """Incomplete or malformed inventory: never report a false clean audit."""


MASTER_ROW = re.compile(r"^\|\s*\**#(\d+)\**\s*\|\s*([^|]+)\|", re.M)
MAP_ROW = re.compile(
    r"^\|\s*\*\*([A-Z][A-Z-]*-\d{2}(?: to [A-Z][A-Z-]*-\d{2})?)\*\*"
    r"\s*\|\s*(\d+)\s*\|\s*\[#(\d+)\b", re.M,
)
TASK = re.compile(r"([A-Z][A-Z-]*)-(\d{2})\Z")
ISSUE_URL = re.compile(r"https://github\.com/interzettel/kushluk/issues/(\d+)\Z")


def _read(label: str, *args: str) -> object:
    """Every call is a GitHub read; errors omit stderr and token data."""
    try:
        run = subprocess.run(["gh", *args], text=True, capture_output=True,
                             timeout=120, check=False)
        if run.returncode:
            raise AuditError("github_read_failed:" + label)
        return json.loads(run.stdout)
    except (OSError, subprocess.TimeoutExpired, ValueError) as exc:
        raise AuditError("github_read_failed:" + label) from exc


def _rows(data: object, name: str) -> list[dict]:
    if not isinstance(data, list):
        raise AuditError(name + "_pages_invalid")
    rows = [item for page in data for item in page] if (
        data and isinstance(data[0], list)
    ) else data
    if any(not isinstance(item, dict) for item in rows):
        raise AuditError(name + "_entries_invalid")
    return rows


def collect_snapshot() -> dict:
    issues = _rows(_read(
        "issues", "api", "--paginate", "--slurp",
        f"repos/{REPO}/issues?state=all&per_page=100",
    ), "issues")
    releases = _rows(_read(
        "releases", "api", "--paginate", "--slurp",
        f"repos/{REPO}/releases?per_page=100",
    ), "releases")
    project = _read("project", "project", "item-list", PROJECT, "--owner",
                    OWNER, "--limit", "500", "--format", "json")
    master = _read("index", "issue", "view", "43", "--repo", REPO,
                   "--json", "body")
    if (not isinstance(project, dict)
            or not isinstance(project.get("items"), list)
            or not isinstance(master, dict)
            or not isinstance(master.get("body"), str)):
        raise AuditError("snapshot_invalid")
    if (type(project.get("totalCount")) is int
            and project["totalCount"] > len(project["items"])):
        raise AuditError("project_items_truncated")
    return {"issues": issues, "releases": releases,
            "project": project, "index_body": master["body"]}


def parse_master(body: str) -> tuple[dict[int, str], list[int]]:
    try:
        table = body.split("## 1. Portfolio map", 1)[1].split(
            "### Non-issues", 1
        )[0]
    except IndexError as exc:
        raise AuditError("master_portfolio_section_missing") from exc
    index: dict[int, str] = {}
    duplicates: set[int] = set()
    for n, raw in MASTER_ROW.findall(table):
        number = int(n)
        if number in index:
            duplicates.add(number)
        state = raw.strip().strip("*").upper()
        if not state.startswith(("OPEN", "CLOSED")):
            raise AuditError("invalid_master_state")
        index[number] = "open" if state.startswith("OPEN") else "closed"
    if not index:
        raise AuditError("master_portfolio_empty")
    return index, sorted(duplicates)


def parse_crosswalk(body: str) -> tuple[dict[str, int], list[str]]:
    try:
        table = body.split("## Full task inventory", 1)[1].split("\n## ", 1)[0]
    except IndexError as exc:
        raise AuditError("crosswalk_section_missing") from exc
    mapped: dict[str, int] = {}
    duplicates: set[str] = set()
    for span, count, owner in MAP_ROW.findall(table):
        parts = span.split(" to ")
        a, b = TASK.fullmatch(parts[0]), TASK.fullmatch(parts[-1])
        if (len(parts) > 2 or a is None or b is None or a[1] != b[1]
                or int(a[2]) > int(b[2])):
            raise AuditError("crosswalk_range_invalid")
        ids = [f"{a[1]}-{n:02d}" for n in range(int(a[2]), int(b[2]) + 1)]
        if len(ids) != int(count):
            raise AuditError("crosswalk_range_count_mismatch")
        for item in ids:
            if item in mapped:
                duplicates.add(item)
            mapped[item] = int(owner)
    if not mapped:
        raise AuditError("crosswalk_empty")
    return mapped, sorted(duplicates)


def tag_for_python_version(version: str) -> str:
    m = re.fullmatch(r"(\d+\.\d+\.\d+)(a|b|rc)(\d+)", version)
    if m:
        return f"v{m[1]}-{{'a': 'alpha', 'b': 'beta', 'rc': 'rc'}[m[2]]}.{int(m[3])}"
    return "v" + version


def audit_snapshot(snapshot: dict, root: Path) -> dict:
    """Pure comparison; does not fetch network data or write any project state."""
    if (not isinstance(snapshot, dict)
            or any(key not in snapshot for key in (
                "issues", "releases", "project", "index_body"))
            or not isinstance(snapshot["issues"], list)
            or not isinstance(snapshot["releases"], list)
            or not isinstance(snapshot["project"], dict)):
        raise AuditError("snapshot_invalid")
    project = snapshot["project"]
    if not isinstance(project.get("items"), list):
        raise AuditError("project_invalid")
    if (type(project.get("totalCount")) is int
            and project["totalCount"] > len(project["items"])):
        raise AuditError("project_items_truncated")
    live = {}
    for item in snapshot["issues"]:
        if not isinstance(item, dict):
            raise AuditError("issue_invalid")
        if "pull_request" in item:
            continue
        n = item.get("number")
        if (type(n) is not int or n in live
                or item.get("state") not in ("open", "closed")):
            raise AuditError("issue_inventory_invalid")
        live[n] = item
    if 43 not in live or not isinstance(snapshot["index_body"], str):
        raise AuditError("master_issue_missing")
    indexed, repeated = parse_master(snapshot["index_body"])
    health = analyze(root)
    owners, repeated_tasks = parse_crosswalk(
        (root / "docs/ISSUE_CROSSWALK.md").read_text(encoding="utf-8")
    )
    task_ids = {item["id"] for item in health["task_progress"]["items"]}
    issue_ids = set(live)
    findings = []

    def flag(code: str, ids=(), note: str = "") -> None:
        findings.append({"code": code, "issues": sorted(ids), "detail": note})

    if repeated:
        flag("duplicate_index_rows", repeated)
    if issue_ids - indexed.keys():
        flag("issues_missing_from_index", issue_ids - indexed.keys())
    if indexed.keys() - issue_ids:
        flag("index_has_unknown_issues", indexed.keys() - issue_ids)
    outdated = [n for n in issue_ids & indexed.keys()
                if indexed[n] != live[n]["state"]]
    if outdated:
        flag("index_state_outdated", outdated)
    if repeated_tasks:
        flag("duplicate_task_mappings", note=",".join(repeated_tasks))
    if task_ids - owners.keys():
        flag("crosswalk_tasks_missing", note=",".join(sorted(task_ids - owners.keys())))
    if owners.keys() - task_ids:
        flag("crosswalk_tasks_unknown", note=",".join(sorted(owners.keys() - task_ids)))
    if set(owners.values()) - issue_ids:
        flag("crosswalk_owners_missing", set(owners.values()) - issue_ids)
    gate_owners = {n for gate in health["gates"] for n in gate["issues"]}
    if gate_owners - issue_ids:
        flag("gate_owners_missing", gate_owners - issue_ids)

    members = {}
    for record in project["items"]:
        if not isinstance(record, dict):
            raise AuditError("project_item_invalid")
        content = record.get("content")
        url = content.get("url") if isinstance(content, dict) else None
        m = ISSUE_URL.fullmatch(url.rstrip("/")) if isinstance(url, str) else None
        if m:
            number = int(m[1])
            if number in members:
                raise AuditError("project_item_duplicate")
            members[number] = record
    if issue_ids - members.keys():
        flag("issues_not_in_project", issue_ids - members.keys())
    empty_fields = {}
    for field in ("Status", *FIELDS):
        missing = [n for n in sorted(issue_ids)
                   if field_value(members.get(n, {}), field) in (None, "")]
        empty_fields[field] = len(missing)
        if missing:
            flag("project_field_missing:" + field, missing)
    pending = [n for n in sorted(issue_ids)
               if needs_sync(live[n], members.get(n))]
    if pending:
        flag("project_sync_pending", pending)

    published = [item for item in snapshot["releases"]
                 if isinstance(item, dict) and item.get("draft") is False
                 and item.get("published_at")]
    published.sort(key=lambda item: str(item["published_at"]))
    version = tomllib.loads((root / "pyproject.toml").read_text())["project"]["version"]
    if not isinstance(version, str):
        raise AuditError("version_invalid")
    expected_tag = tag_for_python_version(version)
    latest = published[-1].get("tag_name") if published else None
    if published and not isinstance(latest, str):
        raise AuditError("release_tag_invalid")
    if latest:
        for doc in ("RELEASE_PLAN.md", "WORK_JOURNAL.md", "STATUS.md"):
            if latest not in (root / "docs" / doc).read_text(encoding="utf-8"):
                flag("latest_release_undocumented:" + doc)
        if latest != expected_tag:
            flag("source_version_ahead_or_mismatched",
                 note=f"source={expected_tag}; published={latest}")

    return {
        "schema_version": 1, "kind": "read_only_portfolio_consistency",
        "status": "drift_detected" if findings else "consistent",
        "findings": findings,
        "counts": {
            "issues": len(live),
            "open": sum(x["state"] == "open" for x in live.values()),
            "closed": sum(x["state"] == "closed" for x in live.values()),
            "indexed": len(indexed),
            "project_present": len(issue_ids & members.keys()),
            "project_fields_missing": empty_fields,
            "project_sync_pending": len(pending),
            "crosswalk_mapped": len(owners),
            "tasks": health["task_progress"]["total"],
            "tasks_checked": health["task_progress"]["checked"],
            "gates_verified_in_manifest": health["verified_count"],
        },
        "release": {"latest_tag": latest, "source_equivalent_tag": expected_tag},
        "policy": {"github_writes": False, "gate_approval": False,
                   "task_completion_awarded": False, "release_approval": False},
    }


def summary(report: dict) -> str:
    c = report["counts"]
    lines = [
        "# Kuşluk portfolio consistency (read-only)",
        "",
        f"**Result:** {report['status']} — observation, not acceptance",
        f"**Issues:** {c['issues']} ({c['open']} open, {c['closed']} closed); "
        f"master index: {c['indexed']}",
        f"**Project:** {c['project_present']}/{c['issues']} attached; "
        f"{c['project_sync_pending']} pending sync",
        f"**Operational checklist:** {c['tasks_checked']}/{c['tasks']} checked; "
        f"{c['crosswalk_mapped']}/{c['tasks']} task IDs mapped",
        f"**Independent gates from manifest:** {c['gates_verified_in_manifest']}/8 "
        "(NOT independently verified by this audit)",
        f"**Latest release tag:** {report['release']['latest_tag'] or 'none'}",
        "", "## Findings", "",
    ]
    if not report["findings"]:
        lines.append("No discrepancies found in checked records.")
    for item in report["findings"]:
        ids = ", ".join(f"#{n}" for n in item["issues"])
        suffix = (": " + ids) if ids else ""
        if item["detail"]:
            suffix += " (" + item["detail"] + ")"
        lines.append(f"- {item['code']}{suffix}")
    lines += ["", "No issues, Project fields, releases, task checks or G1–G8 "
              "are modified. Review issues with the human steward.", ""]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--fixture", type=Path, help="Offline JSON input; no GitHub access")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--summary", type=Path)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)
    try:
        snapshot = (json.loads(args.fixture.read_text(encoding="utf-8"))
                    if args.fixture else collect_snapshot())
        report = audit_snapshot(snapshot, args.root)
        payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
        print(payload)
        if args.output:
            args.output.write_text(payload, encoding="utf-8")
        if args.summary:
            with args.summary.open("a", encoding="utf-8") as file:
                file.write(summary(report))
        return 1 if args.strict and report["findings"] else 0
    except (AuditError, OSError, TypeError, KeyError, ValueError) as exc:
        code = str(exc) if isinstance(exc, AuditError) else "invalid_local_input"
        print(json.dumps({"status": "audit_incomplete", "code": code}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
