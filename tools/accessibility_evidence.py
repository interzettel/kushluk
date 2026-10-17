"""Preflight completeness of a PRIVATE independent accessibility observation.

This neither tests accessibility nor verifies a human participant. It never
uploads data or echoes participant notes, names, screen output or credentials.
"""
from __future__ import annotations

from datetime import date
import json
from pathlib import Path
import re
import sys

TASKS = tuple(f"A{i}" for i in range(1, 6))
OUTCOMES = {"unassisted_pass", "assisted_pass", "fail", "blocked"}
QUESTIONS = (
    "focus_navigation", "form_labels", "source_consent",
    "status_meaning", "zoom_or_contrast",
)


def assess(record: object) -> dict:
    problems = []
    if not isinstance(record, dict):
        return _summary("incomplete", ["root: expected object"])
    if record.get("status") == "template-not-observation":
        return _summary("template", ["status: blank template, no human evidence"])
    if record.get("schema_version") != 1 or record.get("status") != "observation":
        problems.append("status: observation and schema_version 1 required")
    for field in ("participant_code", "observer_code"):
        item = record.get(field)
        if (not isinstance(item, str)
                or not re.fullmatch(r"[A-Za-z0-9_-]{2,64}", item)
                or item in {"REPLACE", "ANONYMOUS_CODE"}):
            problems.append(f"{field}: anonymous identifier required")
    if record.get("participant_code") == record.get("observer_code"):
        problems.append("participant_code/observer_code: must be different")
    if not re.fullmatch(r"[0-9a-f]{40}", str(record.get("source_commit", ""))):
        problems.append("source_commit: real 40-character commit required")
    try:
        when = date.fromisoformat(str(record.get("local_date", "")))
        if when > date.today():
            raise ValueError
    except ValueError:
        problems.append("local_date: valid, nonfuture local date required")
    value = record.get("os_and_screen_reader")
    if (not isinstance(value, str) or not 3 <= len(value) <= 160
            or value.startswith("REPLACE")):
        problems.append("os_and_screen_reader: observed configuration required")
    if record.get("consent_to_observation") is not True:
        problems.append("consent_to_observation: explicit consent required")
    tasks = record.get("tasks")
    if not isinstance(tasks, dict) or set(tasks) != set(TASKS):
        problems.append("tasks: exactly A1-A5 required")
    else:
        for task in TASKS:
            row = tasks[task]
            if not isinstance(row, dict):
                problems.append(f"tasks.{task}: expected object")
                continue
            result = row.get("result")
            if result not in OUTCOMES:
                problems.append(f"tasks.{task}.result: actual observed outcome required")
            seconds = row.get("elapsed_seconds")
            if type(seconds) not in (int, float) or not 0 <= seconds <= 3600:
                problems.append(f"tasks.{task}.elapsed_seconds: measured duration required")
            hints = row.get("hints")
            if type(hints) is not int or not 0 <= hints <= 100:
                problems.append(f"tasks.{task}.hints: nonnegative integer required")
            if result == "unassisted_pass" and type(hints) is int and hints > 0:
                problems.append(f"tasks.{task}: hinted task cannot be unassisted")
            detail = row.get("observed_issue")
            if not isinstance(detail, str):
                problems.append(f"tasks.{task}.observed_issue: text required")
            elif result in {"assisted_pass", "fail", "blocked"} and not detail.strip():
                problems.append(f"tasks.{task}.observed_issue: explain observed friction")
    answers = record.get("comprehension")
    if not isinstance(answers, dict):
        problems.append("comprehension: missing")
    else:
        for question in QUESTIONS:
            answer = answers.get(question)
            if not isinstance(answer, str) or not answer.strip():
                problems.append(f"comprehension.{question}: actual response required")
    if record.get("independently_verified") is True:
        problems.append("independently_verified: must remain false before outside review")
    if record.get("release_gate_accepted") is True:
        problems.append("release_gate_accepted: cannot be self-awarded")
    return _summary("ready_for_review" if not problems else "incomplete", problems)


def _summary(status: str, problems: list[str]) -> dict:
    return {
        "kind": "independent_accessibility_observation_preflight",
        "status": status, "issues": problems,
        "assistive_technology_verified": False,
        "human_trial_verified": False, "release_gate_accepted": False,
    }


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("Usage: python -m tools.accessibility_evidence PRIVATE_RECORD.json",
              file=sys.stderr)
        return 2
    path = Path(args[0])
    try:
        if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size <= 131072:
            raise ValueError
        obj = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError):
        print(json.dumps(_summary("incomplete", ["file: invalid private JSON"])))
        return 2
    result = assess(obj)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "ready_for_review" else 1


if __name__ == "__main__":
    raise SystemExit(main())
