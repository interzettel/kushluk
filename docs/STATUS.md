# Kushluk Status

Last implementation verification snapshot: 2026-10-17 (four-page software CI; physical trials outstanding).
Documentation and issue inventory reviewed: 2026-10-17; six evidence-backed task checkboxes reconciled.

**Status caveat:** the 2026-10-16 inventory did **not** independently rerun CI or physical print tests. Do not infer four-page migration, unattended execution, or real-reader trials are done from the new planning issues. [#43](https://github.com/interzettel/kushluk/issues/43) indexes all issues, and [ISSUE_CROSSWALK.md](ISSUE_CROSSWALK.md) maps the 90 existing work-ledger tasks to accountable issues. Execution blockers have dedicated issues: [#45](https://github.com/interzettel/kushluk/issues/45) format, [#46](https://github.com/interzettel/kushluk/issues/46) print profiles, [#47](https://github.com/interzettel/kushluk/issues/47) local scheduler/retries. Docs/ADR ambiguities: [#44](https://github.com/interzettel/kushluk/issues/44).

### Stable local scheduler operations v1 (F-014 / #47; software only)

`kushluk operate --request PRIVATE.json` accepts strictly versioned local JSON run/status/pause/resume/archived-delivery requests, with separate delivery consent and bounded errors. `kushluk run --latest-start HH:MM` enforces a last *start* cutoff in the configured IANA time zone, not a guaranteed print-ready deadline; date-scoped `pause-day` and `resume-day` persist small private markers without cancelling active runs or submitting jobs. The existing at-most-once run and manual archive reprint receipts remain authoritative. See [OPERATIONS_V1.md](OPERATIONS_V1.md) and `tests/test_operations.py`.

AUT-01 and AUT-03 software work reconciled (AUT now **4/13**, all tasks **12/90 = 13.33%**). Stable agent-side preview/render contracts, adaptive OS timers, delivery-stage observational truth, provider-specific permissions, real unattended five-day operation and device validation remain pending. G1–G8 all **unverified**; no actual schedule or printer was installed.

### Engineering hardening and ledger reconciliation (17 Oct 2026)

Six existing software slices (FMT-01/02/06/07, AUT-02/10) have now been evidence-reconciled from source, tests and previously green Linux/macOS CI into [WORK_LEDGER.md](WORK_LEDGER.md); the task checkboxes are not eight release gates. FMT-03's realistic clipping validation and AUT-03's deadline guard remain open. Source exception messages and SMTP/CUPS failure output have been made generic before persisting into run receipts or printed CLI warnings; specific failure codes and safe local guidance remain. CI's synthetic CLI generation now uses `tools.offline_smoke` (all network sockets and print/email submissions forbidden) on Linux and native macOS, with a real four-page PDF on macOS. This is not live-source, device or host acceptance. Evidence is linked to [#54](https://github.com/interzettel/kushluk/issues/54), [#45](https://github.com/interzettel/kushluk/issues/45), [#46](https://github.com/interzettel/kushluk/issues/46), [#47](https://github.com/interzettel/kushluk/issues/47).

## Planning and next release

The source package currently says `0.1.0`; it is **not** a demonstrated tagged public release. [32 stable feature IDs](FEATURE_CATALOG.md) now map technical/reader outcomes to epics, milestone evidence, target versions and issues. Proposed first public *prerelease* is `v0.2.0-alpha.1` after installation/source-preview gates; first stable `v1.0.0` requires real hardware + five unattended mornings and privacy/source-rights proof per [RELEASE_PLAN.md](RELEASE_PLAN.md). There is no dated release promise. External source review ballots are provisional until an independent Claude review and founder decision: [REUSE_REVIEWS.md](REUSE_REVIEWS.md).

### Experimental EPUB exporter (F-016)

The offline `kushluk export-epub --date YYYY-MM-DD` command builds an EPUB3 ZIP with four reflowable chapters from the archived semantic metadata. It never fetches sources or sends email/print jobs. EPUB XML/ZIP checks and unit tests exist; physical e-reader compatibility/epubcheck/accessibility remain unverified, so this is **not a shipped v1.1 feature**. See [EPUB.md](EPUB.md) and [#33](https://github.com/interzettel/kushluk/issues/33).

### Visual print inspection (F-023 — partial)

`kushluk inspect-print --pdf FILE --output-dir NEW_DIR [--rasterize]` produces private per-page geometry/text anchor reports and optional Poppler PNG snapshots from existing A4 or imposed A3 PDFs. It flags structural problems but **never** claims automatic glyph-accurate clipping or real physical paper approval. See [PRINT_INSPECTION.md](PRINT_INSPECTION.md); source printer reliability and print quality still require #13 hardware evidence.

### Source-rights guardrail (F-007 / F-011 partial)

The private source registry now stores four reader intent choices: ignore, reference-only, derivative, and private-direct. **Only reference-only is executable**; the other modes stay disabled until provider-specific rights and implementation checks exist. Reference-only RSS feeds discard feed-provided description/content from the candidate passed into editorial/archives; headline, link and generic "Open the source" pointer remain. The legacy explicitly configured RSS path now uses the same reference-only content and public-only network fetch protections as approved RSS sources. Publisher-specific source permission checks beyond reference-only and other connectors remain open. See [OPML.md](OPML.md), [#4](https://github.com/interzettel/kushluk/issues/4) and [#49](https://github.com/interzettel/kushluk/issues/49).

### Real-device evidence handoff (not certification)

`kushluk record-field-proof` stores privacy-conscious local operator observations and source-artifact/photo SHA-256 hashes for paper, e-reader, and host restart tests; matching structural PDF inspection is required before reporting a passing paper trial. All receipts explicitly remain **self-reported, independently unverified and not accepted as release gates**. See [FIELD_ACCEPTANCE.md](FIELD_ACCEPTANCE.md). Hardware access and actual user trials remain open under #13/#33/#47.

### Evidence checkpoint — software / external validator / actual devices (17 Oct 2026)

- [PR #93](https://github.com/interzettel/kushluk/pull/93): source-rights intent modes with fail-closed non-executable derivative/private-direct paths; approved RSS reference-only mode strips feed descriptions from exported story content. Full licensed-content processing and legacy RSS policy remain open.
- [PR #94](https://github.com/interzettel/kushluk/pull/94): synthetic EPUB independently **passes W3C EPUBCheck 5.4.0** in [official conformance CI run](https://github.com/interzettel/kushluk/actions/runs/38984422462), plus standard Linux/macOS CI. This is **not** real reader/accessibility verification.
- [PR #95](https://github.com/interzettel/kushluk/pull/95): local private operator reports for paper, e-reader and host reboot with SHA-256 provenance, plus actual-trial runbook. Every receipt remains **self-reported** until an independent reviewer accepts evidence; no real devices were accessed through the connector.

No GitHub Release or version bump, no hardware acceptance or five-morning reliability evidence, no progress gate movement. F-006 is implemented-but-unreleased, F-007/F-011/F-016/F-023 remain partial, and F-009/F-010 remain hardware/host blocked.

### Per-feed RSS degradation, not all-or-nothing

A failed RSS source (unsafe destination, timeout, invalid XML or rejected DTD) no longer suppresses healthy sources. The engine records a redacted source-index failure code and keeps already validated successful candidates, allowing a degraded-but-traceable edition; it never prints private feed URLs/tokens in diagnostics. Unexpected implementation errors still surface instead of being swallowed. See [#49](https://github.com/interzettel/kushluk/issues/49); this does not make provider permissions or content rights complete.

### Safer outbound story references

RSS item links are now checked as references (without network access) before becoming `Story.source_url`: only public HTTP(S) locations, no embedded credentials, private IPs, unsafe schemes, or known token/session query parameters; fragments are removed. Offline EPUB export **rechecks old archived links** under the same policy before embedding hyperlinks. Unsafe links retain the headline/source attribution but have no clickable URL. Some legitimate personalized paywall links may be omitted rather than risk publishing private tokens; this is deliberate. F-011 remains partial; legal authorization and full provider rights checks remain open.

### Local first-run profile (F-008 — partial)

`kushluk setup` creates a private offline local profile for a reader-selected display name, latitude/longitude, timezone, and optional printer queue. Environment overrides and installations without profiles keep working; no credentials or source permissions enter the profile. Guided printer/canonical source onboarding and physical hardware acceptance remain open. See [LOCAL_SETUP.md](LOCAL_SETUP.md) and #5.

### Browser-first local setup slice (F-008, partial)

`kushluk setup-web` provides a temporary loopback-only browser form with CSRF/Host/Origin protections, no third-party resources, and a create-only private profile. It neither activates subscriptions nor configures actual printers or schedulers; see [LOCAL_SETUP.md](LOCAL_SETUP.md). End-user accessibility/real device and installation acceptance are not verified.

### E-reader language semantics (F-016 — partial)

EPUB export accepts an explicit IETF language tag (e.g., `--language de`) and places it consistently in OPF metadata and XHTML navigation/chapters. The old honest `und` default remains for editions without a known dominant language. Static TOC labels have English, German, and Turkish translations. The real W3C EPUBCheck job now covers English and German synthetic exports, but real screen-reader/multilingual content acceptance remains open under #33.

### Browser source consent review (F-007/F-008 — partial)

The loopback-only `setup-web` page now offers a second, **fully offline** source-review page: paste a bounded OPML proposal in memory, preview escaped title and hostname only (no private query tokens), explicitly approve *one feed at a time* into the existing reference-only registry, or pause/resume with fresh consent. No source bodies are imported, fetched or enabled without opt-in. Browser and CLI reuse the same per-feed consent path. Provider-specific full-text rights, novices/accessibility and printer hardware remain unverified. See [LOCAL_SETUP.md](LOCAL_SETUP.md).

### Printer readiness and explicit queue preference in local onboarding (F-008 — partial)

Step 3 of `kushluk setup-web` now offers **explicit** local CUPS queue discovery (`lpstat -p`) and a per-discovered-queue, read-only capability check for advertised A4/A3, duplex and current availability. A browser GET does not trigger hardware probing. After an explicit check and separate opt-in, the reader may save just the checked queue name to an existing private local profile. No print job or CUPS configuration change is performed, and all reported capability states are advisory until real printer trials. See [LOCAL_SETUP.md](LOCAL_SETUP.md), [FIELD_ACCEPTANCE.md](FIELD_ACCEPTANCE.md), #5/#13.

### First-reader software rehearsal (not a human observation)

A full synthetic U1–U6 browser journey regression now validates the ephemeral local server, fictional profile, OPML preview, per-feed consent, pause/resume and explicit checked printer preference without hardware or network source access. The [participant handoff](FIRST_READER_HANDOFF.md) and private `tools.first_reader_evidence` JSON preflight prepare observer notes, but do not certify an independent reader or release gate. The real U1 installation and human comprehension/usability, keyboard accessibility, physical printer, e-reader and unattended host tests remain outstanding. F-008 remains partial.

### Prepared, but not collected: independent acceptance evidence

The [first-reader pilot protocol and blank consent-safe record](FIRST_READER_PILOT.md) specify actual U1–U6 setup tasks including printer readiness; nobody has yet completed an independent first-user observation. [Provider-specific rights proof](RIGHTS_EVIDENCE.md) now specifies license account/scope, transformation boundaries, AI processing, third-party images, attribution, review and revocation evidence required before derivative or private-direct workflows may execute. Neither document confers legal permission or hardware evidence. F-007/F-008/F-011 remain partial; G1–G8 unchanged.

## Repository hygiene

- Default branch: `main`.
- Current durable execution queue: `docs/WORK_LEDGER.md`.
- Target unattended production architecture: `docs/FULL_AUTOMATION.md`.
- Recovered project-chat decisions/ideas: `docs/CHAT_RECONCILIATION.md`.
- CI should remain green before implementation changes are considered settled.

## Stage status

### Stage 0 — Product definition

**Complete enough for implementation.**

The product, requirements, architecture, editorial rules, design direction, privacy boundary, onboarding, failure policy, roadmap, work ledger, ADRs, and recovered chat-history decisions/ideas are recorded.

Two consequential decisions were added after the original Stage 0 pass:
- ADR 0013 — four logical A4 pages with multiple print profiles;
- ADR 0014 — edition-scoped morning intent.

### Stage 1 — Walking skeleton

**Active. Four-page software path implemented; print-profile imposition and real-world proof are pending.**

Current executable implementation:

`weather + calendar + RSS -> candidates -> clustering/ranking -> publication -> four-page A4 HTML -> validated PDF -> archive -> print/email`

Available commands:

- `kushluk run` / `kushluk run-status` — local receipt and at-most-once delivery boundary (not yet real unattended host proof)
- `kushluk deliver-archived` — explicit archived-only resend, separate receipt
- `kushluk print-proof` — synthetic offline A4/A3 PDFs + inspection checklist
- `kushluk doctor`
- `kushluk generate --no-pdf`
- `kushluk generate`
- `kushluk generate --print`
- `kushluk generate --email`
- `kushluk generate --print --email-on-print-failure`
- `kushluk archive-list`

## Implemented

### Inputs
- local **read-only OPML subscription import/export proposal**; new sources are not activated or fetched (F-006, #49);
- Open-Meteo weather;
- RSS/Atom;
- generic ICS calendar;
- calendar fixture fallback.

### Editorial core
- canonical candidates;
- transparent ranking;
- deterministic near-duplicate story clustering;
- source-cluster awareness;
- no forced lead story.

### Publication
- stable edition ID;
- Markdown canonical edition;
- deterministic four-page A4 HTML and versioned logical page IDs;
- warm editorial v0 CSS;
- optional PDF rendering.

### Reliability
- typed failures;
- graceful source degradation;
- four-page PDF count, geometry and content-order validation;
- editorial cut/retry rather than typography shrinking;
- overflow PDF kept as debug output rather than printed.

### Delivery
- native A4-home and A3-folded software print profiles; A3 4|1 / 2|3 imposition with validated A3 landscape geometry;
- CUPS printer discovery/capabilities;
- duplex-aware print submission;
- generic SMTP delivery;
- email fallback when printing is explicitly requested and fails.

### Archive / operations
- Markdown, JSON, HTML and validated PDF archive;
- run/failure/delivery summary;
- archive listing;
- runtime doctor;
- CI tests, linting and walking-skeleton smoke test;
- local run-state receipts blocking repeated/uncertain delivery (full unattended system is unverified);
- crash-safe archival before delivery, typed stage snapshots, human-authorized recovery from archive;
- reproducible offline print-proof kit with file checksums (real paper acceptance pending).

## Decided but not yet implemented

- optional staple marks and real-device calibration for A4/A3;
- optional edition-scoped morning intent;
- layout-manifest/archetype layer;
- automated media acquisition, crop, caption/credit, placement and fallback;
- stable orchestration boundary for native schedulers, n8n, Apple Shortcuts, or future services.

## Needs local/private setup or evidence

- choose the real always-on/local runtime host;
- connect the real printer;
- connect a real task source and preferred personal calendar/mail providers;
- configure SMTP if email delivery is wanted;
- run at least five real morning editions;
- physically compare A4 stapled and A3 folded output;
- tune density, reading time, paper behaviour, image handling, and failure mapping from evidence.

## Research queue

The work ledger tracks dedicated spikes for:
- modern newspaper closing/page-production workflow;
- n8n vs native scheduler vs Apple Shortcuts;
- Canva structured template population;
- Adobe/Creative Cloud/InDesign-like automation;
- automated image acquisition/placement and rights policy.

## Next execution boundary

The next substantive implementation is the stable versioned unattended-run boundary and deadline/reader controls (#47), alongside richer deterministic archetypes (#51), rights-aware assets (#50), and source/verification adapters (#49). A4/A3 **software** print profiles already exist; full device-specific paper preflight and physical acceptance remain (#46/#13). Actual host/printer trials and a first-reader participant remain unverified.

See `docs/WORK_LEDGER.md` for task IDs and acceptance criteria.
