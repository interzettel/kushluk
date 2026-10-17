# M1 dependency inventory and third-party review — #54

**Status:** inventory automation, **not** completed legal/security approval. This is a developer engineering aid for the proposed, unpublished `v0.2.0-alpha.1`. The development package remains `0.1.0`.

## Evidence written by clean-install CI

[CI](https://github.com/interzettel/kushluk/actions/workflows/ci.yml) builds the wheel and source distribution twice and installs **each** in its own empty virtual environment outside the source checkout. During both installs, `tools/release_check.py` now:

1. Uses `python -m pip check` to check declared Python dependency compatibility.
2. Executes `tools/release_inventory.py` using the **isolated installed venv's Python**, not the repository Python.
3. Writes `wheel/installed-environment.json` and `sdist/installed-environment.json` alongside the synthetic fixture and `release-evidence.json`.
4. Records the inventory's SHA-256 digest and actual installed package count in each `installs` entry in release evidence.

The inventory captures normalized installed Python distribution **name**, resolved **version**, declared `License-Expression` when available, and whether a license classifier/legacy field exists. It excludes private source paths, metadata locations, installation URLs, account credentials, raw license texts and complete distribution metadata. Pip/setuptools/wheel, when installed, are explicitly labeled as tooling but are still included in the environment snapshot.

This is an **installed-environment inventory**, not a formally generated SPDX/CycloneDX SBOM, vendored-code audit, trademark clearance, dependency lockfile, reproducible end-to-end supply-chain attestation, or proof of production vulnerability absence. A package claiming MIT or BSD metadata has **not** been independently license-reviewed merely because the field exists.

## What remains before publishing anything

- Inspect each transitive Python distribution's actual license and retained notices; verify bundled code/assets/fonts and any incompatible terms.
- Audit native WeasyPrint/Pango/Fontconfig/Harfbuzz/cairo and OS/brew dependencies on both macOS architectures and the selected Linux baseline.
- Run a separately approved, timestamped vulnerability check with current advisories. Offline metadata alone does not detect CVEs.
- Pin/review reproducible release dependency versions or a platform-specific constraints policy. Wheel/sdist byte reproducibility within a runner does **not** guarantee identical dependencies next month.
- Decide whether publishing warrants a standard SPDX/CycloneDX SBOM and automated provenance attestations, then version those outputs rather than mislabeling this provisional JSON.
- Obtain a human release decision before any `v0.2.0-alpha.1` version bump/tag/signature or GitHub Release.

The root [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md) distinguishes dependencies installed from PyPI from code/assets copied into the project. [SECURITY.md](../SECURITY.md) explains how to report private findings. Candidate artifacts live in CI for 14 days and must never include reader archives, email headers or API tokens.
