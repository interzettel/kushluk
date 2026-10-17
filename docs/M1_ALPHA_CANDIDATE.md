# M1 alpha — artifact acceptance and release decision

**Proposed distribution:** `v0.2.0-alpha.1`, not released. The checked-in
package stays at development version `0.1.0`; its current CI ZIP artifacts
contain **0.1.0** wheel/sdist files. **Do not rename the development files or
tag this SHA as an alpha:** Python's prerelease version would be `0.2.0a1`
and must be rebuilt/tested under a separately approved release version.

## Exact established software evidence, 17 October 2026

The earlier green `main` SHA was
`bca67eff72452fc655b9ef48516f1cec9e7d5e44` and its
[full five-job CI run](https://github.com/interzettel/kushluk/actions/runs/39061118029)
and [project-health run](https://github.com/interzettel/kushluk/actions/runs/39061118079)
passed. GitHub uploaded four installable-candidate ZIPs on that CI run:

| CI platform | GitHub artifact ID | Outer artifact ZIP SHA-256 (reported by GitHub) |
| --- | --- | --- |
| Linux / Python 3.11 | 12111103669 | `41cb3fd9665c9ed44123a0a17de6b8b876aab576cb96be107244eb850af0eb1f` |
| Linux / Python 3.12 | 12111616446 | `1ac0b98e618c041854864bca7a1ca88c01c722cd5b94c8190b979cb1dbf2234c` |
| macOS 15 / Apple Silicon | 12110664354 | `85971a1bdb74853ffaff5a0e76c901c59bb2fa5bddbc360a00a5c1ce5eb786bb` |
| macOS 15 / Intel | 12111446646 | `8445cee8488d583913f890981edebba65d79e42389619797b4465e3c1c6d0ee7` |

**Audit correction:** an inspection of the prior Apple Silicon artifact from
that run found `runtime_module_from_venv=false` in its wheel/sdist
release receipts, even though the old checker reported a clean install. The
old checker had used a raw string prefix test for macOS temporary paths
(`/var` versus `/private/var`). That is an **evidence-validation defect**:
the former green CI alone does *not* establish correctly attributed macOS
virtualenv isolation. The corrected checker resolves actual paths and fails
closed if the installed module is not under the real isolated venv. A **new
green CI run on that corrected checker** supersedes the affected observation.
Do not retrospectively rewrite the historical evidence.

These are **outer GitHub Actions artifact checksums**, not wheel or sdist
checksums. The wheel and sdist hashes are separately recorded in each
`release-evidence.json`. The artifact ZIPs are **temporary**, typically
expiring 14 days after creation, so download/review only while available.
This snapshot is not a claim that the author downloaded or inspected
each ZIP's contents by hand. Real hardware, readers and licence signoff
remain unverified; [the release checklist](RELEASE_APPROVAL.md) is authoritative.

## Additional automatic independent evidence preflight

The build matrix now runs `tools.m1_bundle_preflight` **after**
`tools.release_check` and before it uploads candidate artifacts. It
independently cross-checks:

- Exactly one wheel and one source archive, with filenames matching
  `release-evidence.json` version metadata and their SHA-256 hashes.
- Separate wheel and sdist `installed-environment.json`/licence-review
  worksheet hashes, actual `kushluk` installed version, pending human
  rights review and observed installed package counts.
- Unchanged synthetic source manifest and hashes of the HTML, Markdown,
  edition JSON, and optional PDF; **wheel/sdist** must generate identical
  deterministic HTML/Markdown/JSON bytes.
- Absence of reported network requests, print/mail submissions,
  physical verification, legal approval, Git tag and publication.
- macOS output must have the PDF path validated by the upstream
  `release_check`; Linux's non-PDF smoke is not substituted for PDF proof.

You can independently inspect a **locally extracted** CI ZIP, without
submitting anything externally:

```bash
python -m tools.m1_bundle_preflight \
  --artifact-dir /PATH/TO/extracted-m1-candidate
# On a macOS job's PDF-enabled candidate:
python -m tools.m1_bundle_preflight \
  --artifact-dir /PATH/TO/extracted-m1-candidate --require-pdf
```

The CI result is included as `m1-preflight.json` in the new CI artifacts.
Even a green report explicitly says
`release_authorized=false`, `tag_created_by_preflight=false` and
`published_by_preflight=false`; it is a **machine checked handoff**, not
a founder signature, provenance attestation or real-printer inspection.
The checker does not download files, read environment credentials, phone
home or alter existing releases.

## Isolated PEP 440 alpha-version build trial

A separate **unreleased** CI job now tests the proposed Python version
`0.2.0a1` without modifying the checked-in `0.1.0`. Run:

```bash
python -m tools.alpha_build_trial --artifact-dir output/m1-alpha-version-trial
```

The tool uses `git archive HEAD` to stage only tracked files in a
throwaway directory, changes exactly the package version there, and
builds/reinstalls both artifacts from scratch. It then runs the independent
M1 evidence preflight, requiring the installed version `0.2.0a1`.
GitHub's `kushluk-m1-isolated-0.2.0a1-trial` is a **temporary developer
testing artifact** only. Its `alpha-version-trial.json` retains the exact
source SHA and explicitly records that the checkout version was unchanged,
legal rights remain unapproved, and no tag/release was published.

**Observed pre-merge dry run:** on an earlier PR branch, the Linux Python
3.12 trial produced actual `kushluk-0.2.0a1-py3-none-any.whl` and
`kushluk-0.2.0a1.tar.gz` and reported two clean installs. The final
post-merge `main` SHA must independently pass this same job before an
official release decision. Staged docs still contain development-version
prose; these trial distributions are **not** approved public release assets.

## Decision still required

Before creating an alpha tag or uploading to a GitHub Release:

1. Obtain/retain the green full-CI evidence for the **final** exact candidate
   commit; recheck its private-data safe sample, wheel/sdist contents, optional
   native dependency evidence and live vulnerability audit.
2. Resolve the **actual** Python transitive/native/font redistribution and
   embedding licence obligations. The per-install pending worksheet and
   font-family matches are not legal permission.
3. Approve exact release scope, platform caveats, README, changelog, security
   notices, synthetic-only nature, alpha distribution channel and final
   `0.2.0a1` package version.
4. Only then perform the isolated alpha version bump, rebuild it reproducibly,
   confirm its version in clean-installed wheel and sdist, review checksums,
   authorize an annotated Git tag and optional GitHub prerelease assets.
   **Do not publish to PyPI implicitly.**

Physical A4/Letter/A3, unattended host reliability and independent reader
and accessibility acceptance are later pilot/stable gates, not evidence the
offline *developer preview* has been released. Continue to carry their
unverified status forward. See [release approval](RELEASE_APPROVAL.md),
[compatibility matrix](COMPATIBILITY_MATRIX.md), and
[real-device protocol](FIELD_ACCEPTANCE.md).
