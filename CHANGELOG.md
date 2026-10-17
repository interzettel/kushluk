# Changelog

This repository is still in **unreleased development**. Changelog entries are
engineering notes, not proof of a published package, signed download, or
physical-product acceptance. A future release must be approved and tagged
separately under [the release plan](docs/RELEASE_PLAN.md).

## Unreleased — M1 installable-preview candidate (proposed v0.2.0-alpha.1)

- Add an installed `kushluk preview --output-dir DIR [--pdf]` command: frozen
  original fictional editorial content, four logical A4 pages, HTML, Markdown,
  schema-v2 edition JSON, SHA-256 manifest and optional validated PDF.
- Correct distribution package inclusion so the wheel and source archive both
  carry runtime modules, the print HTML template and required legal/readme files.
- Reproducibly build wheel/sdist twice, compare archive digests, then install
  **each** archive into its own empty virtual environment outside the checkout.
- Check installed CLI, template resources, edition metadata and four-page PDF
  rendering on supported Linux and macOS CI hosts; retain review artifacts.
- Add a developer-oriented [preview installation guide](docs/PREVIEW_INSTALL.md)
  with explicit known limits, offline sample instructions and a separate
  release approval checkpoint.
- Record environment-level installed Python dependencies and declared license
  metadata with hashes in each clean wheel/sdist preview proof. `pip check`
  detects inconsistent Python requirements, not vulnerable/native packages.
- Add read-only `kushluk archive-check` with bounded schema-v2 reference checks
  and explicit legacy-v1/future migration hold, never implicit archival edits.

- Add private field-proof receipt review and consecutive local host-date cross-checks; no automated acceptance of operator self-reports or printer behavior.
- Require the WeasyPrint 70.x security line (excluding vulnerable 69.0), and add weekly/manual live Python advisory scans plus macOS native text-library/font-family inventory for reviewer evidence; no claim of completed legal/font audits.
- Fail closed on symlinked, missing, empty or oversized archived inputs before manual PDF/email recovery.
- Improve local setup keyboard skip navigation and screen-reader descriptions, and add content-free recovery guidance in run reports (not an automatic notification service).
- Document a conservative legacy archive migration hold, platform/device compatibility matrix and explicit human alpha release approval checklist.

- Add user-selectable DIN A4 or US Letter home paper preference in first-run CLI/browser setup with legacy A4 compatibility, plus an independently validated Letter PDF variant, driverless CUPS Letter preflight and explicit archived Letter recovery (#129). A3 remains optional, and no physical device proof is claimed.

- Add versioned, read-only `incident-report` diagnostics for local agents (#20): fixed action identifiers, explicit severity, allowlisted failure codes, create-only private export, and no implicit remote transmission or automatic retries. Native notifications and physical proof remain open.

- Add opt-in native desktop failure notifications (`notify-local --send` / `run --notify-local`) with fixed privacy-safe messages and crash-safe once-per-incident submission claims. No push service or verified display/read receipt; local-only (#17/#20).

- Add an accessible, read-only `/status` page to the existing loopback setup browser, with today's archive and queue-submission states, fixed safe operator guidance and no active delivery effects (#5/#20).

- Record operator-observed US Letter physical samples through `record-field-proof --kind paper-letter`, with mandatory matching `letter-home` PDF inspection; self-report never advances release gates (#129).

- Generate a pending-review licence evidence worksheet for each isolated wheel/sdist install, with hashed Python inventory and unresolved native-library/font-rights rows. Metadata does not grant legal approval (#54/#57).

- Extend the independent U1–U6 reader handoff and synthetic regression for Letter selection and read-only `/status`; add private keyboard/screen-reader A1–A5 observation template and local completeness preflight without awarding a human or device pass (#5).

- Independently audit M1 installer evidence before CI upload: compare wheel/sdist hashes, installed package/rights-pending receipts and deterministic fictional preview output, with a permanently unapproved release state; add a dated alpha evidence handoff (#54/#87).

- Fix macOS clean-install evidence using real path containment instead of raw prefix comparison (which could misclassify `/var` versus `/private/var` venv paths), and reject any installed runtime that actually resides outside its venv (#54).

- Exercise exact proposed PEP 440 `0.2.0a1` wheel/sdist metadata in an
  isolated Git-tracked source snapshot with two clean installs and M1 bundle
  preflight. The checkout remains `0.1.0`, and no release/tag is made (#87).

**No prerelease has been published.** `pyproject.toml` remains `0.1.0`;
the future version `v0.2.0-alpha.1` requires an explicit owner decision,
review of dependencies/licenses and controlled tag/release creation.

## Development baseline — 0.1.0 (not a published stable release)

The four-page software pipeline, proofing, archive/delivery safeguards,
source adapters and editor are under active work in `main`. Their acceptance
is tracked separately from installability. The eight physical/product delivery
evidence gates remain unverified until supported real-world tests occur.
