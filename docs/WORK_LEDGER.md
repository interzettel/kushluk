# Kushluk Work Ledger

Last implementation-status review: 2026-10-17.
Issue/task reconciliation reviewed: 2026-10-17 (software-only native scheduler recipe added; external acceptance unchanged).

This is the cross-stage execution ledger for Kushluk. It records work that is decided, open, blocked, or research-only. It complements `ROADMAP.md`; the roadmap explains sequencing, while this file is the operational source of truth for unfinished work.

**Traceability:** every numbered task in this file is mapped to its primary GitHub implementation/discussion owner in [ISSUE_CROSSWALK.md](ISSUE_CROSSWALK.md) (90 tasks in the 2026-10-16 snapshot). [GitHub master issue #43](https://github.com/interzettel/kushluk/issues/43) is the issue portfolio index; issue creation/closure alone does **not** change the task checkboxes. The first explicitly scoped implementation packages are #45–#52 and document reconciliation is #44. See [STATUS.md](STATUS.md) for independently verified implementation status.

**Known ADR reconciliation issue:** accepted ADR 0015 (replaceable orchestration and agent runtime) is now indexed; two files still claim accepted ADR 0012. Resolve the duplicate under #44 before treating either variant as a uniquely canonical decision. Do not silently change accepted-ADR text.

## First operator-reported physical and scheduled-host observations — 2026-10-19

The dated [October local field-pilot register](FIELD_PILOT_2026_10.md) records four A4 **single-sided** pages produced on an HP DeskJet 2800 series (2026-10-18), manual edition `20261018-001` validated/archived in 6.47 s (2026-10-18), and one one-time Windows Task Scheduler → Ubuntu 24.04 WSL2 **digital-only** morning edition `20261019-001` (07:30 trigger; archive ready at 07:30:08 local, `ready_by_met=true`; 1.05 s recorded trigger lag; 7.19 s process-to-archive). Follow-up host evidence is tracked under [#47](https://github.com/interzettel/kushluk/issues/47); integration and paper quality under [#13](https://github.com/interzettel/kushluk/issues/13).

**Next:** five distinct 07:30 digital-only trial tasks were registered for **20–24 October 2026**, but **0/5 has run or been observed** at this snapshot. Check task results and local receipts after each morning, then test reboot/wake, outage/replay and independently reviewed physical delivery. Windows printer access is **not** native WSL2 CUPS proof. The pilot does not change any **26/90** checked implementation tasks or **0/8** accepted delivery gates; manual paper output and one scheduled archive are *partial observations*, not automatic acceptance of TRIAL-01/02/04 or AUT-09/12.

## M1 follow-up: bounded archive compatibility and dependency inventory — #54/#87, 2026-10-17

[PR #121](https://github.com/interzettel/kushluk/pull/121) builds on green M1 clean-install [PR #120](https://github.com/interzettel/kushluk/pull/120). Both clean wheel and sdist environments now run `pip check` and produce an installed Python distribution/version/license-**metadata** inventory, with SHA-256 provenance and explicitly **incomplete** legal, native dependency and vulnerability checks. [Audit bounds](DEPENDENCY_AUDIT.md).

The installed CLI `kushluk archive-check --archive-root ...` now assesses bounded private archived **metadata** read-only, classifying canonically structured schema-v2 pages as readable, legacy schema-v1/future as unsupported pending migration, and malformed/symlink references as unsafe. It exposes aggregate counts only; no archived content migration or physical/SMTP delivery approval. [Archive compatibility contract](ARCHIVE_COMPATIBILITY.md).

**Remaining:** authoritative independent license/VEX/CVE review, native PDF/font dependency notice review, an approved and reversible migration design for v1, actual older-user archived editions, and any future release tag/version. **Task ledger remains 26/90 · 28.89%; evidence gates G1–G8 0/8**, package version 0.1.0, **no prerelease publication**.

## Google OAuth source adapters and exact DOI metadata checking — #49/#48/#16, 2026-10-17

[PR #119](https://github.com/interzettel/kushluk/pull/119) adds a local Gmail metadata OAuth client, a separate Google Tasks read-only client wired into real editions, limited cloud HTTP queries and a conservative exact Crossref bibliographic checker. See [GOOGLE_PROVIDERS.md](GOOGLE_PROVIDERS.md).

**Verification boundary:** the adapters are real API-shaped implementations, but both local OAuth grants require the owner to create their own Google Cloud client, explicitly consent and run a real-account test. This session had no such grant and no live Gmail/Tasks acceptance. Crossref direct live probe could not complete due to local network/DNS restrictions; fixture tests cover match/conflict/abstain. No generic factual claims are marked verified. Gmail review remains inactive, paid derivatives and private copy disabled.

**Ledger unchanged: 26/90 · 28.89%; SRC 3/10 · 30.00%.** SRC-01 still awaits real connected-mail acceptance; SRC-08 still awaits claim-level verification across independent primary evidence; all gates G1–G8 0/8. Version 0.1.0 unchanged.

## Editorial input adapters, conservative provenance and local newsletter discovery — #49/#48/#16, 2026-10-17

[PR #118](https://github.com/interzettel/kushluk/pull/118) adds optional task/research inputs and metadata-only newsletter proposals. [EDITORIAL_INPUTS.md](EDITORIAL_INPUTS.md) documents the rights and trust boundaries.

**Three software-level SRC tasks checked, with narrowly scoped evidence:**
- **SRC-03**: working provider-replaceable local JSON task adapter, owner-provided export; strict schema, due/overdue filtering, no completed task, no credentials and nonsecret failure behavior. **Real remote OAuth task provider remains open.**
- **SRC-04**: opt-in Crossref public scholarly metadata title search with 5-result bound, HTTPS hostname-pinned SSRF/redirect guard; includes DOI pointer, originating date and no abstract/body or invented facts. **Broader current-news and general web research adapters remain open.**
- **SRC-07**: preserved candidate/origin identifiers, clean source URL, publish/retrieval timestamps, reference-only rights and conservative verification status through clustering, story selection and publication archive.

**Partially implemented but unchecked:** SRC-01 local owner-exported header discovery with 60-day/250-record limits and no message bodies, but no live consented mailbox API; SRC-02 explicit four per-newsletter rights modes are stored but **all ingestion remains disabled** pending provider-specific permission review; SRC-08 unverified/conflicted source-pointer states, not factual claim verification; SRC-09 existing clustering covers RSS and research but not newsletter/social ingestion or independent disagreement evidence. SRC-05/06/10 still open. #16 local metered cost/production adversarial tests remain separate.

**Ledger software snapshot:** **26/90 · 28.89%** checked; SRC **3/10 · 30.00%**. Evidence gates **G1–G8 0/8 · 00.00%**; version stays `0.1.0`. No public, mail, OAuth, physical print or verified-claim acceptance claimed.

## Rights-aware owner-imported media — #50, 2026-10-17

**Status:** [PR #117](https://github.com/interzettel/kushluk/pull/117) under full Linux/macOS CI review. [MEDIA_RIGHTS.md](MEDIA_RIGHTS.md) defines private-print versus shareable rights boundaries, explicit local grant/import/assignment, checksum-secured originals and text-only fallback.

**Six software tasks implemented and checked, subject to final green CI:**

- **IMG-01:** `MediaAsset` schema-v1 source/license/permission, SHA-256 normalized identity, attribution, alt/caption, resolution and crop/focal policy; owner must affirm `--approve-print`.
- **IMG-04:** deterministic `lead-66x33` print slot in typed composition budget, one eligible lead on balanced or practical-heavy pages; multi-lead news covers remain deliberately text-only.
- **IMG-05:** bounded focal crop or white-letterbox contain, and explicit fallback to the existing text article on low DPI, corrupt, missing, revoked, ineligible or unknown asset.
- **IMG-06:** bounded caption/credit/alt metadata, printable credit/license below the figure, escaping/word wrapping, canonical source citation preserved.
- **IMG-07:** minimum 180 DPI at 66×33 mm after crop and SHA-256 content checks, with no implicit upsampling of undersized image.
- **IMG-08:** private content-addressed normalized originals and versioned rights record; selected immutable print crop copied into archived edition; explicit `media-remove` revocation does not silently rewrite earlier archived/distributed images.

**Partial/unchecked:** IMG-02 remote provider-specific lawful acquisition deliberately not implemented; IMG-03 duplicate, hotlink, low-resolution, SVG, unknown-license and corruption checks exist, but real-world watermark detection and suitability review do not; IMG-09 synthetic shape tests and three image-bearing comparison PDFs exist, but genuine physical paper inspection/portrait editorial approval is still required. RES-IMG-01 research/legal approval remains outstanding despite a provisional written policy. Shareable rights are explicitly owner-attested, **not independently legally verified**.

**Software task snapshot:** **23/90 · 25.56%** checked overall, image handling **6/9 · 66.67%**. Independent physical/product evidence **G1–G8 0/8 · 00.00%**; package stays `0.1.0`. Fixtures are original geometric artwork only, no web download or real print operation.

## Deterministic editorial composition — #51 / #21, 2026-10-17

**Implementation branch:** [PR #116](https://github.com/interzettel/kushluk/pull/116), pending merge review and full PDF CI signoff. The canonical four logical A4 pages are unchanged; content planning now lives in `src/kushluk/composition.py` and [LAYOUT_COMPOSITION.md](LAYOUT_COMPOSITION.md).

**Evidence-backed software checks in this tranche (4):**
- **LAY-02:** finite, typed balanced/news-heavy/practical-heavy archetype family, independent of printer profile;
- **LAY-04:** deterministic, auditable shorten/move/demote/replace/remove-unapproved-image/omit fit policy with no silently dropped mandatory calendar/task entries. A true post-render archetype repair switch remains an extension;
- **LAY-05:** independently modelled editorial archetype and CSS theme tokens, shared four-page canonical structure;
- **LAY-07:** deterministic production auto-selector based on manifest counts with a persisted `select_archetype` audit decision; direct archived/EPUB builder defaults to balanced for compatibility.

**Partial work, deliberately unchecked:**
- **LAY-01:** typed `CompositionBlock` (lead/brief/practical/source index) is real, but quote/table/language/continuation block taxonomy remains incomplete;
- **LAY-03:** character and zero-image slot budgets work; printed line/glyph metrics, approved image sizes and caption/aspect-ratio constraints are not complete;
- **LAY-06:** all three variants generate synthetic four-page PDFs in CI, but final design/reader approval and broad corpus acceptance are outstanding;
- **LAY-08/09:** HTML/SVG/PDF comparison/box-diagnostics fixtures exist, but frozen approved visual baselines and six-column binding/fold-safe physical proof are missing. The WeasyPrint practical-row fallback is an intentional partial limitation;
- **FMT-03:** test inspector adds per-page text/footer/size bounds, but content clipping/optical readability across real papers and fonts remains open;
- **LAY-10/11:** discretionary vocabulary, charts, maps, reading time remain research.

**Software ledger:** **17/90 tasks · 18.89%**, LAY **4/11 · 36.36%**. **Evidence gates G1–G8: 0/8 · 00.00%**; no release, printer, physical-reader or real editorial approval claim. The comparison kit uses only a fixed synthetic edition and never submits print/email or fetches live sources.

## North star

**Kushluk should be capable of producing and delivering the morning edition without manual editorial layout work.**

The intended unattended path is:

```text
scheduled trigger / user trigger
  -> personal context + optional morning intent
  -> source ingestion
  -> research / verification
  -> editorial selection and copy fitting
  -> image/asset resolution
  -> layout plan
  -> deterministic four-page renderer
  -> validation / cut loop
  -> print-profile imposition
  -> print and/or digital delivery
  -> archive + run ledger
```

Workflow tools such as n8n, Apple Shortcuts, systemd/cron, launchd, or a future hosted scheduler may trigger and coordinate the run, but Kushluk's canonical data model, editorial rules, renderer, validation, archive, and failure semantics remain in the core application.

## Status vocabulary

- **DONE** — implemented or decision completed.
- **NEXT** — immediate implementation/research target.
- **PLANNED** — accepted work, not yet started.
- **RESEARCH** — evidence needed before implementation choice.
- **BLOCKED** — depends on hardware, credentials, or a user decision.
- **TRIAL** — implementation exists but needs real-world evidence.

## Decision ledger

| ID | Status | Decision |
|---|---|---|
| ADR-0012 | DONE | Newsletter discovery uses explicit per-source modes: ignore, reference, derivative, private direct inclusion. |
| ADR-0013 | DONE | Canonical edition geometry is four logical A4 pages. A4 and A3 are print/imposition profiles, not separate editorial layouts. |
| ADR-0014 | DONE | Optional spoken/typed morning intent is edition-scoped and does not silently become durable profile data. |
| ADR-0015 | DONE | The core edition engine owns publication state; orchestration, agents and design adapters are replaceable via stable Kushluk contracts. |
| D-RENDER | DONE | Approved production layouts are deterministic; generative models do not redesign the edition at print time. |
| D-AUTO | DONE | Full automation is the product target; humans may configure/review, but daily layout assembly must not require manual InDesign/Canva work. |

## AUT-09 / AUT-12 measured diagnostics slice — 2026-10-17

[Issue #47](https://github.com/interzettel/kushluk/issues/47) now has a **read-only software timing/reporting implementation** without activating an actual scheduler or assuming paper delivery.

- **AUT-09 (partial, unchecked):** `src/kushluk/run_metrics.py` and `kushluk run-report` expose allowlisted UTC stage events, source/renderer/archive milestones, fail-closed unknown/failed/submitted transport-state distinctions, and explicit `physical_print_verified: false`. `tests/test_run_metrics.py` includes private-token, inconsistent history and submission-uncertain cases. **Still missing:** true physical printer completion, independently observed delivery, alerts/notification pathway.
- **AUT-12 (partial, unchecked):** `kushluk run --ready-by HH:MM` records an optional **software archive** target; `kushluk timing-plan --ready-by HH:MM --margin-minutes N --history-days N` reads up to 90 previous local edition receipts, requires >=3 validated archive timings and suggests a conservative nearest-rank p90 start with optional buffer. Generated native scheduler recipes pass an expected trigger clock so timing reports can separately measure process launch lag; the planner prefers three or more comparable trigger-to-archive samples, otherwise labels its run-start-only basis. It **never edits/installs** the timer or represents fixtures as measurements of a real host. **Still missing:** observed OS scheduler trigger-to-start/wake latency, production margins and independent ready-by-08:00 acceptance. Manual start-clock adjustments continue via `schedule-export`.
- **Five-day local rehearsal (synthetic only):** `tests/test_synthetic_five_mornings.py` exercises date isolation, no duplicate resends, paused mornings, deadline misses and repeat invocations using fake delivery-free stages. This is not TRIAL-01/04/05 and not a real host/reboot.
- [Timing methods and evidence limitations](TIMING_REPORTS.md). **No AUT-09 or AUT-12 checkbox advanced** until the complete acceptance description can be met. The operational ledger remains **13/90 · 14.44%** and all G1–G8 **0/8 · 00.00%**.

## Unattended production contract — current completion plan, 2026-10-17

**Priority:** [Issue #47](https://github.com/interzettel/kushluk/issues/47) (Stage 1 / P1). This is the actively maintained work list: it describes *what remains* even when an earlier parent checkbox was checked for a software slice. A programmatic timer template is not five genuinely unattended mornings.

| Order | Ledger ID | Executable acceptance boundary | Status |
| --- | --- | --- | --- |
| 1 | AUT-05 | Versioned, owner-reviewable **systemd user timer + macOS launchd LaunchAgent**, configurable trigger and latest-start margin; export never installs, enables or prints; synthetic unit tests | **Software implemented**; real-host enable/reboot unverified |
| 2 | AUT-09 | Durable typed chronological run stages and safe last-known-state query across Linux/macOS processes; stale receipt after crash must not be treated as a live/print-complete run | **Software partial**: advisory run lock and stage trace; true printed/recipient delivery cannot be observed from CUPS/SMTP submission |
| 3 | AUT-12 | Start clock set explicitly by owner; no 07:30 hard-coded product invariant; measure actual trigger/readiness latency and tune deadline margin from observed runs | **Configurable software implemented**, adaptive/observed margin not yet verified |
| 4 | AUT-01/02/03/10 | Strict operation contract, date-scoped idempotency and safe manual archive-only reprint with no implicit retry after crash | **Software implemented**, full host/adapter acceptance open |
| 5 | AUT-04 | Edition-scoped morning intent with no persistence into global interests | **Open**; requires editorial/ranking integration |
| 6 | AUT-06/07/08/11/13 & RES-AUTO-01/02 | Optional n8n/Shortcuts/AirPrint/wake/IPP research or adapters; do not make a proprietary service core infrastructure | **Research or conditional work**, not Stage 1 blockers |

**Acceptance still outstanding before marking #47 finished or G3 verified:** actual host selection and user-authorized install, real systemd/launchd enable/disable and reboot/wake checks, at least five timed morning editions, one deliberate outage/crash and human-checked reprint avoidance, exact 08:00-ready metrics, safe local logs and privacy, printer/SMTP queue acceptance and true delivery boundaries. Cross-process pause/start ordering and network-filesystem lock correctness are also not proven. Provider connections, physical devices and human observations have not been fabricated.

**Progress rule:** `AUT-05` may be checked for a **working exported recipe with tests**, even though its real unattended-host acceptance remains open. `AUT-09` and `AUT-12` remain unchecked until their full observability/adaptive or verified scheduling requirements are met. Separately tracked delivery gates G1–G8 remain unverified.

## Scheduler operations v1 evidence — 2026-10-17

Two previously open software tasks are now checked with dedicated tests, pending PR CI review; **hardware and real unattended host proofs remain separate**.

| Task | Delivered software evidence | Still not a product/release acceptance |
| --- | --- | --- |
| AUT-01 | `src/kushluk/operations.py`: versioned, strict local JSON `operate` boundary for run/status/pause/resume/archived delivery. `tests/test_operations.py` exercises invalid/untrusted requests and permission boundaries. | Further ADR 0015 operations (independent preview/render/provider-health) and full agent/tool integration remain later work. |
| AUT-03 | `scheduled.run_once` local-time `latest_start` cutoff plus existing durable at-most-once receipts; `pause_day`/`resume_day` only affect future starts. `tests/test_operations.py` covers cutoff, replay, tampering and authorized reprints. | No guarantee edition is *ready* at cutoff, no real print/device proof, and atomic pause-vs-start race remains a noted implementation limit. |

**Operational ledger:** now **12/90 · 13.33%** (AUT **4/13 · 30.77%**); evidence gates **G1–G8: 0/8 · 00.00%**. AUT-05 native-host recipe is documented as an example but **not checked** without an independently verified unattended deployment; AUT-09 complete real-world stage taxonomy remains open.

## Evidence reconciliation — 2026-10-17

Six previously unchecked tasks are now checked **for implemented software behavior only**, after source/test and current green CI review. This is not a declaration that related GitHub issues or real-device evidence gates are finished.

| Ledger task | Software proof | What remains outside its completed slice |
| --- | --- | --- |
| FMT-01 | [#80](https://github.com/interzettel/kushluk/pull/80), `tests/test_four_pages.py`: stable four-page publication model and archived page IDs | Legacy one-page archive migration proof under #45 |
| FMT-02 | [#80](https://github.com/interzettel/kushluk/pull/80), `tests/test_four_pages.py`: deterministic four-page HTML/PDF without manual composition | More sophisticated page archetypes (#51) |
| FMT-06 | [#81](https://github.com/interzettel/kushluk/pull/81), `tests/test_print_profiles.py`: A3 software imposition 4|1 and 2|3, validated PDF | Device-specific duplex orientation and physical paper proof (#13) |
| FMT-07 | `src/kushluk/printing.py`, `tests/test_printing.py`: explicit one-sided CUPS fallback when duplex is unsupported | Printer-specific real-device test (#46/#13) |
| AUT-02 | [#82](https://github.com/interzettel/kushluk/pull/82), `src/kushluk/cli.py`, `tests/test_scheduled.py`: `kushluk run` date-scoped replay protection | Versioned external operation contract (#47/AUT-01), unattended host proof |
| AUT-10 | [#83](https://github.com/interzettel/kushluk/pull/83), `tests/test_recovery.py`: explicit idempotent archive-only delivery retry, no forced regeneration | Real printer-state uncertainty and five-morning host trial |

**Not checked despite partial code:** FMT-03 (realistic per-page clipping/overflow), FMT-04 (A4 physical duplex sheet validation), FMT-08/09/10 (complete platform/profile/geometry and paper preflight), AUT-01/03/05/09 (complete versioned contract, deadline controls, unattended recipe and all run-state transitions). All G1–G8 evidence gates remain unverified. The checked-task percentage reports ledger state, **never overall product readiness**.

## Immediate execution queue

### P0 — Make the repository internally consistent

- [x] **DOC-01** Record four-page A4/A3 print-profile decision.
- [x] **DOC-02** Record ephemeral morning intent.
- [x] **DOC-03** Update README, Product, Requirements, Architecture, Editorial System, Design Brief, Status, Roadmap, Open Decisions, and Stage 1 backlog so they no longer describe the superseded one-sheet format as canonical.
- [ ] **DOC-04** Keep this ledger current whenever a consequential task is added, completed, blocked, or abandoned.
- [x] **DOC-05** Reconcile prior project-chat decisions/ideas into `CHAT_RECONCILIATION.md` and promote stable items into canonical docs.

### P1 — Four-page production migration

- [x] **FMT-01** Replace the one-page publication geometry with four logical A4 pages in the canonical publication schema.
  - Acceptance: page identity/order is explicit and archived.
- [x] **FMT-02** Refactor renderer/templates to produce four logical A4 pages before physical imposition.
  - Acceptance: deterministic HTML/PDF output, no hand editing.
- [ ] **FMT-03** Update validation from “exactly one page” to four-page geometry and per-page overflow checks.
- [ ] **FMT-04** Implement **A4 Home Printer** profile: two A4 sheets, duplex where supported, logical order 1–4.
- [ ] **FMT-05** Add optional three-point staple registration marks inside the safe binding margin.
- [x] **FMT-06** Implement **A3 Folded Newspaper** imposition: outside `4 | 1`, inside `2 | 3`, then half-fold to A4.
- [x] **FMT-07** Add single-sided A4 fallback when duplex is unavailable.
- [ ] **FMT-08** Extend printer capability/profile selection without changing editorial layout.
- [ ] **FMT-09** Add print fixtures for margins, fold safety, binding safety, rotation, and duplex edge choice.
- [ ] **FMT-10** Add paper/profile preflight: detect incompatible media where the platform exposes it; otherwise rely on explicit paper-profile configuration without pretending the printer knows stock/colour.

### P1 — Daily full automation

- [x] **AUT-01** Define a stable run request/response contract so external orchestrators can trigger Kushluk without knowing internal implementation details.
- [x] **AUT-02** Add a scheduler-safe CLI/API entrypoint that is idempotent for a date/edition.
- [x] **AUT-03** Add deadline and “already generated/printed” guards to prevent accidental duplicate morning prints.
- [ ] **AUT-04** Add optional `morning_intent` input to the run model and ranking trace.
- [x] **AUT-05** Provide an unattended local-host recipe (systemd/cron/launchd) as the baseline.
- [ ] **AUT-06** Prototype an n8n orchestration that calls the same stable Kushluk run boundary rather than reimplementing editorial logic inside n8n.
- [ ] **AUT-07** Prototype Apple Shortcuts as a trigger/control surface: generate now, pause today, digital-only, reprint, and optional voice morning intent.
- [ ] **AUT-08** Investigate the practical Apple printing path: what can be automated through macOS printing/CUPS versus what AirPrint/iOS requires interactively.
- [ ] **AUT-09** Add run-state observability: started, sources complete, editorial complete, rendered, validated, submitted to printer, printed/failed, digitally delivered.
- [x] **AUT-10** Add recovery semantics so a failed print never causes editorial regeneration unless explicitly requested.
- [ ] **AUT-11 (RESEARCH)** Test wake-up, local-host-availability, and printer-reachability triggers as optional release signals without weakening the configured deadline.
- [ ] **AUT-12** Keep exact pipeline start time adaptive/configurable; an earlier ~07:30 idea is only a scheduling heuristic for an 08:00-ready edition.
- [ ] **AUT-13 (RESEARCH)** Test driverless/network CUPS/IPP from the chosen local/home-server deployment, including containerised operation only if it simplifies printer reachability rather than complicating it.

### P1 — Source acquisition and editorial input

- [ ] **SRC-01** Implement connected-mail newsletter discovery over a bounded recent window.
- [ ] **SRC-02** Implement per-newsletter modes from ADR 0012.
- [x] **SRC-03** Add a real task connector.
- [x] **SRC-04** Add public-web/news research as a provider-independent candidate source.
- [ ] **SRC-05** Add Reddit/Hacker News connectors.
- [ ] **SRC-06** Investigate/implement X/social source adapter without making it a hard dependency.
- [x] **SRC-07** Preserve original source URLs/message references and timestamps through synthesis.
- [ ] **SRC-08** Strengthen claim verification for material stories.
- [ ] **SRC-09** Deduplicate newsletters, RSS, social, and web coverage into story clusters.
- [ ] **SRC-10** Add travel-context signal adapters from calendar plus connected ticket/confirmation/provider sources without building a permanent travel-history corpus.

### P1 — Automated image acquisition and placement

- [x] **IMG-01** Add a first-class media asset model: source URL, local/cache path, licence/usage status, attribution, caption, alt text, aspect ratio, dimensions, focal point, crop policy, and verification state.
- [ ] **IMG-02** Build image candidate acquisition for stories from original/reputable sources where lawful and technically available.
- [ ] **IMG-03** Reject hotlink-only, low-resolution, watermarked, duplicate, or unclear-rights assets according to policy.
- [x] **IMG-04** Add deterministic image placement slots to the layout manifest.
- [x] **IMG-05** Add automatic crop/focal-point handling with safe fallbacks (`contain`, alternate crop, illustration, or text-only).
- [x] **IMG-06** Add caption and attribution fitting rules.
- [x] **IMG-07** Validate effective print resolution and prevent unusable assets from reaching print.
- [x] **IMG-08** Cache selected assets for reproducible archived editions.
- [ ] **IMG-09** Create a fixture suite covering portrait, landscape, square, tiny, missing, and awkward-focal-point images.

### P1 — Layout grammar and template family

- [ ] **LAY-01** Define semantic content blocks independent of visual template: lead, brief, practical strip, calendar, weather, quote, image story, table, language item, continuation/QR, etc.
- [x] **LAY-02** Define a finite family of page archetypes rather than one rigid template or free-form generated design.
- [ ] **LAY-03** Define layout-slot capacity rules in characters/lines/aspect ratios so the editor can fit copy before rendering.
- [x] **LAY-04** Define overflow substitutions: shorten, move, demote, remove image, switch archetype, or cut story.
- [x] **LAY-05** Separate **layout archetype** from **visual theme/style tokens** so the same editorial structure can support multiple approved looks.
- [ ] **LAY-06** Build at least three production-ready archetypes: balanced day, news-heavy day, and schedule/practical-heavy day.
- [x] **LAY-07** Add deterministic layout scoring/selection based on the publication manifest.
- [ ] **LAY-08** Freeze approved explorations into HTML/CSS/SVG templates and regression fixtures.
- [ ] **LAY-09** Implement/test the six-column A4 base grid with shared inner binding/fold safety.
- [ ] **LAY-10 (RESEARCH)** Test the recovered editorial vocabulary (`WORTH KNOWING`, `FROM YESTERDAY`, `SINCE WE LAST LOOKED`, `NEARBY`, `ONE SMALL THING`, `WORD OF THE DAY`, `TEN MINUTES`, `GO DEEPER →`) without turning every label into a permanent box.
- [ ] **LAY-11 (RESEARCH)** Test small maps, tiny charts/sparklines, source-confidence display, and per-item reading-time estimates for actual print value.

### P2 — External design-tool integration

- [ ] **DES-EXT-01 (RESEARCH)** Test whether Canva templates can be reliably populated from structured data while preserving exact typography, overflow behaviour, image crops, and four-page ordering.
- [ ] **DES-EXT-02 (RESEARCH)** Test Adobe/Creative Cloud automation paths, including whether an approved InDesign-like template can be populated/exported unattended through available APIs/connectors.
- [ ] **DES-EXT-03** Treat Canva/Adobe as optional authoring/import/export tooling unless the spike proves they can meet unattended deterministic production requirements.
- [ ] **DES-EXT-04** If external templates are used, define a template contract: named text slots, image slots, max copy lengths, style IDs, page IDs, and export profile.
- [ ] **DES-EXT-05** Preserve a renderer-native fallback so Kushluk is not locked to a design SaaS.

### P2 — Production research

- [ ] **RES-NEWS-01 (RESEARCH)** Document how daily newspapers actually close an edition: editorial budget meeting, page plan/dummy, section deadlines, copy desk, photo desk, page design, late-news replacement, preflight, plate/print deadlines.
- [ ] **RES-NEWS-02 (RESEARCH)** Identify which newsroom practices transfer to Kushluk: fixed grids, page budgets, story length classes, edition deadlines, late-breaking replacement slots, and preflight.
- [ ] **RES-NEWS-03 (RESEARCH)** Quantify what is automated versus manually paginated in modern newspaper production systems.
- [ ] **RES-AUTO-01 (RESEARCH)** Compare n8n, native OS schedulers, Apple Shortcuts, and a lightweight Kushluk scheduler for local-first reliability.
- [ ] **RES-AUTO-02 (RESEARCH)** Determine whether the project needs a workflow engine at all, or only a stable trigger/API plus native scheduler.
- [ ] **RES-IMG-01 (RESEARCH)** Define a safe image-rights policy for private personal editions versus any future shared/public edition.

### P2 — Editorial/user model

- [ ] **ED-01** Add explicit morning-intent influence to selection explanations.
- [ ] **ED-02** Add durable interest model separate from edition-scoped intent.
- [ ] **ED-03** Add continuity/story threads across editions.
- [ ] **ED-04** Improve serendipity selection using source diversity and learning value.
- [ ] **ED-05** Add user-controlled density modes without changing core layout safety.
- [ ] **ED-06** Add feedback capture that is useful without becoming surveillance telemetry.

### P2 — Onboarding and controls

- [ ] **UX-01** Onboarding: printer profile and capabilities.
- [ ] **UX-02** Onboarding: email/newsletter discovery and review.
- [ ] **UX-03** Onboarding: interests/beats and language policy.
- [ ] **UX-04** Controls: pause/snooze, print/digital-only, reprint, generate now.
- [ ] **UX-05** Controls: choose A4 Home Printer / A3 Folded Newspaper when multiple profiles are available.
- [ ] **UX-06** Surface failures in human language without exposing implementation noise.
- [ ] **UX-07** Preserve the physical morning ritual in UX: minimal screen interaction, pick up/optionally staple A4 output, or fold/use A3 output.
- [ ] **UX-08 (PLANNED)** Add later messaging delivery (WhatsApp was an explicit example in the founding chats) only through an appropriate replaceable connector.

### P1/P2 — Real-world proof

- [ ] **TRIAL-01 (BLOCKED)** Select the real always-on/local runtime host.
- [ ] **TRIAL-02 (BLOCKED)** Connect the real printer.
- [ ] **TRIAL-03 (BLOCKED)** Configure real calendar/task/mail credentials locally.
- [ ] **TRIAL-04 (TRIAL)** Print and read at least five consecutive real morning editions.
- [ ] **TRIAL-05** Record generation time, print reliability, what was read, what was ignored, overflow failures, image failures, and binding/fold friction.
- [ ] **TRIAL-06** Run A4 stapled and A3 folded physical comparisons before final typography/layout lock.
- [ ] **TRIAL-07** Use the trial evidence to set final reading-time and density targets.

## Completion boundary for “full automation v1”

Kushluk reaches full-automation v1 when all of the following are true:

1. A scheduler or external trigger can start an edition without opening an editor.
2. Personal context and configured sources are acquired without manual exports.
3. Optional morning intent can be supplied by voice/text but is not required.
4. Stories are selected, verified, written, and cut automatically.
5. Images are acquired, attributed, cropped, and placed automatically or safely omitted.
6. A deterministic layout archetype is selected and rendered into four logical A4 pages.
7. The edition validates without manual layout repair.
8. The system chooses/uses the configured A4 or A3 print profile.
9. Printing/digital fallback is executed and status is recorded.
10. The complete edition and run trace are archived reproducibly.

Anything that still requires opening InDesign/Canva every morning is not full automation.
