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


def format_percent(completed: int, total: int) -> str:
    """Two decimal places, zero-padded below 10%, from explicit counts."""
    if total <= 0 or not 0 <= completed <= total:
        raise HealthError("Percent requires 0 <= completed <= positive total")
    return f"{100 * completed / total:05.2f}%"


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
    detailed = []
    for match in TASK.finditer(ledger):
        end = ledger.find("\n", match.end())
        detail = ledger[match.end():end if end != -1 else len(ledger)].strip()
        detailed.append({"id": match["id"], "checked": match["mark"] == "x",
                         "summary": detail})
    rows = [
        {"group": key, "checked": sum(f"{key}-{i:02d}" in done
                                      for i in range(1, maximum + 1)),
         "total": maximum,
         "percentage": format_percent(sum(f"{key}-{i:02d}" in done
                                          for i in range(1, maximum + 1)), maximum)}
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
        "task_progress": {"checked": len(done), "total": len(expected),
                          "percentage": format_percent(len(done), len(expected)),
                          "groups": rows, "items": detailed},
        "gates": gates,
        "verified_count": sum(g["status"] == "verified" for g in gates),
        "verified_percentage": format_percent(
            sum(g["status"] == "verified" for g in gates), len(gates)
        ),
    }


def render(s: dict) -> str:
    tasks = s["task_progress"]
    gates = s["gates"]
    lines = [
        "# Kushluk progress and evidence gates",
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
        f"**{s['verified_count']} of 8 verified with evidence "
        f"({s['verified_percentage']}).** "
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
        f"**{tasks['checked']} of {tasks['total']} task checkboxes checked "
        f"({tasks['percentage']}).** "
        "This measures task-record state, not overall readiness.",
        "",
        "| Task group | Checked | Total | Progress |",
        "| --- | ---: | ---: | ---: |",
    ]
    for row in tasks["groups"]:
        lines.append(f"| {row['group']} | {row['checked']} | {row['total']} | {row['percentage']} |")
    lines += [
        f"| **TOTAL** | **{tasks['checked']}** | **{tasks['total']}** | **{tasks['percentage']}** |",
        "",
        "## Individual tasks",
        "",
        "The lines below are generated from WORK_LEDGER.md. Each task ID has a primary "
        "owner in [ISSUE_CROSSWALK.md](ISSUE_CROSSWALK.md), not its own invented progress weight.",
        "",
    ]
    for group in tasks["groups"]:
        prefix = group["group"] + "-"
        lines.extend([
            f"<details><summary><strong>{group['group']} — "
            f"{group['checked']}/{group['total']} checked · "
            f"{group['percentage']}</strong></summary>",
            "",
            "| Task ID | Ledger state | Description |",
            "| --- | --- | --- |",
        ])
        for item in tasks["items"]:
            if item["id"].startswith(prefix):
                summary = item["summary"].replace("|", r"\|").replace("\n", " ")
                state = "CHECKED" if item["checked"] else "OPEN"
                lines.append(f"| `{item['id']}` | {state} | {summary} |")
        lines.extend(["", "</details>", ""])
    lines += [
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



# Warm editorial Kushluk palette. Source: docs/DESIGN_BRIEF.md and
# src/kushluk/templates/edition.html. SVG remains useful in monochrome.
PAPER = "#F3EFE4"
INK = "#1A1A1A"
MUTED = "#6D6961"
RULE = "#BDB6A8"
SALMON = "#E8C9B8"
YELLOW = "#F3D77B"
WHITE = "#FFFDF8"
GROUP_NAMES = {
    "DOC": "Project records",
    "FMT": "Four-page formats",
    "AUT": "Unattended runs",
    "SRC": "Source connectors",
    "IMG": "Image handling",
    "LAY": "Editorial layouts",
    "DES-EXT": "Design integrations",
    "RES-NEWS": "Newspaper research",
    "RES-AUTO": "Automation research",
    "RES-IMG": "Image rights research",
    "ED": "Editorial intelligence",
    "UX": "Setup and controls",
    "TRIAL": "Physical trials",
}


def render_svg(s: dict) -> str:
    """Render the same canonical evidence snapshot as accessible, editable SVG."""
    from html import escape

    def esc(value: object) -> str:
        return escape(str(value), quote=True)

    def rect(x, y, w, h, color, *, radius=0, stroke=None) -> str:
        border = f' stroke="{stroke}" stroke-width="1"' if stroke else ""
        return (
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" '
            f'rx="{radius}" fill="{color}"{border}/>'
        )

    def txt(x, y, value, size=16, weight=400, *, color=INK, letter="0") -> str:
        return (
            f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" '
            f'font-weight="{weight}" letter-spacing="{letter}" '
            f'font-family="Georgia,Times New Roman,serif">{esc(value)}</text>'
        )

    p = [
        '<svg xmlns="http://www.w3.org/2000/svg" role="img" '
        'aria-labelledby="title desc" viewBox="0 0 1160 1100" '
        'width="1160" height="1100">',
        "<title id=\"title\">Kushluk — development and proof of delivery</title>",
        "<desc id=\"desc\">An evidence status map with eight delivery gates "
        "and a separate count of checked operational tasks. The presence "
        "of a task checkbox is not a percentage of completed product.</desc>",
        rect(0, 0, 1160, 1100, PAPER),
        rect(36, 35, 1088, 1030, WHITE, radius=3, stroke=RULE),
        # Masthead: ink rules + restrained sun, no stock illustration
        txt(68, 111, "Kushluk", 51, 700, letter="-2"),
        txt(71, 142, "AN OPEN PERSONAL MORNING PUBLICATION", 13, 600, color=MUTED, letter="1.25"),
        '<circle cx="1072" cy="91" r="20" fill="' + YELLOW + '"/>',
        rect(68, 171, 1024, 2, INK),
        txt(68, 207, "01  /  DELIVERY EVIDENCE", 19, 700, letter="0.8"),
        txt(888, 207, s["review_date"] + "  ·  REVIEW SNAPSHOT", 13, 400, color=MUTED),
    ]
    status_words = {"unverified": "AWAITING PROOF", "in_progress": "IN TEST",
                    "blocked": "BLOCKED", "verified": "VERIFIED"}
    for index, gate in enumerate(s["gates"]):
        col, row = index % 2, index // 2
        x, y = 68 + col * 518, 225 + row * 91
        w = 500
        p.append(rect(x, y, w, 77, PAPER, radius=5, stroke=RULE))
        p.append(rect(x + 12, y + 14, 5, 49, INK if gate["status"] == "verified" else SALMON))
        p.append(txt(x + 28, y + 29, gate["id"] + "  " + gate["name"], 17, 650))
        p.append(txt(x + 28, y + 55, status_words[gate["status"]], 12, 700, color=MUTED, letter="0.65"))
        p.append(txt(x + 336, y + 55, "ISSUE " + ", ".join(str(i) for i in gate["issues"][:4]), 11, 400, color=MUTED))
    p.append(txt(847, 595, f"{s['verified_count']}/8 VERIFIED · "
                 f"{s['verified_percentage']}", 12, 600, color=MUTED))
    p.append(rect(68, 602, 1024, 1, RULE))
    p.append(txt(68, 642, "02  /  OPERATIONAL TASKS", 19, 700, letter="0.8"))
    task = s["task_progress"]
    p.append(txt(802, 642, f'{task["checked"]} / {task["total"]} CHECKED · '
                 f'{task["percentage"]}', 15, 700, color=INK))
    p.append(txt(68, 668, "Checkboxes from the work ledger, not a product-completion estimate.", 14, 400, color=MUTED))
    rows = task["groups"]
    for i, group in enumerate(rows):
        col, row = i % 2, i // 2
        x, y = 68 + col * 518, 702 + row * 44
        p.append(txt(x, y, GROUP_NAMES.get(group["group"], group["group"]), 15, 500))
        p.append(txt(x + 344, y, f'{group["checked"]} / {group["total"]} · '
                     f'{group["percentage"]}', 13, 600, color=MUTED))
        p.append(rect(x, y + 9, 474, 7, "#DDD6C9", radius=3))
        fill = 474 * group["checked"] / group["total"]
        if fill:
            p.append(rect(x, y + 9, round(fill, 2), 7, INK, radius=3))
    p.append(rect(68, 1032, 1024, 1, RULE))
    p.append(txt(68, 1054, "EVIDENCE FIRST.  •  LOCAL BY DEFAULT.  •  NO IMPLIED COMPLETION.", 12, 600, color=MUTED, letter="0.5"))
    p.append("</svg>\n")
    return "\n".join(p)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "write", "render", "svg", "json"))
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args(argv)
    try:
        result = analyze(args.root)
        markdown = render(result)
        graphic = render_svg(result)
        path = args.root / "docs/PROGRESS.md"
        art = args.root / "docs/progress.svg"
        if args.command == "write":
            path.write_text(markdown, encoding="utf-8")
            art.write_text(graphic, encoding="utf-8")
            print("Updated docs/PROGRESS.md and docs/progress.svg")
        elif args.command == "check":
            if not path.exists() or path.read_text(encoding="utf-8") != markdown:
                raise HealthError("Progress report stale: run python tools/project_health.py write")
            if not art.exists() or art.read_text(encoding="utf-8") != graphic:
                raise HealthError("Branded progress SVG stale: run python tools/project_health.py write")
            print(f"Progress validated: {result['task_progress']['total']} tasks; "
                  f"{result['verified_count']}/8 gates evidence-verified.")
        elif args.command == "render":
            sys.stdout.write(markdown)
        elif args.command == "svg":
            sys.stdout.write(graphic)
        elif args.command == "json":
            print(json.dumps(result, indent=2, ensure_ascii=False))
    except (OSError, json.JSONDecodeError, HealthError) as exc:
        print(f"Project health error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
