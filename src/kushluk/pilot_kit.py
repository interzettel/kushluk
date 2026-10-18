"""Create a PRIVATE, blank human field-test kit; never run the field test.

No feeds, printer, mail, scheduler or network access. The outputs are
templates only, never observations, release approval or user evidence.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import re

COMMIT = re.compile(r"[0-9a-f]{40}\\Z")
UNKNOWN_SHA = "REPLACE_WITH_TESTED_MAIN_COMMIT"
SAFETY_CHECKS = (
    "private_data_remains_on_owner_device",
    "sources_have_explicit_approved_rights_or_synthetic_only",
    "operator_has_permission_to_use_printer",
    "participant_consented_to_observation",
    "host_schedule_and_retry_policy_reviewed",
    "failure_and_rollback_instructions_understood",
)
READER_QUESTIONS = (
    "external_data_expectation", "rss_approval_meaning",
    "print_or_schedule_expectation", "hardest_step", "repeat_setup_intent",
)
ACCESS_QUESTIONS = (
    "focus_navigation", "form_labels", "source_consent",
    "status_meaning", "zoom_or_contrast",
)


class PilotKitError(ValueError):
    """Return safe fixed errors only, no private paths or free text."""


def _first_reader(commit: str) -> dict:
    return {
        "schema_version": 1, "status": "template-not-observation",
        "source_commit": commit, "observer_code": "REPLACE",
        "participant_code": "ANONYMOUS_CODE", "local_date": "YYYY-MM-DD",
        "os_and_version": "REPLACE",
        "device_context": "OWN_OR_BORROWED_COMPUTER",
        "consent_to_observation": False,
        "consent_to_share_redacted_notes": False,
        "tasks": {f"U{i}": {
            "result": "not_attempted", "elapsed_seconds": None,
            "hints": 0, "observed_issue": "", "evidence_reference": "",
        } for i in range(1, 7)},
        "comprehension": {key: "" for key in READER_QUESTIONS},
        "reviewer_signoff": "not_reviewed",
        "independently_verified": False, "release_gate_accepted": False,
    }


def _accessibility(commit: str) -> dict:
    return {
        "schema_version": 1, "status": "template-not-observation",
        "source_commit": commit, "participant_code": "ANONYMOUS_CODE",
        "observer_code": "REPLACE", "local_date": "YYYY-MM-DD",
        "os_and_screen_reader": "REPLACE",
        "consent_to_observation": False,
        "consent_to_share_redacted_notes": False,
        "tasks": {f"A{i}": {
            "result": "not_attempted", "elapsed_seconds": None,
            "hints": 0, "observed_issue": "",
        } for i in range(1, 6)},
        "comprehension": {key: "" for key in ACCESS_QUESTIONS},
        "independently_verified": False,
        "reviewer_signoff": "not_reviewed", "release_gate_accepted": False,
    }


def _safety() -> dict:
    return {
        "schema_version": 1, "status": "template-not-observation",
        "checks": {name: False for name in SAFETY_CHECKS},
        "human_rights_review_completed": False,
        "independently_verified": False, "release_gate_accepted": False,
    }


INSTRUCTIONS = """# Kuşluk — PRIVATE M2a beta operator handoff

This directory is blank, fictional test paperwork, NOT a real observed trial.
It may contain personal observations after you fill it: do not commit, publish,
email or upload it. Keep all files and photographs on the operator's computer.

1. Record the exact software SHA tested. If this kit was made without
   `--source-commit`, replace REPLACE_WITH_TESTED_MAIN_COMMIT with the real
   tested repository SHA in first-reader.json and accessibility.json.
   A SHA label is not proof that the observed installation used that code.
2. Produce a synthetic four-page A4 test PDF with
   `kushluk print-proof --output-dir /PRIVATE/proof`.
   Inspect it structurally with
   `kushluk inspect-print --profile a4-home --pdf /PRIVATE/proof/kushluk-proof-a4.pdf --output-dir /PRIVATE/inspection --rasterize`.
   Only with the operator's permission, physically print and inspect the pages,
   then save a LOCAL photograph and an operator-reported receipt:
   `kushluk record-field-proof --kind paper-a4 --artifact /PRIVATE/proof/kushluk-proof-a4.pdf --inspection /PRIVATE/inspection/inspection.json --evidence /PRIVATE/photo.jpg --device "observed model" --operator "initials" --observations "actual observations" --result pass --acknowledge-direct-observation --output /PRIVATE/receipts/a4.json`.
   Never report pass unless real paper was actually seen.
3. On the operator's actual host, examine reboot/wake and scheduler logs,
   retry safety, duplicate job risk and one actual archived scheduled run.
   Save a REAL host-resume evidence receipt using record-field-proof.
   See docs/HOST_TRIAL_REVIEW.md in a repository checkout.
4. Have an independent, consenting novice perform U1–U6 using fictional
   feeds. Complete first-reader.json with ALL actual outcomes, measured
   durations, hints, comprehension and consent. A hinted task is assisted.
   The separate optional A1–A5 screen-reader trial uses accessibility.json.
   Do not silently preconfigure the participant's computer.
5. Review six operator permissions and safeguards in safety.json. After
   genuine checks, change its status to operator-checklist; never change
   independently_verified or release_gate_accepted to true yourself.
6. From a matching repo checkout, run the read-only private beta preflight:
   `python -m tools.beta_pilot_preflight --a4-receipt /PRIVATE/receipts/a4.json --pdf /PRIVATE/proof/kushluk-proof-a4.pdf --inspection /PRIVATE/inspection/inspection.json --paper-evidence /PRIVATE/photo.jpg --archive-root /PRIVATE/archive --host-receipts /PRIVATE/receipts --host-start-date YYYY-MM-DD --reader-record first-reader.json --safety-checklist safety.json`.
   Tool paths shipped under tools/ are available in a SOURCE CHECKOUT,
   not via the published Python wheel.

Even a complete operator packet means ONLY ready for outside human review.
No actual hardware, printer, waking host, participant, publisher rights or
release gate is certified. The beta is not tagged/published; 0/8 gate proof.
The stable release separately requires five genuine unattended mornings.

Full instructions: docs/BETA_PRIVATE_PILOT.md, docs/FIELD_ACCEPTANCE.md,
docs/FIRST_READER_PILOT.md and docs/ACCESSIBILITY_PILOT.md in GitHub.
"""


def _create_file(path: Path, content: bytes) -> None:
    fd = os.open(
        path,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
        0o600,
    )
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def create_pilot_kit(directory: Path, *, source_commit: str | None = None) -> dict:
    if source_commit is not None and not COMMIT.fullmatch(source_commit):
        raise PilotKitError("invalid_source_commit")
    if directory.is_symlink() or directory.exists() or directory.parent.is_symlink():
        raise PilotKitError("private_directory_must_be_new")
    # The operator chooses the local destination. Only the kit is created;
    # the program never writes real observations or accesses external devices.
    try:
        directory.mkdir(mode=0o700, parents=True, exist_ok=False)
        if directory.is_symlink() or directory.stat().st_mode & 0o077:
            raise PilotKitError("private_directory_permissions_invalid")
        source = source_commit if source_commit is not None else UNKNOWN_SHA
        templates = {
            "first-reader.json": _first_reader(source),
            "accessibility.json": _accessibility(source),
            "safety.json": _safety(),
        }
        blobs = {
            name: (json.dumps(obj, indent=2, sort_keys=True) + "\\n").encode("utf-8")
            for name, obj in templates.items()
        }
        blobs["SESSION.md"] = INSTRUCTIONS.encode("utf-8")
        for name, blob in blobs.items():
            _create_file(directory / name, blob)
        manifest = {
            "schema_version": 1, "kind": "m2a_private_blank_operator_kit",
            "status": "template_not_an_observation",
            "source_commit": source,
            "source_commit_verified_against_installation": False,
            "files_sha256": {
                name: sha256(blobs[name]).hexdigest() for name in sorted(blobs)
            },
            "no_network_or_device_access": True,
            "participant_tested": False,
            "paper_physically_tested": False,
            "host_resume_tested": False,
            "rights_independently_reviewed": False,
            "beta_publication_authorized": False,
            "release_gates_independently_verified": 0,
        }
        _create_file(
            directory / "MANIFEST.json",
            (json.dumps(manifest, indent=2, sort_keys=True) + "\\n").encode("utf-8"),
        )
        return {
            "status": "private_blank_pilot_kit_created",
            "files_created": len(blobs) + 1,
            "source_commit_verified": False,
            "physical_print_verified": False,
            "first_reader_verified": False,
            "beta_publication_authorized": False,
        }
    except PilotKitError:
        raise
    except OSError as exc:
        raise PilotKitError("private_kit_creation_failed") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--source-commit",
                        help="Exact 40-character tested source SHA; metadata only")
    args = parser.parse_args(argv)
    try:
        result = create_pilot_kit(args.output_dir, source_commit=args.source_commit)
    except PilotKitError as exc:
        print(json.dumps({"status": "rejected", "code": str(exc)}))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
