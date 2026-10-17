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

**No prerelease has been published.** `pyproject.toml` remains `0.1.0`;
the future version `v0.2.0-alpha.1` requires an explicit owner decision,
review of dependencies/licenses and controlled tag/release creation.

## Development baseline — 0.1.0 (not a published stable release)

The four-page software pipeline, proofing, archive/delivery safeguards,
source adapters and editor are under active work in `main`. Their acceptance
is tracked separately from installability. The eight physical/product delivery
evidence gates remain unverified until supported real-world tests occur.
