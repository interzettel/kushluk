"""Observer records are never uploaded or mistaken for human acceptance."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from tools.first_reader_evidence import assess, main


def sample():
    record = json.loads(Path("docs/FIRST_READER_TEMPLATE.json").read_text(encoding="utf-8"))
    record.update({
        "status": "observation",
        "source_commit": "a" * 40,  # synthetic shape test, not a real commit
        "observer_code": "observer-01", "participant_code": "reader-02",
        "local_date": date.today().isoformat(),
        "os_and_version": "Test OS version",
        "device_context": "Borrowed laptop",
        "consent_to_observation": True,
    })
    for row in record["tasks"].values():
        row.update(result="unassisted_pass", elapsed_seconds=12, hints=0,
                   observed_issue="", evidence_reference="")
    for name in record["comprehension"]:
        record["comprehension"][name] = "Synthetic response; not a real person"
    return record


def test_blank_template_cannot_be_counted_as_observation():
    raw = json.loads(Path("docs/FIRST_READER_TEMPLATE.json").read_text())
    report = assess(raw)
    assert report["status"] == "template"
    assert report["human_trial_verified"] is False
    assert report["release_gate_accepted"] is False


def test_completed_schema_is_only_ready_for_review():
    report = assess(sample())
    assert report == {
        "kind": "first_reader_observation_preflight",
        "status": "ready_for_review",
        "human_trial_verified": False,
        "release_gate_accepted": False,
        "issues": [],
    }


def test_missing_consent_and_unattempted_tasks_block_preflight():
    record = sample()
    record["consent_to_observation"] = False
    record["tasks"]["U5"]["result"] = "not_attempted"
    issues = assess(record)["issues"]
    assert "consent_to_observation: must be explicitly true" in issues
    assert any("U5.result" in issue for issue in issues)


def test_hinted_unassisted_and_unspecified_failure_are_rejected():
    record = sample()
    record["tasks"]["U2"].update(result="unassisted_pass", hints=2)
    record["tasks"]["U4"].update(result="fail", observed_issue="")
    record["tasks"]["U3"]["elapsed_seconds"] = -1
    issues = assess(record)["issues"]
    assert any("tasks.U2" in issue for issue in issues)
    assert any("tasks.U4.observed_issue" in issue for issue in issues)
    assert any("tasks.U3.elapsed_seconds" in issue for issue in issues)


def test_self_asserted_verification_and_release_gate_not_accepted():
    record = sample()
    record["independently_verified"] = True
    record["release_gate_accepted"] = True
    report = assess(record)
    assert report["status"] == "incomplete"
    assert report["human_trial_verified"] is False
    assert report["release_gate_accepted"] is False


def test_cli_does_not_echo_private_notes(tmp_path, capsys):
    record = sample()
    record["tasks"]["U2"]["observed_issue"] = "SECRET_NOTE_DO_NOT_ECHO"
    file = tmp_path / "private.json"
    file.write_text(json.dumps(record), encoding="utf-8")
    assert main([str(file)]) == 0
    displayed = capsys.readouterr().out
    assert "ready_for_review" in displayed
    assert "SECRET_NOTE_DO_NOT_ECHO" not in displayed
    assert "Synthetic response" not in displayed
    assert record["observer_code"] not in displayed


def test_bad_json_and_symlink_not_read(tmp_path, capsys):
    file = tmp_path / "bad.json"
    file.write_text("{ broken")
    assert main([str(file)]) == 2
    assert "incomplete" in capsys.readouterr().out
    good = tmp_path / "good.json"
    good.write_text(json.dumps(sample()))
    link = tmp_path / "link.json"
    link.symlink_to(good)
    assert main([str(link)]) == 2
    assert "incomplete" in capsys.readouterr().out
