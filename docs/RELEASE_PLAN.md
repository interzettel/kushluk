# Versioned release and outreach plan

**Proposal ready for founder/Claude review — 17 October 2026** · [planning issue #87](https://github.com/interzettel/kushluk/issues/87). No calendar date is claimed for device proof or formal public launches. [Feature registry](FEATURE_CATALOG.md) defines stable IDs. [ROADMAP.md](ROADMAP.md) stays the strategy/stage view; [WORK_LEDGER.md](WORK_LEDGER.md) remains task authority; [PROGRESS.md](PROGRESS.md) and G1–G8 remain separate acceptance-evidence authorities.

## Current version ≠ official release

`pyproject.toml` declares **0.2.0a1**, published on **18 October 2026** as the narrowly scoped, experimental **[v0.2.0-alpha.1 GitHub source prerelease](https://github.com/interzettel/kushluk/releases/tag/v0.2.0-alpha.1)**. This is the first actual GitHub prerelease but is **not a stable launch, PyPI distribution, native executable, or evidence of physical-device or first-reader acceptance**.

**Version grammar:** normal [Semantic Versioning](https://semver.org): `MAJOR.MINOR.PATCH[-prerelease]`. `1.4.2` is valid; **`v1.04.002` is NOT valid SemVer** due to leading zeros, so zero-padded `01.04.002` is permitted only as a progress-board *display string*, never a Python package or Git tag. V1 does **not** include all speculative features at once. Within v1: new backward-compatible features → minor (1.1.0), bug fixes/security patches → patch (1.0.1), backwards-incompatible published contracts → major (2.0.0) or formally gated deprecation. For pre-1.0, internal APIs may change but archived edition schemas must remain explicitly migrated/readable.

**Hotfix policy:** each bug has user impact / reproducible failure / regression test / affected feature IDs / version target; urgent print duplicate / privacy breach / fabricated article / wrong person mail is release-blocking, not a "minor UI bug". Branch from supported tagged release for patches, test macOS+Linux, publish changelog, record CVE/security advisory only if actually applicable; do not silently regenerate the user's already printed edition after an update.

## Milestones — what the product actually gains

| Milestone | Target train | Included features | Measurable exit gate | Status |
| --- | --- | --- | --- | --- |
| **M0 · Press-line prototype** | Development 0.1.0 (not official release) | F-001..005 | Four logical A4 PDF pages, A4/A3 software profiles, crash-safe archive and dry-run evidence on Linux/Intel/ARM; **not** real-device completion | **Software slices implemented; G1/G2/G3 remain unverified as tracked** |
| **M1 · First GitHub preview** | **v0.2.0-alpha.1** — proposed first official *prerelease* | F-001..006 | Source OPML preview is offline and requires explicit approval; reproducible build/package install; synthetic sample edition, readable README/config/SECURITY; CI green; exact release artifact and tag. No automatic home-print reliability advertised | **Published 18 Oct 2026 — GitHub source-only experimental prerelease, tag `d90f9a5`; exact-main six-job CI and live dependency audit green. No native/font or real-device rights signoff.** |
| **M2a · First invited private pilot** | **v0.3.0-beta.1** | F-007..014, plus the M1 feature set | At least one supported physical A4 printer verified, tested run/failure/reboot and a reader able to set up; source rights and secrets check. A3 enabled only if actually verified on hardware | **Blocked by human + real host/printer proof** |
| **M2b · First stable public release** | **v1.0.0** | F-001..014 (scope narrowed to features that satisfy acceptance; any optional A3/SMTP unavailable in a profile is identified rather than falsely promised) | **Five real unattended mornings**, duplicate-delivery and fallback trials, genuine printer/provenance evidence, repeatable first-run installation, supported printer/platform matrix, privacy/security docs, packaging+changelog+tag. Passing unit tests alone not enough | **Not yet** |
| **M3 · Reader formats** | **v1.1.0** | F-015..017 | Same canonical edition exports validated reflowable EPUB, tested on actual target reader; OPDS private/optional and only shipped if authenticated and tested | Proposed post-v1 |
| **M4 · User-controlled source intelligence** | **v1.2.0** | F-018..021 | Approved newsletter discovery, source-right modes, optional research/social adapters with rate limits and provenance, reproducible local feedback | Proposed post-v1 |
| **M5 · Editorial studio** | **v1.3.0** | F-022..025 | Real page/asset QA, readable modes, deterministic archetypes and bounded repair; no mandatory inference subscription | Proposed post-v1 |
| **M6 · Extra reading surfaces** | **v1.4.0** | F-027..029 | Accessible fluid web/audio/travel examples independently verified, optional and privacy-safe | Candidate post-v1 |
| **MX · Noncommitted investigations** | **No release assigned** | F-026, F-030..032 | Research-only issues and explicit adopt/reject; no schedule promises | Not a launch dependency |

**First actual release:** `v0.2.0-alpha.1` when M1 checks are met. **First stable release:** `v1.0.0` only after M2b physical/personal-rights/first-reader proofs. No invented deadline. `1.0.1` would be the first patch *after* `1.0.0`, not a feature bucket. The M1/M2 version mapping is a release-planning proposal pending founder review, **not an accepted ADR or released tag**.

## What is an epic or milestone in this system?

We practice **continuous flow with evidence gates**, *not fixed-time Scrum*. Using the word **epic** is fine: it is a useful umbrella around several features, not a Scrum ceremony. A **feature** is an expected user-visible capability; **milestone** is a verified combination that matters to a user; **work package** is a GitHub issue; **task** is a stable work-ledger ID or bounded PR; **proof** is a test, artifact, hardware trial or recorded review. GitHub Project statuses stay Backlog, Ready, In progress, In review and Done. Work is pulled by priority/dependencies, not pre-allocated into sprints; review can be async; WIP ideally one principal engineering slice at a time. We do not score velocity, story points or fictional capacity. The coordinator must not equate a merged PR or planning document with a released feature. No second parallel kanban/project board is created.

## External-contact and outside-tester gates

| Gate | Earliest trigger | Whom/contact method | May we do it now? | Evidence + safeguards |
| --- | --- | --- | --- | --- |
| **C0 · Targeted upstream clarification** | A concrete reuse question from #84/#88 with URL/revision and specific technical/legal ambiguity | Public upstream issue/discussion with permission, or private polite technical question | **Draft allowed now; no outreach without founder authorization** | Need a real question, own experiment, honor maintainers' time; no entitlement to response; no private reader content |
| **C1 · Limited developer feedback** | **M1 prerelease passed** and sample uses only synthetic/rights-cleared data | 3–5 opt-in technical readers/contributors to install and inspect sample | **Not yet** | Honest prototype label, security/privacy basics and reproducible offline install; solicit consent and link reproducible issue template |
| **C2 · Invited real-life pilots** | **M2a:** first physical home-print/device validation and safe cancellation/replay | A few volunteers comfortable with their own authorized feeds/printer | **Not yet** | Explicit consent, no centralized copy of their newsletters, no promised uptime, incident guidance, bounded telemetry off by default |
| **C3 · Public OSS release & announcements** | **M2b v1.0.0**, audited rights, reproducible 5 mornings & packaging | Community, journalists, library/print/OSS circles, partner projects | **Not yet** | Truthful launch wording backed by video/photos/CI; never call alpha features stable; permission for any quoted testimonial |
| **C4 · Commercial/publisher discussion** | Separate business/rights RFC #35/#38/#40/#41 and owner authorization | Publishers, printer companies, commercial partners | **Not on current critical path** | No implied redistribution rights, costs, hosting or license promises |

A GitHub repository is already publicly viewable; *outreach* here means proactive contact, recruitment, press, or marketing. Any inbound OSS issue may be handled before C1 without implying a launch. We **do not** contact Claude by implication: the same evidence is handed off in [#88](https://github.com/interzettel/kushluk/issues/88), and independent actual review comments are needed before recording agreement.

## M1 package candidate evidence versus an actual prerelease

The developer-oriented installation proof under [#54](https://github.com/interzettel/kushluk/issues/54) and [#87](https://github.com/interzettel/kushluk/issues/87) is implemented in [PR #120](https://github.com/interzettel/kushluk/pull/120): `kushluk preview` creates one frozen, entirely synthetic four-page edition; the wheel and sdist are built twice under a pinned epoch and **each** is clean-installed in a separate virtual environment. CI tests Linux Python 3.11 and 3.12 and macOS Apple Silicon/Intel with native PDF rendering. [Full local installation and limitation guide](PREVIEW_INSTALL.md) and [unreleased changelog](../CHANGELOG.md) record the contract.

Green CI is **software evidence**, not physical/reader approval. The separate GitHub-only source-alpha workflow may create `v0.2.0-alpha.1` only for the explicitly scoped first-party code after matching green CI and current public-PyPI advisory audit. No PyPI claims, bundled system fonts/native binaries or real device rights are approved. Package metadata is `0.2.0a1`. Binary wheels/source archives and synthetic samples are retained as temporary Actions artifacts, not a signed/public release. Release-checklist items requiring final legal/dependency review, human release approval and an actual release tag remain unchecked.

### M1 supplementary release-readiness diagnostics (not acceptance)

[PR #121](https://github.com/interzettel/kushluk/pull/121) adds machine-readable version/license **metadata** from each installed wheel and sdist environment, pip dependency-consistency tests, and a bounded v1/v2 archive structural compatibility report. These narrow the evidence gaps for the checklist below but **do not** finish the dependency-license/vulnerability audit, native font review, historical v1 migration, or founder release decision. [Dependency audit](DEPENDENCY_AUDIT.md) · [Archive contract](ARCHIVE_COMPATIBILITY.md). Neither a source distribution nor a compatibility inventory permits silent resale or reprinting of another person's material.

[Alpha release approval checklist](RELEASE_APPROVAL.md) · [supported CI/device matrix](COMPATIBILITY_MATRIX.md) · [v1 archive migration hold](ARCHIVE_MIGRATION_PLAYBOOK.md). These are review guides, not gate approvals.

## Release verification checklist

- [ ] `pyproject.toml` version and annotated tag correspond; no unreviewed version bump
- [ ] Clean install from built wheel and sdist on supported Linux/macOS Intel/Apple Silicon; CLI and sample PDF
- [ ] Offline tests including no-source, invalid XML, inaccessible printer, missing Pango, no network, SMTP failure; security/PII regression tests
- [ ] Schema migration/readability contract for older archive editions
- [ ] Audit license of actual bundled code, assets and fonts; `THIRD_PARTY_NOTICES.md` for incorporated material; dependency SBOM/licensing review
- [ ] Rights/compliance wording: reference vs derivative vs private direct inclusion; safe logs and credentials
- [ ] Real hardware proof and five-day evidence **only for stable, not a synthetic alpha demo**
- [ ] Changelog, upgrade/recovery instructions, supported platform/profile table and explicit known limitations
- [ ] Authorised human release decision; GitHub Release created intentionally, not by merging a milestone PR

**Evidence/percentage discipline:** M1/M2 are milestones, not another generated percentage axis. [PROGRESS.md](PROGRESS.md) and existing work-ledger/G1–G8 are still authoritative. Do not count projections or planned release numbers as progress.
