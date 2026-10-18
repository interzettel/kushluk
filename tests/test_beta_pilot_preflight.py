"""M2a preflight is intentionally a *non-approval* of physical/beta gates."""
from __future__ import annotations

from datetime import date, datetime, timezone
from hashlib import sha256
import json

from tools import beta_pilot_preflight as beta


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj), encoding="utf-8")
    return path


def paper_packet(tmp_path):
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF synthetic only, NOT physical print")
    inspection = write_json(tmp_path / "inspection.json", {
        "schema_version": 1, "profile": "a4-home",
        "pdf_sha256": sha256(pdf.read_bytes()).hexdigest(),
        "structural_errors": [], "physical_verified": False,
    })
    photo = tmp_path / "synthetic-photo.png"
    photo.write_bytes(b"synthetic test photo with secret INJECTED-OBSERVER-NOTE")
    receipt = write_json(tmp_path / "private" / "paper.json", {
        "schema_version": 1, "kind": "paper-a4",
        "operator_reported_result": "pass",
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "operator_identifier": "NOT_A_REAL_PERSON",
        "device_description": "TEST_NOT_A_REAL_PRINTER",
        "observations": "INJECTED-OBSERVER-NOTE",
        "artifact": {"sha256": sha256(pdf.read_bytes()).hexdigest(),
                     "bytes": pdf.stat().st_size},
        "print_inspection_sha256": sha256(inspection.read_bytes()).hexdigest(),
        "evidence_files": [{"sha256": sha256(photo.read_bytes()).hexdigest(),
                            "bytes": photo.stat().st_size}],
        "acknowledged_direct_observation": True,
        "attestation": "operator-self-report; not independently validated",
        "independently_verified": False, "release_gate_accepted": False,
    })
    return receipt, pdf, inspection, photo


def reader_packet(tmp_path):
    src = json.loads((beta.Path("docs/FIRST_READER_TEMPLATE.json")).read_text())
    src.update({
        "status": "observation", "source_commit": "a"*40,
        "observer_code": "observer-01", "participant_code": "user-02",
        "local_date": date.today().isoformat(),
        "os_and_version": "TEST synthetic macOS",
        "device_context": "TEST mocked Mac",
        "consent_to_observation": True,
    })
    for task in src["tasks"].values():
        task.update({"result": "unassisted_pass", "elapsed_seconds": 42,
                     "hints": 0, "observed_issue": "",
                     "evidence_reference": ""})
    for key in src["comprehension"]:
        src["comprehension"][key] = "Synthetic TEST-SECRET-ANSWER"
    return write_json(tmp_path / "private" / "reader.json", src)


def safety_packet(tmp_path):
    return write_json(tmp_path / "private" / "safety.json", {
        "schema_version": 1, "status": "operator-checklist",
        "checks": {name: True for name in beta._REQUIRED_SAFETY},
        "human_rights_review_completed": False,
        "independently_verified": False,
        "release_gate_accepted": False,
    })


def test_empty_packet_is_missing_without_asserting_acceptance():
    report = beta.assess_beta()
    assert report["status"] == "operator_evidence_incomplete"
    assert set(report["domains"]) == {
        "paper", "host", "first_reader", "source_rights_safety",
    }
    assert all(x == "missing_operator_evidence" for x in report["domains"].values())
    assert report["G1_to_G8_independently_verified"] == 0
    assert not report["beta_publication_authorized"]


def test_hash_linked_synthetic_packet_only_ready_for_outside_review(tmp_path, monkeypatch):
    receipt, pdf, inspect, photo = paper_packet(tmp_path)
    reader = reader_packet(tmp_path)
    safety = safety_packet(tmp_path)
    archive, host = tmp_path / "archive", tmp_path / "receipts"
    archive.mkdir()
    host.mkdir()

    def stub_review(**kwargs):
        return {"days": [
            {"software_completed_with_validated_archive": i == 0,
             "matching_operator_host_pass_reported": i == 0,
             "expected_scheduler_start_recorded": i == 0} for i in range(5)
        ]}
    monkeypatch.setattr(beta, "review_host_trial", stub_review)
    report = beta.assess_beta(
        a4_receipt=receipt, pdf=pdf, inspection=inspect, paper_evidence=[photo],
        reader_record=reader, safety_checklist=safety,
        archive_root=archive, host_receipts=host, host_start=date(2026, 10, 18),
    )
    assert report["status"] == "operator_packet_ready_for_independent_review"
    assert not report["beta_publication_authorized"]
    assert not report["actual_printer_verified"]
    assert not report["unattended_host_verified"]
    assert not report["first_reader_independently_verified"]
    assert report["G1_to_G8_independently_verified"] == 0
    contents = json.dumps(report)
    for secret in ("INJECTED-OBSERVER-NOTE", "NOT_A_REAL_PERSON", "TEST-SECRET-ANSWER",
                   str(tmp_path)):
        assert secret not in contents


def test_paper_fails_on_tampered_files_missing_profile_and_fake_approval(tmp_path):
    receipt, pdf, inspection, photo = paper_packet(tmp_path)
    assert beta.inspect_paper(receipt, pdf, inspection, [photo])["status"] == (
        "operator_paper_report_correlated"
    )
    before = json.loads(receipt.read_text())
    for key, value in [("release_gate_accepted", True),
                       ("independently_verified", True)]:
        data = dict(before)
        data[key] = value
        write_json(receipt, data)
        assert beta.assess_beta(
            a4_receipt=receipt, pdf=pdf, inspection=inspection,
            paper_evidence=[photo],
        )["domains"]["paper"] == "operator_evidence_invalid_or_incomplete"
    write_json(receipt, before)
    photo.write_bytes(b"modified fake photo")
    assert beta.assess_beta(
        a4_receipt=receipt, pdf=pdf, inspection=inspection, paper_evidence=[photo],
    )["domains"]["paper"] == "operator_evidence_invalid_or_incomplete"


def test_reader_assistance_or_failed_consent_never_passes_packet(tmp_path):
    reader = reader_packet(tmp_path)
    assert beta.inspect_reader(reader)["status"] == "novice_observation_ready_for_review"
    data = json.loads(reader.read_text())
    data["tasks"]["U3"]["result"] = "assisted_pass"
    data["tasks"]["U3"]["observed_issue"] = "Hint required"
    write_json(reader, data)
    assert beta.assess_beta(reader_record=reader)["domains"]["first_reader"] == (
        "operator_evidence_invalid_or_incomplete"
    )
    data["tasks"]["U3"]["result"] = "unassisted_pass"
    data["tasks"]["U3"]["observed_issue"] = ""
    data["consent_to_observation"] = False
    write_json(reader, data)
    assert beta.assess_beta(reader_record=reader)["domains"]["first_reader"] == (
        "operator_evidence_invalid_or_incomplete"
    )


def test_safety_checklist_does_not_count_as_legal_rights_approval(tmp_path):
    checklist = safety_packet(tmp_path)
    assert beta.inspect_safety(checklist)["human_rights_review_completed"] is False
    data = json.loads(checklist.read_text())
    data["human_rights_review_completed"] = True
    write_json(checklist, data)
    assert beta.assess_beta(safety_checklist=checklist)["domains"][
        "source_rights_safety"
    ] == "operator_evidence_invalid_or_incomplete"


def test_operator_safety_record_must_not_self_accept_release_gate(tmp_path):
    checklist = safety_packet(tmp_path)
    data = json.loads(checklist.read_text())
    for claimed in (True, None):
        submitted = dict(data)
        if claimed is None:
            submitted.pop("release_gate_accepted")
        else:
            submitted["release_gate_accepted"] = claimed
        write_json(checklist, submitted)
        assert beta.assess_beta(safety_checklist=checklist)["domains"][
            "source_rights_safety"
        ] == "operator_evidence_invalid_or_incomplete"


def test_no_private_content_in_cli_output(tmp_path, capsys):
    receipt, pdf, inspection, photo = paper_packet(tmp_path)
    assert beta.main([
        "--a4-receipt", str(receipt), "--pdf", str(pdf),
        "--inspection", str(inspection), "--paper-evidence", str(photo),
    ]) == 1
    output = capsys.readouterr().out
    assert "paper" in output
    assert "INJECTED-OBSERVER-NOTE" not in output
    assert str(tmp_path) not in output


def test_symlinked_private_input_fails_closed(tmp_path):
    receipt, pdf, inspection, photo = paper_packet(tmp_path)
    alias = tmp_path / "alias.json"
    alias.symlink_to(receipt)
    report = beta.assess_beta(a4_receipt=alias, pdf=pdf, inspection=inspection,
                              paper_evidence=[photo])
    assert report["domains"]["paper"] == "operator_evidence_invalid_or_incomplete"
