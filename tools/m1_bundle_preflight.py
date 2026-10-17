"""Independent, offline M1 artifact review; never authorizes or publishes a release.

Run this after tools.release_check against its output directory. Successful
software evidence can be REVIEWED for a proposed alpha; it is never an
approval of rights, physical delivery, a release tag or external invitations.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re

MAX_BYTES = 60 * 1024 * 1024
VERSION = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+(?:a[0-9]+)?\Z")
HEX_SHA = re.compile(r"[0-9a-f]{64}\Z")
PREVIEW = frozenset({
    "kushluk-preview.html", "kushluk-preview.md",
    "kushluk-preview-edition.json",
})
PROPOSED_TAG = "v0.2.0-alpha.1"


class M1EvidenceError(ValueError):
    """A release-evidence precondition failed (never display raw file data)."""


def _read_file(path: Path) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise M1EvidenceError("missing_or_unsafe_artifact")
    try:
        size = path.stat().st_size
        if not 0 < size <= MAX_BYTES:
            raise M1EvidenceError("artifact_empty_or_oversized")
        return path.read_bytes()
    except OSError as exc:
        raise M1EvidenceError("artifact_unreadable") from exc


def _read_json(path: Path) -> dict:
    raw = _read_file(path)
    if len(raw) > 2 * 1024 * 1024:
        raise M1EvidenceError("evidence_json_oversized")
    try:
        result = json.loads(raw)
    except (ValueError, UnicodeError) as exc:
        raise M1EvidenceError("invalid_evidence_json") from exc
    if not isinstance(result, dict):
        raise M1EvidenceError("invalid_evidence_schema")
    return result


def _hash(path: Path) -> str:
    return sha256(_read_file(path)).hexdigest()


def _expect_digest(actual: str, expected: object) -> None:
    if not isinstance(expected, str) or not HEX_SHA.fullmatch(expected):
        raise M1EvidenceError("invalid_declared_sha256")
    if actual != expected:
        raise M1EvidenceError("artifact_checksum_mismatch")


def inspect_bundle(root: Path, *, require_pdf: bool = False) -> dict:
    """Verify both installed distributions against their independent receipts."""
    if root.is_symlink() or not root.is_dir():
        raise M1EvidenceError("invalid_bundle_directory")
    evidence = _read_json(root / "release-evidence.json")
    version = evidence.get("development_version")
    if not isinstance(version, str) or not VERSION.fullmatch(version):
        raise M1EvidenceError("invalid_package_version")
    if (evidence.get("schema_version") != 1
            or evidence.get("status") != "clean_install_passed"
            or evidence.get("builds_byte_reproducible") is not True
            or evidence.get("installed_dependency_inventory_available") is not True
            or evidence.get("pdf_validated") is not require_pdf
            or evidence.get("tag_created") is not False
            or evidence.get("published") is not False
            or evidence.get("physical_verified") is not False
            or evidence.get("network_used_by_preview") is not False
            or evidence.get("legal_license_review_complete") is not False
            or evidence.get("native_dependency_review_complete") is not False
            or evidence.get("suggested_prerelease") != PROPOSED_TAG):
        raise M1EvidenceError("unsupported_or_unverified_release_evidence")
    wheels = list(root.glob("kushluk-*.whl"))
    sdists = list(root.glob("kushluk-*.tar.gz"))
    if len(wheels) != 1 or len(sdists) != 1:
        raise M1EvidenceError("missing_or_duplicate_distribution")
    wheel, sdist = wheels[0], sdists[0]
    if (wheel.name != f"kushluk-{version}-py3-none-any.whl"
            or sdist.name != f"kushluk-{version}.tar.gz"):
        raise M1EvidenceError("distribution_version_mismatch")
    _expect_digest(_hash(wheel), evidence.get("wheel_sha256"))
    _expect_digest(_hash(sdist), evidence.get("sdist_sha256"))
    installs = evidence.get("installs")
    if not isinstance(installs, dict) or set(installs) != {"wheel", "sdist"}:
        raise M1EvidenceError("missing_independent_install_proofs")

    fixed = PREVIEW | {"kushluk-preview.pdf"} if require_pdf else PREVIEW
    checked = {}
    for kind, archive in (("wheel", wheel), ("sdist", sdist)):
        item = installs[kind]
        if (not isinstance(item, dict)
                or item.get("installed_distribution") != archive.name
                or item.get("runtime_module_from_venv") is not True
                or item.get("synthetic_only") is not True
                or item.get("physical_verified") is not False
                or item.get("pdf_validated") is not require_pdf
                or item.get("license_signoff_complete") is not False
                or item.get("legal_license_review_complete") is not False):
            raise M1EvidenceError("untrusted_install_receipt")
        number = item.get("dependency_count")
        if type(number) is not int or number < 2 or number > 2000:
            raise M1EvidenceError("invalid_installed_dependency_count")
        install_dir = root / kind
        if install_dir.is_symlink() or not install_dir.is_dir():
            raise M1EvidenceError("unsafe_install_directory")
        if (item.get("dependency_inventory") != "installed-environment.json"
                or item.get("license_review_worksheet") != "license-review-worksheet.json"):
            raise M1EvidenceError("unexpected_install_evidence_name")
        for filename, key in (
            ("installed-environment.json", "dependency_inventory_sha256"),
            ("license-review-worksheet.json", "license_review_worksheet_sha256"),
        ):
            _expect_digest(_hash(install_dir / filename), item.get(key))
        inventory = _read_json(install_dir / "installed-environment.json")
        review = _read_json(install_dir / "license-review-worksheet.json")
        packages = inventory.get("installed_packages")
        if (inventory.get("schema_version") != 1
                or inventory.get("kind") != "installed-python-environment-inventory"
                or not isinstance(packages, list) or len(packages) != number
                or not any(isinstance(p, dict) and p.get("name") == "kushluk"
                           and p.get("version") == version for p in packages)
                or inventory.get("legal_license_review_complete") is not False
                or review.get("schema_version") != 1
                or review.get("kind") != "license-review-evidence-worksheet"
                or review.get("human_signoff_required") is not True
                or review.get("approved_for_release") is not False
                or review.get("python_inventory_sha256")
                != item.get("dependency_inventory_sha256")
                or review.get("review_counts", {}).get("python_pending") != number):
            raise M1EvidenceError("inventory_or_license_evidence_mismatch")
        manifest = _read_json(install_dir / "preview-manifest.json")
        declared = manifest.get("files")
        if (manifest.get("schema_version") != 1
                or manifest.get("fixture_date") != "2026-10-17"
                or manifest.get("fixture_generated_at") != "2026-10-17T07:00:00+02:00"
                or manifest.get("four_logical_a4_pages") is not True
                or manifest.get("pdf_validated") is not require_pdf
                or manifest.get("synthetic_only") is not True
                or manifest.get("physical_verified") is not False
                or any(manifest.get(k) != 0 for k in (
                    "network_requests", "printer_submissions", "mail_submissions"
                ))
                or not isinstance(declared, dict) or set(declared) != fixed):
            raise M1EvidenceError("unsafe_or_incomplete_synthetic_manifest")
        files = item.get("files")
        if not isinstance(files, dict) or files != declared:
            raise M1EvidenceError("manifest_install_receipt_mismatch")
        for filename, digest in declared.items():
            _expect_digest(_hash(install_dir / filename), digest)
        # These three deterministic files must match ACROSS the two installs.
        checked[kind] = {name: declared[name] for name in PREVIEW}
    if checked["wheel"] != checked["sdist"]:
        raise M1EvidenceError("installed_synthetic_fixture_drift")
    return {
        "schema_version": 1,
        "kind": "m1_engineering_bundle_preflight",
        "status": "software_evidence_ready_for_review",
        "installed_version": version,
        "proposed_release_tag": PROPOSED_TAG,
        "distribution_sha256": {
            "wheel": evidence["wheel_sha256"], "sdist": evidence["sdist_sha256"],
        },
        "verified_clean_install_evidence": ["wheel", "sdist"],
        "pdf_structural_proof_reported": require_pdf,
        "sample_network_print_email_submissions": 0,
        "legal_license_signoff_complete": False,
        "native_font_signoff_complete": False,
        "independent_first_reader_test_complete": False,
        "physical_print_and_host_verified": False,
        "release_authorized": False,
        "tag_created_by_preflight": False,
        "published_by_preflight": False,
        "review_gate": "owner_approval_and_rights_review_still_required",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--require-pdf", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = inspect_bundle(args.artifact_dir, require_pdf=args.require_pdf)
    except M1EvidenceError as exc:
        print(json.dumps({
            "status": "rejected", "code": str(exc),
            "tag_created_by_preflight": False, "release_authorized": False,
        }))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
