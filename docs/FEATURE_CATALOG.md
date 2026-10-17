# Canonical feature catalogue

**Planning baseline:** 17 October 2026 · [Owner #87](https://github.com/interzettel/kushluk/issues/87) · [Release plan](RELEASE_PLAN.md) · [Current code status](STATUS.md). This is the **feature layer**, not an alternative issue/task backlog.

## What is a feature?

A **feature** is a user/maintainer-visible capability with a stable `F-###` ID, owner issue, demonstrable benefit, and release target. An **epic** is a coordination group of multiple features (the domain code below); a **milestone** is a vertical slice with acceptance evidence; an **issue/work package** owns implementation; the **90 task IDs** and **8 evidence gates** retain their existing authorities. Release versions indicate intended packaging **not shipped status**. Tasks can be completed before a milestone while a feature remains unverified. Features may move between *future* releases only with a dated note, and only an actual tag/release is marketed as shipped.

**State vocabulary:** `implemented-unreleased` = code exists but the target release has no tag; `partially-implemented` = slices exist with open acceptance; `building` = bounded implementation under way; `planned`, `research`, `blocked-hardware/host`, `decision-open` are **not delivery claims**.

## Feature × epic × milestone × version × proof owner

| ID | Feature | Epic | Milestone | Target version | Issue owner | State | Evidence required |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F-001 | Canonical four-page edition | PUBLISH | M0 | v0.2.0-alpha.1 | [#45](https://github.com/interzettel/kushluk/issues/45) | implemented-unreleased | Four numbered A4 pages, ordered source refs, archives, PDF validation; merged #80; overflow QA still open |
| F-002 | A4/A3 print profiles | DELIVER | M0 | v0.2.0-alpha.1 | [#46](https://github.com/interzettel/kushluk/issues/46) [#7](https://github.com/interzettel/kushluk/issues/7) | implemented-unreleased | Software A4/duplex/single-sided and imposed A3; merged #81; hardware proof missing |
| F-003 | Crash-safe scheduled local run | OPERATE | M0 | v0.2.0-alpha.1 | [#47](https://github.com/interzettel/kushluk/issues/47) [#17](https://github.com/interzettel/kushluk/issues/17) | implemented-unreleased | At-most-once and archive-only manual recovery merged #82/#83; no unattended host acceptance |
| F-004 | Offline print proof and diagnostics | DELIVER | M0 | v0.2.0-alpha.1 | [#13](https://github.com/interzettel/kushluk/issues/13) [#46](https://github.com/interzettel/kushluk/issues/46) | implemented-unreleased | Synthetic A4/A3 PDFs and inspection manifest #83; printer evidence missing |
| F-005 | Local weather/RSS/ICS sources | SOURCES | M0 | v0.2.0-alpha.1 | [#3](https://github.com/interzettel/kushluk/issues/3) [#49](https://github.com/interzettel/kushluk/issues/49) | implemented-unreleased | Weather, RSS and fixture/ICS calendar; no blanket private-provider permissions |
| F-006 | Source list OPML import/export preview | SOURCES | M1 | v0.2.0-alpha.1 | [#49](https://github.com/interzettel/kushluk/issues/49) [#48](https://github.com/interzettel/kushluk/issues/48) | implemented-unreleased | Offline parser, URL dedup, unactivated private proposal and re-export tested in #89; no released package tag |
| F-007 | Source catalog and permission review | SOURCES | M2 | v1.0.0 | [#4](https://github.com/interzettel/kushluk/issues/4) [#48](https://github.com/interzettel/kushluk/issues/48) [#49](https://github.com/interzettel/kushluk/issues/49) | partially-implemented | Per-feed rights modes; pinned-public-IP, reference-only and per-source recovery; opt-in read-only connectivity preflight; guided setup and licensed source reuse pending |
| F-008 | Guided local installation and setup | SETUP | M2 | v1.0.0 | [#5](https://github.com/interzettel/kushluk/issues/5) [#12](https://github.com/interzettel/kushluk/issues/12) | planned | Cross-platform non-agent first edition without code editing; agent path optional |
| F-009 | Physical home-printer acceptance | DELIVER | M2 | v1.0.0 | [#13](https://github.com/interzettel/kushluk/issues/13) [#46](https://github.com/interzettel/kushluk/issues/46) | blocked-hardware | Hardware operator proof receipts available via #95, but no actual A4/A3 hardware/photos have been independently reviewed |
| F-010 | Five unattended mornings | OPERATE | M2 | v1.0.0 | [#13](https://github.com/interzettel/kushluk/issues/13) [#47](https://github.com/interzettel/kushluk/issues/47) | blocked-host | 5 logged editions, restart/sleep and error recovery, no duplicate deliveries |
| F-011 | Rights-aware publication and source receipts | TRUST | M2 | v1.0.0 | [#4](https://github.com/interzettel/kushluk/issues/4) [#16](https://github.com/interzettel/kushluk/issues/16) | partially-implemented | Four intent modes persisted; all RSS sources discard feed bodies and use bounded pinned-public-IP transport; provider/private rights checks still open #93/#97 |
| F-012 | Reader-print/email outputs and fallback | DELIVER | M2 | v1.0.0 | [#7](https://github.com/interzettel/kushluk/issues/7) [#17](https://github.com/interzettel/kushluk/issues/17) | partially-implemented | SMTP implemented; real device acceptance and documented fallbacks pending |
| F-013 | Run-status, retry and local notifications | OPERATE | M2 | v1.0.0 | [#20](https://github.com/interzettel/kushluk/issues/20) [#47](https://github.com/interzettel/kushluk/issues/47) [#17](https://github.com/interzettel/kushluk/issues/17) | partially-implemented | Machine states and manual archive recovery exist; deadline/retry controls pending |
| F-014 | Minimum release/security/packaging | RELEASE | M2 | v1.0.0 | [#54](https://github.com/interzettel/kushluk/issues/54) [#57](https://github.com/interzettel/kushluk/issues/57) [#34](https://github.com/interzettel/kushluk/issues/34) | planned | Signed/tagged release, sample, install, privacy and dependency evidence |
| F-015 | Portable edition/recipe manifest | PUBLISH | M3 | v1.1.0 | [#15](https://github.com/interzettel/kushluk/issues/15) [#33](https://github.com/interzettel/kushluk/issues/33) | planned | Versioned schema without private articles/credentials in shareable recipe |
| F-016 | EPUB export with navigable TOC | DELIVER | M3 | v1.1.0 | [#33](https://github.com/interzettel/kushluk/issues/33) [#7](https://github.com/interzettel/kushluk/issues/7) | partially-implemented | Offline EPUB3 exporter; **W3C EPUBCheck 5.4.0 verified synthetic fixture** via CI #94; actual reader, accessibility, images and language correctness still unverified |
| F-017 | Private optional OPDS/e-reader transport | DELIVER | M3 | v1.1.0 | [#33](https://github.com/interzettel/kushluk/issues/33) [#7](https://github.com/interzettel/kushluk/issues/7) | research | No public private archive, optional auth/service, Kobo/Kindle compatibility tests |
| F-018 | Authorized newsletter discovery/review | SOURCES | M4 | v1.2.0 | [#48](https://github.com/interzettel/kushluk/issues/48) [#4](https://github.com/interzettel/kushluk/issues/4) | planned | Bounded mailbox, explicit user approval, four provider-independent source modes |
| F-019 | Reddit/HN/public research adapters | SOURCES | M4 | v1.2.0 | [#49](https://github.com/interzettel/kushluk/issues/49) [#3](https://github.com/interzettel/kushluk/issues/3) | planned | Rights-compliant APIs, known cost/scope, truthful degradation |
| F-020 | Metadata-first and conditional article fetch | SOURCES | M4 | v1.2.0 | [#49](https://github.com/interzettel/kushluk/issues/49) [#4](https://github.com/interzettel/kushluk/issues/4) | research | Dedup listing first; fetch bodies only with eligibility and proven benefit |
| F-021 | Local persistent feedback/preferences | EDITORIAL | M4 | v1.2.0 | [#19](https://github.com/interzettel/kushluk/issues/19) [#14](https://github.com/interzettel/kushluk/issues/14) | planned | Reversible taste controls; bounded, local and auditable |
| F-022 | Validated article/image rights and crops | TRUST | M5 | v1.3.0 | [#50](https://github.com/interzettel/kushluk/issues/50) [#16](https://github.com/interzettel/kushluk/issues/16) | planned | Image provenance, credit, DPI and safe fallback on invalid assets |
| F-023 | Four-page visual fit regression proof | PUBLISH | M5 | v1.3.0 | [#21](https://github.com/interzettel/kushluk/issues/21) [#51](https://github.com/interzettel/kushluk/issues/51) [#45](https://github.com/interzettel/kushluk/issues/45) | partially-implemented | Automated per-page PDF structure/text-anchor warnings, optional private PNG snapshots; pixel diff and actual legibility review pending |
| F-024 | Editorial layout archetypes and themes | EDITORIAL | M5 | v1.3.0 | [#9](https://github.com/interzettel/kushluk/issues/9) [#51](https://github.com/interzettel/kushluk/issues/51) [#21](https://github.com/interzettel/kushluk/issues/21) | planned | Deterministic monochrome, warm color, rights-safe graphic options |
| F-025 | Agent bounded write/check/repair | OPERATE | M5 | v1.3.0 | [#20](https://github.com/interzettel/kushluk/issues/20) [#21](https://github.com/interzettel/kushluk/issues/21) | research | Provider-neutral, code-led numeric truth and explicit retry budget |
| F-026 | Alternative renderer benchmark | RESEARCH | MX | uncommitted | [#26](https://github.com/interzettel/kushluk/issues/26) [#30](https://github.com/interzettel/kushluk/issues/30) | research | Typst/Chromium/Paged.js only if fixed-content evidence beats baseline |
| F-027 | Fluid digital reading surface | EXPERIENCE | M6 | v1.4.0 | [#33](https://github.com/interzettel/kushluk/issues/33) [#9](https://github.com/interzettel/kushluk/issues/9) | research | Same edition/story IDs; accessible motion optional, actual PDFs verified |
| F-028 | Optional audio/podcast delivery | EXPERIENCE | M6 | v1.4.0 | [#8](https://github.com/interzettel/kushluk/issues/8) | planned | Optional BYO agent/TTS, text provenance, no hosting requirement |
| F-029 | Travel-aware pause/digital-only delivery | OPERATE | M6 | v1.4.0 | [#17](https://github.com/interzettel/kushluk/issues/17) [#47](https://github.com/interzettel/kushluk/issues/47) | planned | Explicit or permissioned travel signal, no surprising home prints |
| F-030 | Optional paper crafts, visual packs and merchandise | EXPERIMENT | MX | uncommitted | [#24](https://github.com/interzettel/kushluk/issues/24) [#25](https://github.com/interzettel/kushluk/issues/25) [#29](https://github.com/interzettel/kushluk/issues/29) [#36](https://github.com/interzettel/kushluk/issues/36) | research | Separate voluntary trial, not launch dependency |
| F-031 | Business/licence/platform options | GOVERNANCE | MX | uncommitted | [#35](https://github.com/interzettel/kushluk/issues/35) [#38](https://github.com/interzettel/kushluk/issues/38) [#40](https://github.com/interzettel/kushluk/issues/40) [#41](https://github.com/interzettel/kushluk/issues/41) | decision-open | Founder-controlled separate policy decisions; MIT today |
| F-032 | Community newsletter and launch film | COMMUNITY | MX | uncommitted | [#11](https://github.com/interzettel/kushluk/issues/11) [#23](https://github.com/interzettel/kushluk/issues/23) [#10](https://github.com/interzettel/kushluk/issues/10) | planned | Contact and claims require actual evidence and owner authorization |

## Epic descriptions

| Epic | Why it exists | Gaining features |
| --- | --- | --- |
| PUBLISH | One truthful, deterministic finite newspaper | F-001, 015, 023 |
| DELIVER | Paper and e-reader/email surfaces from identical edition | F-002, 004, 009, 012, 016, 017 |
| OPERATE | Reliable local unattended morning ownership | F-003, 010, 013, 025, 029 |
| SOURCES | Reader-approved portable intake | F-005, 006, 007, 018, 019, 020 |
| TRUST | Attribution, rights, safe media and privacy | F-011, 022 |
| SETUP | Actual human/agent install path | F-008 |
| RELEASE | Packaging/maintenance contracts | F-014 |
| EDITORIAL | Taste, information hierarchy and legible visual grammar | F-021, 024 |
| EXPERIENCE | Alternative accessible presentation modes | F-027, 028 |
| RESEARCH / EXPERIMENT / GOVERNANCE / COMMUNITY | Separately gated comparisons, optional business and public communication | F-026, 030, 031, 032 |

**Maintenance work and hotfixes are not features simply because they consume PRs.** They link to the affected feature ID, failing test and release version; a bug can cross several epics without creating a new epic. Changes to ownership, legal policy, baseline costs, or default source access require explicit founder approval.

## Updating this catalog

Only change one stable feature ID after an actual agreed product-scope shift. Add issue owner and acceptance evidence; do not close the issue or move its milestone simply to move a percent counter. Record versions explicitly in [RELEASE_PLAN.md](RELEASE_PLAN.md) when a milestone changes, use [WORK_JOURNAL.md](WORK_JOURNAL.md) for dated substantive changes. Current project board remains the existing [Project #3](https://github.com/orgs/interzettel/projects/3); this document does not create another independent ticket tracker.

