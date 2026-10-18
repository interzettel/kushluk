"""Human field proof is self-attested, never a software-approved physical gate."""
from hashlib import sha256
import json
import os

import pytest

from kushluk.cli import main
from kushluk.field_proof import FieldProofError, record_field_proof


def _files(tmp_path):
    artifact = tmp_path / "edition.pdf"
    artifact.write_bytes(b"%PDF artificial bytes for unit test")
    evidence = tmp_path / "photo.png"
    evidence.write_bytes(b"\x89PNG\r\n\x1a\noperator's own evidence placeholder")
    inspect = tmp_path / "inspection.json"
    inspect.write_text(json.dumps({
        "schema_version": 1, "pdf_sha256": sha256(artifact.read_bytes()).hexdigest(),
        "profile": "a4-home", "structural_errors": [], "visual_verified": False,
        "physical_verified": False,
    }))
    return artifact, evidence, inspect


def test_paper_pass_captures_hashes_but_never_validates_physical_result(tmp_path):
    artifact, photo, inspect = _files(tmp_path)
    receipt_path = tmp_path / "private" / "receipt.json"
    data = record_field_proof(
        kind="paper-a4", artifact=artifact, evidence=[photo],
        inspection=inspect, output=receipt_path, device="Example USB inkjet",
        operator="Local observer", observations="Printed 4 A4 pages, margins reviewed",
        result="pass", acknowledge=True,
    )
    assert data["operator_reported_result"] == "pass"
    assert data["independently_verified"] is False
    assert data["release_gate_accepted"] is False
    assert data["print_inspection_sha256"] == sha256(inspect.read_bytes()).hexdigest()
    assert "photo.png" not in receipt_path.read_text()
    assert "edition.pdf" not in receipt_path.read_text()
    if os.name != "nt":
        assert receipt_path.stat().st_mode & 0o777 == 0o600


def test_paper_pass_requires_matching_inspection_and_evidence(tmp_path):
    artifact, photo, inspect = _files(tmp_path)
    common = dict(
        kind="paper-a4", artifact=artifact, device="Inkjet", operator="Person",
        observations="All marks inspected", result="pass", output=tmp_path / "r.json",
        acknowledge=True,
    )
    with pytest.raises(FieldProofError, match="matching"):
        record_field_proof(evidence=[photo], **common)
    inspect.write_text(json.dumps({
        "schema_version": 1, "pdf_sha256": "wrong",
        "structural_errors": [],
    }))
    with pytest.raises(FieldProofError, match="does not match"):
        record_field_proof(evidence=[photo], inspection=inspect, **common)
    assert not (tmp_path / "r.json").exists()


def test_missing_photo_or_ack_cannot_claim_pass(tmp_path):
    artifact, photo, inspect = _files(tmp_path)
    base = dict(
        kind="epub-reader", artifact=tmp_path / "book.epub",
        device="Test e-reader", operator="Tester", observations="Read chapter navigation",
        result="pass", output=tmp_path / "reader.json",
    )
    base["artifact"].write_bytes(b"fake epub for unit test")
    with pytest.raises(FieldProofError, match="direct observation"):
        record_field_proof(evidence=[photo], acknowledge=False, **base)
    with pytest.raises(FieldProofError, match="direct observation"):
        record_field_proof(evidence=[], acknowledge=True, **base)


def test_fail_receipt_stays_a_fail_and_never_overwrites(tmp_path):
    artifact, _, _ = _files(tmp_path)
    path = tmp_path / "failed.json"
    kwargs = dict(
        kind="paper-a4", artifact=artifact, evidence=[], output=path,
        device="Printer", operator="Tester", observations="Duplex reversed",
        result="fail", acknowledge=False,
    )
    report = record_field_proof(**kwargs)
    assert report["operator_reported_result"] == "fail"
    assert report["release_gate_accepted"] is False
    before = path.read_bytes()
    with pytest.raises(FieldProofError, match="exists"):
        record_field_proof(**kwargs)
    assert path.read_bytes() == before


def test_cli_reader_proof_records_no_automatic_reader_certification(tmp_path, capsys):
    _, picture, _ = _files(tmp_path)
    epub = tmp_path / "sample.epub"
    epub.write_bytes(b"synthetic EPUB bytes for unit test")
    output = tmp_path / "receipt.json"
    assert main([
        "record-field-proof", "--kind", "epub-reader",
        "--artifact", str(epub), "--output", str(output),
        "--device", "Example e-reader", "--operator", "Operator",
        "--observations", "Chapter links work on device",
        "--result", "pass", "--evidence", str(picture),
        "--acknowledge-direct-observation",
    ]) == 0
    response = json.loads(capsys.readouterr().out)
    assert response["status"] == "operator_report_recorded"
    assert response["independently_verified"] is False
    assert response["release_gate_accepted"] is False


def test_symlink_evidence_rejected(tmp_path):
    _, photo, _ = _files(tmp_path)
    alias = tmp_path / "linked.png"
    alias.symlink_to(photo)
    epub = tmp_path / "test.epub"
    epub.write_bytes(b"something")
    with pytest.raises(FieldProofError, match="symlink"):
        record_field_proof(
            kind="epub-reader", artifact=epub, evidence=[alias],
            device="Device", operator="Human", observations="Inspected page",
            result="pass", acknowledge=True, output=tmp_path / "r.json",
        )


def test_letter_field_receipt_requires_matching_letter_profile(tmp_path):
    artifact, photo, inspection = _files(tmp_path)
    report = json.loads(inspection.read_text())
    report["profile"] = "letter-home"
    inspection.write_text(json.dumps(report))
    output = tmp_path / "private" / "letter.json"
    data = record_field_proof(
        kind="paper-letter", artifact=artifact, evidence=[photo],
        inspection=inspection, output=output, device="US home Letter printer",
        operator="Observer", observations="Real four-page US Letter trial inspected",
        result="pass", acknowledge=True,
    )
    assert data["kind"] == "paper-letter"
    assert data["independently_verified"] is False
    assert data["release_gate_accepted"] is False
    assert data["print_inspection_sha256"] == sha256(inspection.read_bytes()).hexdigest()


@pytest.mark.parametrize("profile", ["a4-home", "a3-folded", None, "custom"])
def test_letter_cannot_use_another_paper_inspection(tmp_path, profile):
    artifact, photo, inspect = _files(tmp_path)
    record = json.loads(inspect.read_text())
    if profile is not None:
        record["profile"] = profile
    inspect.write_text(json.dumps(record))
    target = tmp_path / "receipt.json"
    with pytest.raises(FieldProofError, match="does not match"):
        record_field_proof(
            kind="paper-letter", artifact=artifact, evidence=[photo],
            inspection=inspect, output=target, device="Printer",
            operator="Human", observations="Test observation", result="pass",
            acknowledge=True,
        )
    assert not target.exists()


def test_cli_letter_record_does_not_claim_real_acceptance(tmp_path, capsys):
    artifact, photo, inspect = _files(tmp_path)
    record = json.loads(inspect.read_text())
    record["profile"] = "letter-home"
    inspect.write_text(json.dumps(record))
    output = tmp_path / "private" / "letter-field.json"
    assert main([
        "record-field-proof", "--kind", "paper-letter",
        "--artifact", str(artifact), "--inspection", str(inspect),
        "--device", "Home Letter printer", "--operator", "Observer",
        "--observations", "Measured margins and four physical pages",
        "--result", "pass", "--evidence", str(photo),
        "--acknowledge-direct-observation", "--output", str(output),
    ]) == 0
    response = json.loads(capsys.readouterr().out)
    assert response["kind"] == "paper-letter"
    assert response["independently_verified"] is False
    assert response["release_gate_accepted"] is False


def test_a4_and_a3_reject_cross_profile_inspection_if_provided(tmp_path):
    artifact, photo, inspect = _files(tmp_path)
    record = json.loads(inspect.read_text())
    record["profile"] = "letter-home"
    inspect.write_text(json.dumps(record))
    for kind in ("paper-a4", "paper-a3"):
        with pytest.raises(FieldProofError, match="does not match"):
            record_field_proof(
                kind=kind, artifact=artifact, inspection=inspect, evidence=[photo],
                output=tmp_path / "receipt.json", device="Printer",
                operator="Observer", observations="Observation",
                result="pass", acknowledge=True,
            )


@pytest.mark.parametrize("kind, wrong", [
    ("paper-a4", None),
    ("paper-a3", None),
    ("paper-a4", "letter-home"),
    ("paper-a3", "a4-home"),
])
def test_passing_paper_requires_exact_explicit_profile(tmp_path, kind, wrong):
    artifact, photo, inspect = _files(tmp_path)
    inspection = json.loads(inspect.read_text())
    if wrong is None:
        inspection.pop("profile", None)
    else:
        inspection["profile"] = wrong
    inspect.write_text(json.dumps(inspection))
    target = tmp_path / "private" / "field.json"
    with pytest.raises(FieldProofError, match="does not match"):
        record_field_proof(
            kind=kind, artifact=artifact, evidence=[photo],
            inspection=inspect, output=target, device="Observed printer",
            operator="Observer", observations="Real physical inspection",
            result="pass", acknowledge=True,
        )
    assert not target.exists()


@pytest.mark.parametrize("bad_errors", [{}, "unverified", None, False])
def test_passing_paper_rejects_nonstrict_inspection_errors(tmp_path, bad_errors):
    artifact, photo, inspect = _files(tmp_path)
    inspection = json.loads(inspect.read_text())
    inspection["structural_errors"] = bad_errors
    inspect.write_text(json.dumps(inspection))
    with pytest.raises(FieldProofError, match="does not match"):
        record_field_proof(
            kind="paper-a4", artifact=artifact, evidence=[photo],
            inspection=inspect, output=tmp_path / "private" / "field.json",
            device="Printer", operator="Observer", observations="Real inspection",
            result="pass", acknowledge=True,
        )


def test_private_receipt_refuses_symlink_directory(tmp_path):
    artifact, photo, inspect = _files(tmp_path)
    real = tmp_path / "private"
    real.mkdir(mode=0o700)
    alias = tmp_path / "link"
    alias.symlink_to(real, target_is_directory=True)
    target = alias / "receipt.json"
    with pytest.raises(FieldProofError, match="symlink"):
        record_field_proof(
            kind="paper-a4", artifact=artifact, evidence=[photo],
            inspection=inspect, output=target,
            device="Printer", operator="Observer", observations="Real inspection",
            result="pass", acknowledge=True,
        )
    assert not target.exists()


def test_private_receipt_refuses_public_directory(tmp_path):
    artifact, photo, inspect = _files(tmp_path)
    target_dir = tmp_path / "public"
    target_dir.mkdir()
    target_dir.chmod(0o755)
    target = target_dir / "receipt.json"
    with pytest.raises(FieldProofError, match="private"):
        record_field_proof(
            kind="paper-a4", artifact=artifact, evidence=[photo],
            inspection=inspect, output=target,
            device="Printer", operator="Observer", observations="Real inspection",
            result="pass", acknowledge=True,
        )
    assert not target.exists()
