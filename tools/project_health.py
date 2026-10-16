#!/usr/bin/env python3
"""Offline deterministic project health analyzer; NOT an overall completion score."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
import json
from pathlib import Path
import re
import sys

TASK = re.compile(
    r"^- \[(?P<mark>[ x])\] \*\*(?P<id>[A-Z][A-Z-]*-\d{2})(?: \([^)]*\))?\*\*",
    re.MULTILINE,
)
STATUSES = {"unverified", "in_progress", "blocked", "verified"}


class HealthError(ValueError):
    pass


def analyze(root: Path) -> dict:
    ledger = (root / "docs/WORK_LEDGER.md").read_text(encoding="utf-8")
    conf = json.loads((root / "docs/progress-manifest.json").read_text(encoding="utf-8"))
    if conf.get("schema_version") != 1:
        raise HealthError("Unsupported progress manifest schema.")
    try:
        date.fromisoformat(conf["review_date"])
    except (ValueError, KeyError, TypeError) as exc:
        raise HealthError("Missing or invalid ISO review_date.") from exc
    groups = conf.get("task_groups")
    if not isinstance(groups, dict) or not groups:
        raise HealthError("No task_groups declared.")
    expected = []
    for key, maximum in groups.items():
        if not re.fullmatch("[A-Z][A-Z-]*", key) or type(maximum) is not int or maximum < 1:
            raise HealthError(f"Invalid task group/count: {key!r}")
        expected.extend(f"{key}-{i:02d}" for i in range(1, maximum + 1))
    observed = [(m["id"], m["mark"] == "x") for m in TASK.finditer(ledger)]
    frequency = Counter(key for key, _ in observed)
    repeated = sorted(key for key, n in frequency.items() if n > 1)
    missing = sorted(set(expected) - frequency.keys())
    unexpected = sorted(frequency.keys() - set(expected))
    if repeated or missing or unexpected:
        raise HealthError(
            f"Work ledger drift: duplicated={repeated}; missing={missing}; "
            f"unexpected={unexpected}. Reconcile manifest AND issue mapping."
        )
    done = {key for key, checked in observed if checked}
    rows = [
        {"group": key, "checked": sum(f"{key}-{i:02d}" in done
                                      for i in range(1, maximum + 1)),
         "total": maximum}
        for key, maximum in groups.items()
    ]
    gates = conf.get("gates")
    if not isinstance(gates, list) or len(gates) != 8:
        raise HealthError("Exactly eight evidence gates required.")
    if [g.get("id") for g in gates if isinstance(g, dict)] != [
        f"G{i}" for i in range(1, 9)
    ]:
        raise HealthError("Gates must be unique and ordered G1–G8.")
    for g in gates:
        label = g["id"]
        if not isinstance(g.get("name"), str) or not g["name"].strip():
            raise HealthError(f"{label}: missing gate name")
        if g.get("status") not in STATUSES:
            raise HealthError(f"{label}: invalid status")
        issues = g.get("issues")
        if not isinstance(issues, list) or not issues or any(
            type(i) is not int or i < 1 for i in issues
        ):
            raise HealthError(f"{label}: invalid GitHub issue references")
        evidence = g.get("evidence", [])
        if not isinstance(evidence, list) or any(
            not isinstance(url, str) or not url.startswith("https://")
            for url in evidence
        ):
            raise HealthError(f"{label}: evidence must be HTTPS links")
        if g["status"] == "verified":
            if not evidence or not g.get("verified_on"):
                raise HealthError(f"{label}: verified requires dated evidence")
            try:
                date.fromisoformat(g["verified_on"])
            except (TypeError, ValueError) as exc:
                raise HealthError(f"{label}: invalid verified_on date") from exc
        elif g.get("verified_on"):
            raise HealthError(f"{label}: only verified gates can have verified_on")
    return {
        "review_date": conf["review_date"],
        "task_progress": {"checked": len(done), "total": len(expected), "groups": rows},
        "gates": gates,
        "verified_count": sum(g["status"] == "verified" for g in gates),
    }


def render(s: dict) -> str:
    tasks = s["task_progress"]
    gates = s["gates"]
    lines = [
        "# Kuşluk progress and evidence gates",
        "",
        f"**Snapshot reviewed:** {s['review_date']} · Sources: "
        "[WORK_LEDGER.md](WORK_LEDGER.md), "
        "[progress-manifest.json](progress-manifest.json)",
        "",
        "> These numbers are NOT an overall percentage of product completion. "
        "Checked tasks count operational checklist marks only. "
        "Delivery gates are independently verified with linked evidence.",
        "",
        "## Delivery evidence gates",
        "",
        f"**{s['verified_count']} of 8 verified with evidence.** "
        "Unverified does not mean failed.",
        "",
        "| Gate | State | Owner issues |",
        "| --- | --- | --- |",
    ]
    for gate in gates:
        links = ", ".join(f"[#{i}](https://github.com/interzettel/kushluk/issues/{i})"
                          for i in gate["issues"])
        lines.append(f"| {gate['id']} — {gate['name']} | {gate['status']} | {links} |")
        if gate["status"] == "verified":
            proof = ", ".join(f"[proof]({url})" for url in gate["evidence"])
            lines.append(f"| Proof ({gate['verified_on']}) | {proof} | |")
    lines += [
        "",
        "## Operational work ledger",
        "",
        f"**{tasks['checked']} of {tasks['total']} task checkboxes checked.** "
        "This measures task-record state, not overall readiness.",
        "",
        "| Task group | Checked | Total |",
        "| --- | ---: | ---: |",
    ]
    for row in tasks["groups"]:
        lines.append(f"| {row['group']} | {row['checked']} | {row['total']} |")
    lines += [
        f"| **TOTAL** | **{tasks['checked']}** | **{tasks['total']}** |",
        "",
        "## Update protocol",
        "",
        "1. Complete an owning issue's acceptance tests and attach reproducible evidence.",
        "2. Update the relevant WORK_LEDGER.md checkbox only after evidence review.",
        "3. Mark a gate verified only with HTTPS evidence and a verified_on ISO date "
        "in progress-manifest.json.",
        "4. Run: python tools/project_health.py write",
        "5. Run: python tools/project_health.py check (enforced by Project health CI).",
        "",
        "The [master ledger #43](https://github.com/interzettel/kushluk/issues/43) "
        "holds the GitHub issue inventory. This offline report does not fetch live GitHub "
        "issue states. [Engineering foundation #54](https://github.com/interzettel/kushluk/issues/54) "
        "owns this reporting system.",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "write", "render", "json"))
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args(argv)
    try:
        result = analyze(args.root)
        markdown = render(result)
        path = args.root / "docs/PROGRESS.md"
        if args.command == "write":
            path.write_text(markdown, encoding="utf-8")
            print("Updated docs/PROGRESS.md")
        elif args.command == "check":
            if not path.exists() or path.read_text(encoding="utf-8") != markdown:
                raise HealthError("Progress report stale: run python tools/project_health.py write")
            print(f"Progress validated: {result['task_progress']['total']} tasks; "
                  f"{result['verified_count']}/8 gates evidence-verified.")
        elif args.command == "render":
            sys.stdout.write(markdown)
        elif args.command == "json":
            print(json.dumps(result, indent=2, ensure_ascii=False))
    except (OSError, json.JSONDecodeError, HealthError) as exc:
        print(f"Project health error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
