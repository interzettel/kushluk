# Upstream Review

This document records public projects reviewed as references before Kushluk implementation.
No upstream code is copied into Kushluk by this review.

## Where did the "borrow what from whom" plan go?

**Reconfirmed 17 October 2026.** The original upstream review survived. This is now the
single **transfer register** for competitor/adjacent-product, newsroom, design and
technical inspirations. [Issue #84](https://github.com/interzettel/kushluk/issues/84)
owns ongoing research, current URL/license verification and adopt/defer decisions.
[ADR 0011](adr/0011-reuse-upstream-preserve-product-layer.md) is the accepted
reuse boundary; [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md) records
material actually incorporated. [CHAT_RECONCILIATION.md](CHAT_RECONCILIATION.md)
holds the recovered aesthetic/product history. Dedicated technical experiments
remain with their specialist issues, rather than being duplicated here.

**Evidence categories used below:** *historic review* means already documented
by the project, **not** a current independent source/license recheck.
*Implemented concept* means Kushluk code has comparable behavior written for
Kushluk, **not** that third-party source code was copied. *Candidate* means
research/design inspiration, not an approved implementation requirement.

| Source or reference | Specific inspiration / problem it solves | Transfer stance | Kushluk state and owner |
| --- | --- | --- | --- |
| [Firstlight](https://github.com/cruftbox/firstlight) | Simple weather + RSS acquisition, private/home deployment, printer controls | **ADAPT concepts / REIMPLEMENT adapters**; do not fork the application | Comparable weather/RSS/CUPS stack implemented independently; [#3](https://github.com/interzettel/kushluk/issues/3), [#7](https://github.com/interzettel/kushluk/issues/7), [#12](https://github.com/interzettel/kushluk/issues/12) · historic review |
| [dmthepm Morning Paper](https://github.com/dmthepm/morning-paper) | Reader-owned newsroom files, finite edition, CLI-to-PDF, preferences | **ADAPT editorial state boundary**; never copy user/private data | Canonical files/archive and bounded four-page edition exist; richer durable preferences [#14](https://github.com/interzettel/kushluk/issues/14) · historic review |
| [OpenPaper](https://github.com/falense/openpaper) | Fetch → cache/deduplicate → curate as distinct stages | **ADAPT concepts / REIMPLEMENT independently** | Source connectors and clustering exist; improved cross-provider dedup [#49](https://github.com/interzettel/kushluk/issues/49) · historic review |
| [Hermes Paper Agent](https://github.com/vaelkeep/hermes-paper-agent) | Markdown handoff, generator ↔ press/validator, inspect → repair, provenance and test fixtures | **ADAPT contracts**, **NO CODE COPY** without checking exact license | Four-page renderer/validator/archive in software; fuller repair loop [#21](https://github.com/interzettel/kushluk/issues/21), agent contract [#20](https://github.com/interzettel/kushluk/issues/20) · historic reference, license unverified |
| [drkpxl skills](https://github.com/drkpxl/drkpxl-skills) | Render → inspect → trim → rerender → print; operational proof first | **ADAPT test strategy**, not another program's code | Copy-fit and print proof work underway [#45](https://github.com/interzettel/kushluk/issues/45), [#13](https://github.com/interzettel/kushluk/issues/13) · exact files/license not reverified |
| Karen X. Cheng personal newspaper reference | Newspaper as a cherished personal object rather than a feed | **ADAPT experiential principle**; **DO NOT COPY** creative layouts | Physical morning ritual [#2](https://github.com/interzettel/kushluk/issues/2), [#13](https://github.com/interzettel/kushluk/issues/13) · historical visual reference; original source URL needs verification |
| **Financial Times** / **Le Monde** / **The Guardian** | Paper-led material feel; rigorous hierarchy/grids; restrained editorial energy | **ADAPT principles only**; **IGNORE** brand identity, proprietary copy, assets/fonts | Warm Editorial Computing direction [#9](https://github.com/interzettel/kushluk/issues/9), page archetypes [#51](https://github.com/interzettel/kushluk/issues/51) · candidate inspiration |
| Swiss/European print-grid traditions | Six-column base, asymmetric compositions, restrained typography | **REIMPLEMENT original design system**; do not clone any publication's exact layout | Grid concept documented; full template grammar [#51](https://github.com/interzettel/kushluk/issues/51) · candidate |
| **WoodWing / traditional newsroom workflows** | Page budget/dummy, copy-fit, late changes, deadline and preflight | **ADAPT workflow concepts**, **IGNORE** full newsroom staffing or vendor lock-in | Experimental newsroom practice assessment [#52](https://github.com/interzettel/kushluk/issues/52) · evidence pending |
| **WeasyPrint / Chromium / Paged.js** | Deterministic print renderer vs browser pagination and overflow diagnostics | **BENCHMARK**, not automatic migration | WeasyPrint remains current engine; controlled benchmark [#26](https://github.com/interzettel/kushluk/issues/26) |
| **Canva / Adobe InDesign** | Named text/image slots, repeatable production template and export | **OPTIONAL authoring/adapters only if proven**, no mandatory paid service | Separate vendor automation experiments [#52](https://github.com/interzettel/kushluk/issues/52) |
| **p5.riso / Risograph print aesthetics** | Optional limited ink/halftone treatments on accessible home printers | **ADAPT aesthetic**, not a requirement for a real Riso press | [#21](https://github.com/interzettel/kushluk/issues/21), [#30](https://github.com/interzettel/kushluk/issues/30); production-proof controls still needed |
| **Anthropic launch communication** | Human-first launch narrative and controlled editorial motion | **ADAPT creative discipline**; **IGNORE** copied brand, motion sequences, original assets | [#11](https://github.com/interzettel/kushluk/issues/11), [#9](https://github.com/interzettel/kushluk/issues/9) · conceptual reference |
| **n8n / native launchd / systemd / Apple Shortcuts** | Replaceable triggers and simple unattended local operation | **ADAPT orchestration boundary**, **IGNORE** hosted workflow dependency | Local CLI + launchd/systemd recipes exist; device acceptance/Shortcuts still [#47](https://github.com/interzettel/kushluk/issues/47) |
| **RSSPub / Atlas** | Earlier EPUB/OPDS and research/scoring leads, respectively | **RESEARCH only** | Actual identity, URLs and licenses missing. Do not adopt or make capability claims until [#84](https://github.com/interzettel/kushluk/issues/84) verifies them |

### Decision vocabulary and non-negotiables

- **COPY** = incorporating actual code, text or assets; **none authorized/recorded from
  these reviewed projects**. Requires verified exact source/version/license,
  attribution and updates to `THIRD_PARTY_NOTICES.md` before merge.
- **ADAPT** = transfer a general approach into an original Kushluk architecture or
  design, with source recognition. **REIMPLEMENT** = write independent code
  honoring our local-first data/privacy and rights constraints.
- **BENCHMARK / RESEARCH** = proposed experiment only; require evidence and an
  adopt/defer/reject outcome in the owning issue before scope expansion.
- **IGNORE** = deliberately exclude a pattern (forced SaaS/runtime AI, infinite
  attention feed, wholesale forks, copyrighted layout/text copies, undocumented
  dependencies, mandatory proprietary creative tooling).
- **Differentiation:** Kushluk is a reader-owned, finite, printable daily edition
  generated from the reader's own authorized sources and replaceable AI tools;
  it is not a hosted publisher, content subscription or scraping mirror.
- **Licenses:** historical MIT labels below reflect the earlier review,
  not fresh verification; [#38](https://github.com/interzettel/kushluk/issues/38)
  is a separate **unresolved** Kushluk licensing RFC. Current LICENSE remains MIT.
- Any newly suggested inspiration must identify **which feature**, the relevant
  original source, user-facing advantage, existing capability, intended owner,
  technical/legal cost, and evidence of whether it actually improved the product.

This register is **not an exhaustive competitive market analysis**. Its purpose
is to keep comparisons useful and accountable without converting every aesthetic
reference into an engineering commitment.

---

## Firstlight — cruftbox/firstlight

License: MIT.

Useful patterns:
- Open-Meteo for keyless weather;
- standard RSS feeds for news;
- local Docker/home-server orientation;
- A4/single-page printing;
- archive and print controls.

Kushluk decision:
Use the same general class of boring, replaceable infrastructure, but keep Kushluk's canonical publication model and editorial layer independent.

## Morning Paper — dmthepm/morning-paper

License: MIT.

Useful patterns:
- private newsroom represented as owned files;
- CLI rendering to PDF;
- finite anti-feed framing;
- durable editorial/preferences files.

Kushluk decision:
Reuse the separation of owned editorial state from rendering as a design reference, not as a hard dependency.

## OpenPaper — falense/openpaper

License: MIT.

Useful patterns:
- deterministic source fetchers;
- separate ingestion and curation stages;
- local source/cache/archive directories;
- explicit seen/deduplication state.

Kushluk decision:
Adopt the connector boundary and deterministic fetch-before-curation principle. Do not copy its broadsheet product assumptions.

## Hermes Paper Agent — vaelkeep/hermes-paper-agent

License: verify exact repository license before copying any code.

Useful patterns:
- generator and print engine separated by a markdown publication contract;
- write → check → fix loop before publishing;
- provenance recorded per edition;
- fixtures that allow the pipeline to run before personal connectors are ready.

Kushluk decision:
Adopt the publication-contract and validation-loop concepts. No code is incorporated by this review.

## Earlier chat references needing rediscovery

Two additional names appeared in earlier project research but the exact repositories/URLs and licences were not preserved in the durable project record:
- **RSSPub** — discussed around EPUB/e-ink/OPDS-style delivery ideas;
- **Atlas** — discussed around research/scoring ideas.

Treat these as historical leads only. Rediscover and verify the exact source/licence before copying code, adopting architecture, or adding them to third-party notices as concrete projects.

## Review result

Stage 1 can proceed without an upstream runtime dependency.

The selected implementation strategy is intentionally conventional:

`connectors -> canonical candidates -> ranking -> publication model -> deterministic HTML -> optional PDF -> print adapter -> archive`

This keeps upstream reuse available later at clear seams and avoids inheriting another project's product assumptions.
