"""Private, read-only M2a beta evidence triage; NEVER an acceptance signature.

Cross-checks a genuine operator's *own* A4 receipt against the actual PDF,
inspection report and evidence file bytes; reviews private novice feedback;
and correlates a scheduled host receipt with self-attested local evidence.
All records remain on the computer and no names, paths, contents, document
titles or participant statements appear in the output.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re

from kushluk.host_trial_review import HostTrialReviewError, review_host_trial
from tools.first_reader_evidence import assess as assess_reader


class BetaEvidenceError(ValueError):
    """Safe, fixed classification only; never expose private source data."""


_SHA = re.compile(r"[0-9a-f]{64}\Z")
_REQUIRED_SAFETY = (
    "private_data_remains_on_owner_device",
    "sources_have_explicit_approved_rights_or_synthetic_only",
    "operator_has_permission_to_use_printer",
    "participant_consented_to_observation",
    "host_schedule_and_retry_policy_reviewed",
    "failure_and_rollback_instructions_understood",
)


def _private_json(path: Path, limit: int = 131072) -> dict:
    try:
        if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size <= limit:
            raise BetaEvidenceError("invalid_private_json")
        result = json.loads(path.read_bytes())
        if not isinstance(result, dict):
            raise BetaEvidenceError("invalid_private_json")
        return result
    except (OSError, UnicodeError, ValueError) as exc:
        raise BetaEvidenceError("invalid_private_json") from exc


def _digest(path: Path, *, max_bytes: int = 50 * 1024 * 1024) -> tuple[str, int]:
    try:
        if path.is_symlink() or not path.is_file():
            raise BetaEvidenceError("invalid_local_evidence")
        size = path.stat().st_size
        if not 0 < size <= max_bytes:
            raise BetaEvidenceError("invalid_local_evidence")
        h = sha256()
        with path.open("rb") as source:
            for chunk in iter(lambda: source.read(65536), b""):
                h.update(chunk)
        if path.stat().st_size != size:
            raise BetaEvidenceError("evidence_changed_during_read")
        return h.hexdigest(), size
    except OSError as exc:
        raise BetaEvidenceError("invalid_local_evidence") from exc


def _sha_entry(claim: object, actual: tuple[str, int]) -> bool:
    return (
        isinstance(claim, dict)
        and isinstance(claim.get("sha256"), str)
        and _SHA.fullmatch(claim["sha256"]) is not None
        and claim["sha256"] == actual[0]
        and type(claim.get("bytes")) is int
        and claim["bytes"] == actual[1]
    )


def inspect_paper(a4_receipt: Path, pdf: Path, inspection: Path,
                  evidence_files: list[Path]) -> dict:
    """Verify consistency only; physical observation remains self-reported."""
    record = _private_json(a4_receipt)
    report = _private_json(inspection, limit=2 * 1024 * 1024)
    try:
        observed = datetime.fromisoformat(record["observed_at_utc"])
        if (observed.tzinfo is None or observed.utcoffset() is None
                or observed.astimezone(timezone.utc) > datetime.now(timezone.utc)):
            raise BetaEvidenceError("invalid_observation_time")
    except (KeyError, TypeError, ValueError) as exc:
        raise BetaEvidenceError("invalid_observation_time") from exc
    if (
        record.get("schema_version") != 1
        or record.get("kind") != "paper-a4"
        or record.get("operator_reported_result") != "pass"
        or record.get("acknowledged_direct_observation") is not True
        or record.get("attestation") != "operator-self-report; not independently validated"
        or record.get("independently_verified") is not False
        or record.get("release_gate_accepted") is not False
        or not isinstance(record.get("operator_identifier"), str)
        or not record["operator_identifier"].strip()
        or not isinstance(record.get("device_description"), str)
        or not record["device_description"].strip()
    ):
        raise BetaEvidenceError("invalid_operator_paper_receipt")
    if not _sha_entry(record.get("artifact"), _digest(pdf)):
        raise BetaEvidenceError("pdf_identity_mismatch")
    try:
        if (
            report.get("schema_version") != 1
            or report.get("profile") != "a4-home"
            or report.get("structural_errors") != []
            or report.get("pdf_sha256") != record["artifact"]["sha256"]
            or report.get("physical_verified") is True
        ):
            raise BetaEvidenceError("a4_inspection_mismatch")
    except (KeyError, TypeError) as exc:
        raise BetaEvidenceError("a4_inspection_mismatch") from exc
    if record.get("print_inspection_sha256") != _digest(
        inspection, max_bytes=2 * 1024 * 1024
    )[0]:
        raise BetaEvidenceError("inspection_identity_mismatch")
    claims = record.get("evidence_files")
    if (not isinstance(claims, list) or not 1 <= len(claims) <= 8
            or len(claims) != len(evidence_files)):
        raise BetaEvidenceError("paper_evidence_count_mismatch")
    if not all(_sha_entry(claim, _digest(path))
               for claim, path in zip(claims, evidence_files)):
        raise BetaEvidenceError("paper_evidence_identity_mismatch")
    return {
        "status": "operator_paper_report_correlated",
        "actual_pdf_bytes_matched": True,
        "inspection_and_evidence_bytes_matched": True,
        "physical_print_independently_verified": False,
    }


def inspect_reader(path: Path) -> dict:
    report = assess_reader(_private_json(path))
    if report["status"] != "ready_for_review":
        raise BetaEvidenceError("reader_observation_incomplete")
    record = _private_json(path)
    outcomes = record["tasks"]
    if any(outcomes[k]["result"] != "unassisted_pass" for k in ("U2", "U3", "U4", "U5", "U6")):
        raise BetaEvidenceError("reader_requires_assistance_or_failed")
    if outcomes["U1"]["result"] not in {"assisted_pass", "unassisted_pass"}:
        raise BetaEvidenceError("reader_install_incomplete")
    return {
        "status": "novice_observation_ready_for_review",
        "install_was_assisted": outcomes["U1"]["result"] == "assisted_pass",
        "participant_independently_verified": False,
    }


def inspect_safety(path: Path) -> dict:
    record = _private_json(path)
    if (record.get("schema_version") != 1
            or record.get("status") != "operator-checklist"
            or not isinstance(record.get("checks"), dict)
            or set(record["checks"]) != set(_REQUIRED_SAFETY)
            or not all(record["checks"][name] is True for name in _REQUIRED_SAFETY)
            or record.get("human_rights_review_completed") is not False
            or record.get("independently_verified") is not False):
        raise BetaEvidenceError("safety_checklist_incomplete")
    return {
        "status": "operator_safety_checklist_complete",
        "human_rights_review_completed": False,
        "source_rights_independently_verified": False,
    }


def inspect_host(archive: Path, receipts: Path, start: date,
                 *, timezone: str = "Europe/Berlin") -> dict:
    report = review_host_trial(
        archive_root=archive, receipts_dir=receipts, start_date=start,
        days=5, timezone=timezone,
    )
    # First beta requires an actually recorded host run and a self-report;
    # the five consecutive days requirement is explicitly reserved for stable.
    observed = [
        d for d in report["days"]
        if d["software_completed_with_validated_archive"]
        and d["matching_operator_host_pass_reported"]
        and d["expected_scheduler_start_recorded"]
    ]
    if not observed:
        raise BetaEvidenceError("host_observation_missing_or_incomplete")
    return {
        "status": "host_operator_report_correlated",
        "matched_host_run_days": len(observed),
        "five_consecutive_unattended_mornings_verified": False,
        "wake_reboot_and_scheduler_independently_verified": False,
        "physical_delivery_independently_verified": False,
    }


def assess_beta(*, a4_receipt: Path | None = None, pdf: Path | None = None,
                inspection: Path | None = None, paper_evidence: list[Path] | None = None,
                reader_record: Path | None = None, safety_checklist: Path | None = None,
                archive_root: Path | None = None, host_receipts: Path | None = None,
                host_start: date | None = None, timezone: str = "Europe/Berlin") -> dict:
    """Fixed-code, content-free review checklist — even all matches NEVER pass beta."""
    paper_evidence = [] if paper_evidence is None else paper_evidence
    status = {}
    issues = []
    domains = {
        "paper": ((a4_receipt, pdf, inspection), bool(paper_evidence)),
        "host": ((archive_root, host_receipts, host_start), True),
        "first_reader": ((reader_record,), True),
        "source_rights_safety": ((safety_checklist,), True),
    }
    for name, (required, extra) in domains.items():
        if any(x is None for x in required) or not extra:
            status[name] = "missing_operator_evidence"
            issues.append(name + "_evidence_missing")
            continue
        try:
            if name == "paper":
                details = inspect_paper(a4_receipt, pdf, inspection, paper_evidence)
            elif name == "host":
                details = inspect_host(archive_root, host_receipts, host_start,
                                       timezone=timezone)
            elif name == "first_reader":
                details = inspect_reader(reader_record)
            else:
                details = inspect_safety(safety_checklist)
            status[name] = details["status"]
            if name == "first_reader" and details["install_was_assisted"]:
                issues.append("first_reader_install_assistance_needs_review")
        except (BetaEvidenceError, HostTrialReviewError, OSError, ValueError):
            status[name] = "operator_evidence_invalid_or_incomplete"
            issues.append(name + "_evidence_invalid_or_incomplete")
    all_matched = all(value not in {
        "missing_operator_evidence", "operator_evidence_invalid_or_incomplete",
    } for value in status.values())
    return {
        "schema_version": 1,
        "kind": "m2a_private_beta_operator_evidence_preflight",
        "milestone": "v0.3.0-beta.1",
        "status": ("operator_packet_ready_for_independent_review" if all_matched
                   else "operator_evidence_incomplete"),
        "domains": status,
        "issues": sorted(issues),
        "source_only_alpha_available": True,
        "actual_printer_verified": False,
        "unattended_host_verified": False,
        "first_reader_independently_verified": False,
        "source_permissions_independently_verified": False,
        "G1_to_G8_independently_verified": 0,
        "beta_version_bumped": False,
        "beta_tag_created": False,
        "beta_publication_authorized": False,
        "privacy": "Read-only; no private note, filename or path included",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--a4-receipt", type=Path)
    parser.add_argument("--pdf", type=Path)
    parser.add_argument("--inspection", type=Path)
    parser.add_argument("--paper-evidence", type=Path, action="append", default=[])
    parser.add_argument("--reader-record", type=Path)
    parser.add_argument("--safety-checklist", type=Path)
    parser.add_argument("--archive-root", type=Path)
    parser.add_argument("--host-receipts", type=Path)
    parser.add_argument("--host-start-date")
    parser.add_argument("--timezone", default="Europe/Berlin")
    args = parser.parse_args(argv)
    try:
        start = date.fromisoformat(args.host_start_date) if args.host_start_date else None
    except ValueError:
        print(json.dumps({"status": "rejected", "code": "invalid_host_start_date"}))
        return 2
    result = assess_beta(
        a4_receipt=args.a4_receipt, pdf=args.pdf, inspection=args.inspection,
        paper_evidence=args.paper_evidence, reader_record=args.reader_record,
        safety_checklist=args.safety_checklist,
        archive_root=args.archive_root, host_receipts=args.host_receipts,
        host_start=start, timezone=args.timezone,
    )
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0 if result["status"] == "operator_packet_ready_for_independent_review" else 1


if __name__ == "__main__":
    raise SystemExit(main())
