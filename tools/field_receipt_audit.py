"""Read-only local audit of operator field-proof receipts.

This summarizes *claims*, not proof. It never upgrades hardware/release gates.
No photographs, operator names, device descriptions or observations are emitted.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
import json
from pathlib import Path
import re

MAX_RECEIPTS = 100
MAX_BYTES = 128 * 1024
KINDS = frozenset(("paper-a4", "paper-a3", "epub-reader", "host-resume"))
RESULTS = frozenset(("pass", "fail", "blocked"))
SHA = re.compile(r"[0-9a-f]{64}\Z")


class ReceiptAuditError(ValueError):
    """Operator-safe validation failure."""


def audit_receipts(directory: Path) -> dict:
    """Validate bounded receipts without trusting self-reported acceptance flags."""
    if directory.is_symlink() or not directory.is_dir():
        raise ReceiptAuditError("Receipt directory must be a real local directory")
    paths = sorted(directory.iterdir())
    if len(paths) > MAX_RECEIPTS:
        raise ReceiptAuditError("Receipt directory exceeds 100 entries")
    counts = Counter()
    invalid = 0
    host_dates: set[str] = set()
    for path in paths:
        if path.is_symlink() or not path.is_file() or path.suffix != ".json":
            invalid += 1
            continue
        try:
            if not 0 < path.stat().st_size <= MAX_BYTES:
                raise ValueError()
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict) or data.get("schema_version") != 1:
                raise ValueError()
            kind, result = data.get("kind"), data.get("operator_reported_result")
            artifact = data.get("artifact")
            if kind not in KINDS or result not in RESULTS:
                raise ValueError()
            if not isinstance(artifact, dict) or not isinstance(artifact.get("sha256"), str) or not SHA.fullmatch(artifact["sha256"]):
                raise ValueError()
            if not isinstance(artifact.get("bytes"), int) or isinstance(artifact["bytes"], bool) or artifact["bytes"] <= 0:
                raise ValueError()
            if data.get("independently_verified") is not False or data.get("release_gate_accepted") is not False:
                # Reject forged/previously modified status rather than treating it as proof.
                raise ValueError()
            if data.get("attestation") != "operator-self-report; not independently validated":
                raise ValueError()
            if result == "pass" and (not data.get("acknowledged_direct_observation") or not data.get("evidence_files")):
                raise ValueError()
            if kind.startswith("paper-") and result == "pass" and not isinstance(data.get("print_inspection_sha256"), str):
                raise ValueError()
            observed = data.get("observed_at_utc")
            if not isinstance(observed, str):
                raise ValueError()
            day = date.fromisoformat(observed[:10]).isoformat()
            counts[(kind, result)] += 1
            if kind == "host-resume" and result == "pass":
                host_dates.add(day)
        except (OSError, UnicodeError, ValueError, TypeError, KeyError, json.JSONDecodeError):
            invalid += 1
    return {
        "schema_version": 1,
        "receipts_scanned": len(paths),
        "invalid_or_unsupported_entries": invalid,
        "operator_reports": {
            kind: {result: counts[(kind, result)] for result in sorted(RESULTS)}
            for kind in sorted(KINDS)
        },
        "host_reported_pass_utc_dates": len(host_dates),
        "host_five_distinct_utc_dates_reported": len(host_dates) >= 5,
        "independently_verified": False,
        "release_gate_accepted": False,
        "note": "Counts are unverified operator self-reports. Distinct UTC dates do not prove five unattended local mornings. Independently review originals, devices and run logs.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipts-dir", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        result = audit_receipts(args.receipts_dir)
    except ReceiptAuditError as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
