# Kuşluk alpha release — scoped source distribution approval

**Limited owner direction:** prepare and publish `v0.2.0-alpha.1` as a **GitHub-only, first-party-source prerelease** after exact-main green six-job CI and a fresh green public dependency advisory audit. Python version is `0.2.0a1`. This is NOT approval for PyPI publication, bundled native/font binaries, generated PDFs, publisher content, unattended/physical/reader gate claims or outside invitations. The [GitHub prerelease](https://github.com/interzettel/kushluk/releases/tag/v0.2.0-alpha.1) was independently verified **published on 18 October 2026**, with annotated tag at commit `d90f9a5ea0a65e7e9393675fd82cefb7e2d4159c`. The matching six-job main CI, live advisory audit and publication workflow passed. Later hardware/reader/native-rights gates remain unverified. Owner #54/#87.

## Engineering evidence to review

The current [M1 alpha evidence handoff](M1_ALPHA_CANDIDATE.md) records a green historical `main` SHA and the GitHub ZIP artifact hashes, and documents the new independent `m1_bundle_preflight` receipt. These CI records are a starting point for inspection, not an approval of actual legal terms or distribution. The final release SHA/version must be rebuilt and reviewed separately.

- [ ] Record the exact current `main` commit SHA and the full five-job green CI run on that SHA (Linux unit, clean installs Python 3.11/3.12, macOS Apple Silicon and Intel PDF).
- [ ] Retrieve and checksum the built wheel and sdist; verify both use installed entry points outside source checkout, contain notices and templates, produce matching deterministic synthetic HTML/Markdown/JSON, and generate four logical A4 PDF pages where native dependencies exist.
- [ ] Review the **live** public-PyPI dependency advisory audit for the resolved runtime including PDF and Google extras. A scanner network error is *not* a pass. Review unresolved package findings and their fixed versions; do not infer safety for native packages.
- [ ] Examine versioned native dependency and font **family** observations, then separately inspect actual font/native licences and binary redistribution terms. Metadata and font name lists do not satisfy this human/legal step.
- [ ] Check safe failure modes (missing Pango, source failure, invalid metadata/XML, printer queue unavailability, SMTP ambiguity, repeated run and explicit archive resend). No automatic retries on uncertain submissions.
- [ ] Confirm archive-v1 remains held for migration review, with no automatic conversion/resend; document backups and restoration from a private copy. See [migration playbook](ARCHIVE_MIGRATION_PLAYBOOK.md).
- [ ] Compare actual supported CI platforms against [compatibility matrix](COMPATIBILITY_MATRIX.md); Windows and physical printer behavior remain **not verified**.
- [ ] Approve final security, rights, data collection/privacy, contributor/legal notices and `CHANGELOG.md`. A synthetic edition does not authorize use of publisher body text or unlicensed images.
- [x] **Limited owner direction:** conditionally release version `0.2.0a1` with annotated tag `v0.2.0-alpha.1`, a first-party source wheel/sdist and SHA256SUMS through GitHub only. No blanket native/rights approval.
- [x] Verify the source-only GitHub prerelease, annotated tag, three downloadable assets, checksums, exact-main CI, fresh advisory audit and successful publication workflow. **No PyPI or native/physical/reader approvals.**

## Isolated alpha-version packaging trial (not publication)

The CI `Isolated 0.2.0a1 candidate version` job builds a temporary
tracked Git snapshot with Python version `0.2.0a1`, clean-installs wheel
and sdist, and rechecks M1 bundle hashes and synthetic preview invariants.
It **does not** edit the development checkout, and never tags or publishes
to GitHub Releases or PyPI. A final authorized version bump, exact release
SHA, human licensing signoff, legal copy and changelog review remain required.

## Scope boundaries for alpha versus later trials

The **alpha** may be evaluated as an offline synthetic developer preview with stated limitations, once the above release authorization is complete. **M2a** private printer trials need a physical A4 page and safe queue/recovery observation. **M2b stable** requires five real unattended mornings, independent reader/device proof and release gate review. None can be awarded by synthetic CI, self-reported receipts, QA docs or a proposed percentage.

For the actual operator tests, use [print and field acceptance](FIELD_ACCEPTANCE.md) and [host trial review](HOST_TRIAL_REVIEW.md). No raw reader receipts should leave the host.
