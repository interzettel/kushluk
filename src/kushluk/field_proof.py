"""Local evidence receipts for real hardware/reader trials, never automatic gate approval."""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path

KINDS = ("paper-a4", "paper-letter", "paper-a3", "epub-reader", "host-resume")
RESULTS = ("pass", "fail", "blocked")
MAX_EVIDENCE_BYTES = 50 * 1024 * 1024


class FieldProofError(ValueError):
    """Sanitized operator-facing input error."""


def _fingerprint(path: Path, *, limit: int = MAX_EVIDENCE_BYTES) -> dict:
    if path.is_symlink() or not path.is_file():
        raise FieldProofError("Evidence must be a regular local file, not a symlink")
    try:
        size = path.stat().st_size
        if size <= 0 or size > limit:
            raise FieldProofError("Evidence file is empty or exceeds 50 MiB")
        digest = sha256()
        with path.open("rb") as data:
            for piece in iter(lambda: data.read(64 * 1024), b""):
                digest.update(piece)
    except OSError as exc:
        raise FieldProofError("Cannot open local evidence file") from exc
    return {"sha256": digest.hexdigest(), "bytes": size}


def _inspection_hash(path: Path, expected_sha: str, kind: str) -> str:
    if path.is_symlink():
        raise FieldProofError("Inspection must be a local regular file")
    try:
        if not path.is_file() or path.stat().st_size > 2 * 1024 * 1024:
            raise FieldProofError("Print inspection report is missing or oversized")
        report = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise FieldProofError("Invalid print inspection JSON") from exc
    expected_profile = {"paper-a4": "a4-home", "paper-letter": "letter-home",
                        "paper-a3": "a3-folded"}[kind]
    observed_profile = report.get("profile") if isinstance(report, dict) else None
    if (not isinstance(report, dict) or report.get("pdf_sha256") != expected_sha
            or report.get("structural_errors") or report.get("schema_version") != 1
            or (observed_profile is not None and observed_profile != expected_profile)
            or (kind == "paper-letter" and observed_profile != "letter-home")):
        raise FieldProofError("Print inspection does not match a structurally valid PDF")
    return _fingerprint(path)["sha256"]


def record_field_proof(
    *, kind: str, artifact: Path, output: Path, device: str, operator: str,
    observations: str, result: str, evidence: list[Path],
    acknowledge: bool, inspection: Path | None = None,
) -> dict:
    """Document a *self-reported observation*, not confirm the actual hardware result."""
    if kind not in KINDS or result not in RESULTS:
        raise FieldProofError("Unknown field trial kind or result")
    if not device.strip() or len(device) > 200:
        raise FieldProofError("A concise device/host model is required")
    if not operator.strip() or len(operator) > 120:
        raise FieldProofError("An actual observer identifier is required")
    if not observations.strip() or len(observations) > 1200:
        raise FieldProofError("Observed conditions and defects are required")
    if len(evidence) > 8:
        raise FieldProofError("No more than eight evidence files per trial")
    if result == "pass" and (not acknowledge or not evidence):
        raise FieldProofError("Passing requires explicit direct observation and evidence")
    if kind.startswith("paper-") and artifact.suffix.lower() != ".pdf":
        raise FieldProofError("Paper proof requires a PDF artifact")
    if kind == "epub-reader" and artifact.suffix.lower() != ".epub":
        raise FieldProofError("E-reader proof requires an EPUB artifact")
    artifact_info = _fingerprint(artifact)
    inspection_sha = None
    if inspection is not None:
        if not kind.startswith("paper-"):
            raise FieldProofError("Print inspection only applies to physical paper trials")
        inspection_sha = _inspection_hash(inspection, artifact_info["sha256"], kind)
    if kind.startswith("paper-") and result == "pass" and inspection_sha is None:
        raise FieldProofError("Passing paper proof requires matching PDF inspection JSON")
    evidence_info = [_fingerprint(path) for path in evidence]
    receipt = {
        "schema_version": 1,
        "kind": kind,
        "operator_reported_result": result,
        "observed_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "operator_identifier": operator.strip(),
        "device_description": device.strip(),
        "observations": observations.strip(),
        "artifact": artifact_info,
        "print_inspection_sha256": inspection_sha,
        "evidence_files": evidence_info,
        "acknowledged_direct_observation": bool(acknowledge),
        "attestation": "operator-self-report; not independently validated",
        "independently_verified": False,
        "release_gate_accepted": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        fd = os.open(output, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise FieldProofError("Receipt already exists; use a unique output filename") from exc
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as file:
            json.dump(receipt, file, ensure_ascii=False, indent=2)
            file.write("\n")
            file.flush()
            os.fsync(file.fileno())
    except BaseException:
        output.unlink(missing_ok=True)
        raise
    return receipt
