"""Local-only preflight for an observed U1–U6 pilot JSON.

Checks completeness and internal consistency, NOT whether an observer is
independent or a release gate has passed. Does not upload records or echo notes.
Usage: python -m tools.first_reader_evidence PRIVATE_RECORD.json
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path


TASK_IDS = tuple(f"U{i}" for i in range(1, 7))
RESULTS = {"unassisted_pass", "assisted_pass", "fail", "blocked", "not_attempted"}
PROMPTS = (
    "external_data_expectation", "rss_approval_meaning",
    "print_or_schedule_expectation", "hardest_step", "repeat_setup_intent",
)


def assess(record: object) -> dict:
    """Return safe field-level diagnostics; no values from the record are echoed."""
    problems = []
    if not isinstance(record, dict):
        return _report("incomplete", ["root: expected JSON object"])
    if record.get("schema_version") != 1:
        problems.append("schema_version: expected 1")
    if record.get("status") == "template-not-observation":
        return _report("template", ["status: this is the untouched observation template"])
    if record.get("status") != "observation":
        problems.append("status: set observation only after a real observed session")

    for field in ("observer_code", "participant_code"):
        value = record.get(field)
        if (not isinstance(value, str) or not re.fullmatch(r"[a-zA-Z0-9_-]{2,64}", value)
                or value in {"REPLACE", "ANONYMOUS_CODE"}
                or "@" in value):
            problems.append(f"{field}: use an anonymous non-placeholder code")
    if record.get("observer_code") == record.get("participant_code"):
        problems.append("observer_code/participant_code: must be independent identifiers")
    commit = record.get("source_commit")
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
        problems.append("source_commit: expected a real 40-character commit SHA")
    date_value = record.get("local_date")
    try:
        observed = date.fromisoformat(date_value) if isinstance(date_value, str) else None
        if observed is None or observed > date.today():
            raise ValueError
    except ValueError:
        problems.append("local_date: expected a valid, nonfuture ISO date")
    for field in ("os_and_version", "device_context"):
        value = record.get(field)
        if (not isinstance(value, str) or len(value.strip()) < 3
                or value.startswith(("REPLACE", "OWN_OR_BORROWED"))):
            problems.append(f"{field}: required observed context (no private identifiers)")
    if record.get("consent_to_observation") is not True:
        problems.append("consent_to_observation: must be explicitly true")

    tasks = record.get("tasks")
    if not isinstance(tasks, dict) or set(tasks) != set(TASK_IDS):
        problems.append("tasks: exactly U1–U6 are required")
    else:
        for name in TASK_IDS:
            item = tasks[name]
            if not isinstance(item, dict):
                problems.append(f"tasks.{name}: expected object")
                continue
            result = item.get("result")
            if result not in RESULTS or result == "not_attempted":
                problems.append(f"tasks.{name}.result: needs an actual observation")
            seconds = item.get("elapsed_seconds")
            if type(seconds) not in {float, int} or not 0 <= seconds <= 86400:
                problems.append(f"tasks.{name}.elapsed_seconds: expected measured duration")
            hints = item.get("hints")
            if type(hints) is not int or not 0 <= hints <= 100:
                problems.append(f"tasks.{name}.hints: expected nonnegative integer")
            if result == "unassisted_pass" and isinstance(hints, int) and hints > 0:
                problems.append(f"tasks.{name}: a hinted task cannot be unassisted")
            observed_issue = item.get("observed_issue")
            if not isinstance(observed_issue, str):
                problems.append(f"tasks.{name}.observed_issue: expected text")
            elif result in {"fail", "blocked", "assisted_pass"} and not observed_issue.strip():
                problems.append(f"tasks.{name}.observed_issue: explain the observed friction")
            if not isinstance(item.get("evidence_reference"), str):
                problems.append(f"tasks.{name}.evidence_reference: expected text")

    answers = record.get("comprehension")
    if not isinstance(answers, dict):
        problems.append("comprehension: required post-task responses")
    else:
        for name in PROMPTS:
            value = answers.get(name)
            if not isinstance(value, str) or not value.strip():
                problems.append(f"comprehension.{name}: missing actual response")

    if record.get("independently_verified") is True:
        problems.append("independently_verified: review must occur outside this local tool")
    if record.get("release_gate_accepted") is True:
        problems.append("release_gate_accepted: this tool cannot certify a release gate")
    return _report("ready_for_review" if not problems else "incomplete", problems)


def _report(status: str, problems: list[str]) -> dict:
    return {
        "kind": "first_reader_observation_preflight",
        "status": status,
        "human_trial_verified": False,
        "release_gate_accepted": False,
        "issues": problems,
    }


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("Usage: python -m tools.first_reader_evidence PRIVATE_RECORD.json", file=sys.stderr)
        return 2
    try:
        source = Path(args[0])
        if source.is_symlink() or not source.is_file() or source.stat().st_size > 131072:
            raise ValueError
        record = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError):
        print(json.dumps(_report("incomplete", ["file: unreadable or invalid private JSON"])))
        return 2
    result = assess(record)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "ready_for_review" else 1


if __name__ == "__main__":
    raise SystemExit(main())
