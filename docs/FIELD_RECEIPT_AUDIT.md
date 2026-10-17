# Review local field receipts (not release approval)

This developer-side read-only helper complements [FIELD_ACCEPTANCE.md](FIELD_ACCEPTANCE.md) and #13/#33/#47. It counts the existing `record-field-proof` JSON format without reading photographs or outputting operator/device/observations.

```bash
python -m tools.field_receipt_audit --receipts-dir ~/kushluk-private-evidence
```

The directory is bounded to 100 entries, individual JSON files to 128 KiB, and symbolic links or malformed receipts are rejected from the counts. Do not put real receipts or private output in the repository. Output is JSON with per-kind self-reported outcomes, invalid-entry count, and a *distinct UTC date count* of passing host-resume claims. It does **not** establish consecutive local mornings, timer execution, real prints, output validity, independent observation or acceptance of G1–G8. The `release_gate_accepted` and `independently_verified` fields in every output are always false.

Reviewers still need to inspect the original evidence off-repository, check local dates, printer/host identity, actual logs and intervention history, and record a separate human decision in the existing owning issues. Never publish private receipts to CI artifacts.
