# Proposed alpha release: human approval handoff

**Release candidate, not an issued release:** `v0.2.0-alpha.1` (proposed). Development package is `0.1.0` until separately approved. **No tag, PyPI upload, GitHub Release or external invitation is authorized by this checklist.** Owner #54/#87.

## Engineering evidence to review

- [ ] Record the exact current `main` commit SHA and the full five-job green CI run on that SHA (Linux unit, clean installs Python 3.11/3.12, macOS Apple Silicon and Intel PDF).
- [ ] Retrieve and checksum the built wheel and sdist; verify both use installed entry points outside source checkout, contain notices and templates, produce matching deterministic synthetic HTML/Markdown/JSON, and generate four logical A4 PDF pages where native dependencies exist.
- [ ] Review the **live** public-PyPI dependency advisory audit for the resolved runtime including PDF and Google extras. A scanner network error is *not* a pass. Review unresolved package findings and their fixed versions; do not infer safety for native packages.
- [ ] Examine versioned native dependency and font **family** observations, then separately inspect actual font/native licences and binary redistribution terms. Metadata and font name lists do not satisfy this human/legal step.
- [ ] Check safe failure modes (missing Pango, source failure, invalid metadata/XML, printer queue unavailability, SMTP ambiguity, repeated run and explicit archive resend). No automatic retries on uncertain submissions.
- [ ] Confirm archive-v1 remains held for migration review, with no automatic conversion/resend; document backups and restoration from a private copy. See [migration playbook](ARCHIVE_MIGRATION_PLAYBOOK.md).
- [ ] Compare actual supported CI platforms against [compatibility matrix](COMPATIBILITY_MATRIX.md); Windows and physical printer behavior remain **not verified**.
- [ ] Approve final security, rights, data collection/privacy, contributor/legal notices and `CHANGELOG.md`. A synthetic edition does not authorize use of publisher body text or unlicensed images.
- [ ] **Founder release decision** authorizes the exact alpha version bump, Git tag `v0.2.0-alpha.1`, release assets, checksums and distribution channel. A merge or green badge **does not** constitute that decision.
- [ ] After explicit authorization only: update package version, build from the approved SHA, re-run clean installs and checks, create annotated tag and GitHub prerelease intentionally, and document SHA/recovery/upgrade contract. Do not publish to PyPI merely because GitHub artifacts exist.

## Scope boundaries for alpha versus later trials

The **alpha** may be evaluated as an offline synthetic developer preview with stated limitations, once the above release authorization is complete. **M2a** private printer trials need a physical A4 page and safe queue/recovery observation. **M2b stable** requires five real unattended mornings, independent reader/device proof and release gate review. None can be awarded by synthetic CI, self-reported receipts, QA docs or a proposed percentage.

For the actual operator tests, use [print and field acceptance](FIELD_ACCEPTANCE.md) and [host trial review](HOST_TRIAL_REVIEW.md). No raw reader receipts should leave the host.
