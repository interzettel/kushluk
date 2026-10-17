"""Synthetic accessibility record schema validation, not a user trial."""
from datetime import date
import json
from pathlib import Path

from tools.accessibility_evidence import assess, main


def fixture():
    data = json.loads(Path("docs/ACCESSIBILITY_TEMPLATE.json").read_text())
    data.update({
        "status": "observation", "source_commit": "a" * 40,
        "participant_code": "participant-02", "observer_code": "observer-01",
        "local_date": date.today().isoformat(),
        "os_and_screen_reader": "macOS VoiceOver synthetic configuration",
        "consent_to_observation": True,
    })
    for row in data["tasks"].values():
        row.update(result="unassisted_pass", elapsed_seconds=42,
                   hints=0, observed_issue="")
    for name in data["comprehension"]:
        data["comprehension"][name] = "synthetic non-human response"
    return data


def test_unfilled_is_template_not_a_human_pass():
    data = json.loads(Path("docs/ACCESSIBILITY_TEMPLATE.json").read_text())
    assert assess(data)["status"] == "template"
    assert assess(data)["release_gate_accepted"] is False


def test_completed_record_is_only_ready_for_review():
    result = assess(fixture())
    assert result["status"] == "ready_for_review"
    assert not result["human_trial_verified"]
    assert not result["assistive_technology_verified"]
    assert not result["release_gate_accepted"]
    assert result["issues"] == []


def test_preflight_rejects_hints_and_false_signoffs():
    data = fixture()
    data["tasks"]["A2"].update(result="unassisted_pass", hints=1)
    data["tasks"]["A4"].update(result="blocked", observed_issue="")
    data["independently_verified"] = True
    data["release_gate_accepted"] = True
    problems = assess(data)["issues"]
    assert any("A2" in p for p in problems)
    assert any("A4" in p for p in problems)
    assert any("release_gate_accepted" in p for p in problems)
    assert assess(data)["status"] == "incomplete"


def test_cli_redacts_screen_reader_notes_and_refuses_symlinks(tmp_path, capsys):
    data = fixture()
    secret = "PRIVATE_CALENDAR_TOKEN_NEVER_ECHO"
    data["tasks"]["A3"]["observed_issue"] = secret
    path = tmp_path / "pilot.json"
    path.write_text(json.dumps(data))
    assert main([str(path)]) == 0
    output = capsys.readouterr().out
    assert "ready_for_review" in output
    assert secret not in output
    assert data["participant_code"] not in output
    link = tmp_path / "pilot-alias"
    link.symlink_to(path)
    assert main([str(link)]) == 2
    assert "incomplete" in capsys.readouterr().out
