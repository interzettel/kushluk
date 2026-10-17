# Kushluk progress and evidence gates

**Snapshot reviewed:** 2026-10-17 · Sources: [WORK_LEDGER.md](WORK_LEDGER.md), [progress-manifest.json](progress-manifest.json)

> These numbers are NOT an overall percentage of product completion. Checked tasks count operational checklist marks only. Delivery gates are independently verified with linked evidence.

## Delivery evidence gates

**0 of 8 verified with evidence (00.00%).** Unverified does not mean failed.

| Gate | State | Owner issues |
| --- | --- | --- |
| G1 — Four-page format | unverified | [#45](https://github.com/interzettel/kushluk/issues/45), [#21](https://github.com/interzettel/kushluk/issues/21) |
| G2 — Real A4/A3 delivery | unverified | [#46](https://github.com/interzettel/kushluk/issues/46), [#7](https://github.com/interzettel/kushluk/issues/7), [#13](https://github.com/interzettel/kushluk/issues/13) |
| G3 — Unattended automation | unverified | [#47](https://github.com/interzettel/kushluk/issues/47), [#17](https://github.com/interzettel/kushluk/issues/17), [#13](https://github.com/interzettel/kushluk/issues/13) |
| G4 — Sources and security | unverified | [#4](https://github.com/interzettel/kushluk/issues/4), [#16](https://github.com/interzettel/kushluk/issues/16), [#48](https://github.com/interzettel/kushluk/issues/48), [#49](https://github.com/interzettel/kushluk/issues/49) |
| G5 — User-owned portability | unverified | [#5](https://github.com/interzettel/kushluk/issues/5), [#15](https://github.com/interzettel/kushluk/issues/15), [#37](https://github.com/interzettel/kushluk/issues/37) |
| G6 — Public trust and legal copy | unverified | [#10](https://github.com/interzettel/kushluk/issues/10), [#34](https://github.com/interzettel/kushluk/issues/34) |
| G7 — Licensing and contribution governance | unverified | [#38](https://github.com/interzettel/kushluk/issues/38), [#54](https://github.com/interzettel/kushluk/issues/54) |
| G8 — Real reader trials | unverified | [#6](https://github.com/interzettel/kushluk/issues/6), [#13](https://github.com/interzettel/kushluk/issues/13) |

## Operational work ledger

**17 of 90 task checkboxes checked (18.89%).** This measures task-record state, not overall readiness.

| Task group | Checked | Total | Progress |
| --- | ---: | ---: | ---: |
| DOC | 4 | 5 | 80.00% |
| FMT | 4 | 10 | 40.00% |
| AUT | 5 | 13 | 38.46% |
| SRC | 0 | 10 | 00.00% |
| IMG | 0 | 9 | 00.00% |
| LAY | 4 | 11 | 36.36% |
| DES-EXT | 0 | 5 | 00.00% |
| RES-NEWS | 0 | 3 | 00.00% |
| RES-AUTO | 0 | 2 | 00.00% |
| RES-IMG | 0 | 1 | 00.00% |
| ED | 0 | 6 | 00.00% |
| UX | 0 | 8 | 00.00% |
| TRIAL | 0 | 7 | 00.00% |
| **TOTAL** | **17** | **90** | **18.89%** |

## Individual tasks

The lines below are generated from WORK_LEDGER.md. Each task ID has a primary owner in [ISSUE_CROSSWALK.md](ISSUE_CROSSWALK.md), not its own invented progress weight.

<details><summary><strong>DOC — 4/5 checked · 80.00%</strong></summary>

| Task ID | Ledger state | Description |
| --- | --- | --- |
| `DOC-01` | CHECKED | Record four-page A4/A3 print-profile decision. |
| `DOC-02` | CHECKED | Record ephemeral morning intent. |
| `DOC-03` | CHECKED | Update README, Product, Requirements, Architecture, Editorial System, Design Brief, Status, Roadmap, Open Decisions, and Stage 1 backlog so they no longer describe the superseded one-sheet format as canonical. |
| `DOC-04` | OPEN | Keep this ledger current whenever a consequential task is added, completed, blocked, or abandoned. |
| `DOC-05` | CHECKED | Reconcile prior project-chat decisions/ideas into `CHAT_RECONCILIATION.md` and promote stable items into canonical docs. |

</details>

<details><summary><strong>FMT — 4/10 checked · 40.00%</strong></summary>

| Task ID | Ledger state | Description |
| --- | --- | --- |
| `FMT-01` | CHECKED | Replace the one-page publication geometry with four logical A4 pages in the canonical publication schema. |
| `FMT-02` | CHECKED | Refactor renderer/templates to produce four logical A4 pages before physical imposition. |
| `FMT-03` | OPEN | Update validation from “exactly one page” to four-page geometry and per-page overflow checks. |
| `FMT-04` | OPEN | Implement **A4 Home Printer** profile: two A4 sheets, duplex where supported, logical order 1–4. |
| `FMT-05` | OPEN | Add optional three-point staple registration marks inside the safe binding margin. |
| `FMT-06` | CHECKED | Implement **A3 Folded Newspaper** imposition: outside `4 \| 1`, inside `2 \| 3`, then half-fold to A4. |
| `FMT-07` | CHECKED | Add single-sided A4 fallback when duplex is unavailable. |
| `FMT-08` | OPEN | Extend printer capability/profile selection without changing editorial layout. |
| `FMT-09` | OPEN | Add print fixtures for margins, fold safety, binding safety, rotation, and duplex edge choice. |
| `FMT-10` | OPEN | Add paper/profile preflight: detect incompatible media where the platform exposes it; otherwise rely on explicit paper-profile configuration without pretending the printer knows stock/colour. |

</details>

<details><summary><strong>AUT — 5/13 checked · 38.46%</strong></summary>

| Task ID | Ledger state | Description |
| --- | --- | --- |
| `AUT-01` | CHECKED | Define a stable run request/response contract so external orchestrators can trigger Kushluk without knowing internal implementation details. |
| `AUT-02` | CHECKED | Add a scheduler-safe CLI/API entrypoint that is idempotent for a date/edition. |
| `AUT-03` | CHECKED | Add deadline and “already generated/printed” guards to prevent accidental duplicate morning prints. |
| `AUT-04` | OPEN | Add optional `morning_intent` input to the run model and ranking trace. |
| `AUT-05` | CHECKED | Provide an unattended local-host recipe (systemd/cron/launchd) as the baseline. |
| `AUT-06` | OPEN | Prototype an n8n orchestration that calls the same stable Kushluk run boundary rather than reimplementing editorial logic inside n8n. |
| `AUT-07` | OPEN | Prototype Apple Shortcuts as a trigger/control surface: generate now, pause today, digital-only, reprint, and optional voice morning intent. |
| `AUT-08` | OPEN | Investigate the practical Apple printing path: what can be automated through macOS printing/CUPS versus what AirPrint/iOS requires interactively. |
| `AUT-09` | OPEN | Add run-state observability: started, sources complete, editorial complete, rendered, validated, submitted to printer, printed/failed, digitally delivered. |
| `AUT-10` | CHECKED | Add recovery semantics so a failed print never causes editorial regeneration unless explicitly requested. |
| `AUT-11` | OPEN | Test wake-up, local-host-availability, and printer-reachability triggers as optional release signals without weakening the configured deadline. |
| `AUT-12` | OPEN | Keep exact pipeline start time adaptive/configurable; an earlier ~07:30 idea is only a scheduling heuristic for an 08:00-ready edition. |
| `AUT-13` | OPEN | Test driverless/network CUPS/IPP from the chosen local/home-server deployment, including containerised operation only if it simplifies printer reachability rather than complicating it. |

</details>

<details><summary><strong>SRC — 0/10 checked · 00.00%</strong></summary>

| Task ID | Ledger state | Description |
| --- | --- | --- |
| `SRC-01` | OPEN | Implement connected-mail newsletter discovery over a bounded recent window. |
| `SRC-02` | OPEN | Implement per-newsletter modes from ADR 0012. |
| `SRC-03` | OPEN | Add a real task connector. |
| `SRC-04` | OPEN | Add public-web/news research as a provider-independent candidate source. |
| `SRC-05` | OPEN | Add Reddit/Hacker News connectors. |
| `SRC-06` | OPEN | Investigate/implement X/social source adapter without making it a hard dependency. |
| `SRC-07` | OPEN | Preserve original source URLs/message references and timestamps through synthesis. |
| `SRC-08` | OPEN | Strengthen claim verification for material stories. |
| `SRC-09` | OPEN | Deduplicate newsletters, RSS, social, and web coverage into story clusters. |
| `SRC-10` | OPEN | Add travel-context signal adapters from calendar plus connected ticket/confirmation/provider sources without building a permanent travel-history corpus. |

</details>

<details><summary><strong>IMG — 0/9 checked · 00.00%</strong></summary>

| Task ID | Ledger state | Description |
| --- | --- | --- |
| `IMG-01` | OPEN | Add a first-class media asset model: source URL, local/cache path, licence/usage status, attribution, caption, alt text, aspect ratio, dimensions, focal point, crop policy, and verification state. |
| `IMG-02` | OPEN | Build image candidate acquisition for stories from original/reputable sources where lawful and technically available. |
| `IMG-03` | OPEN | Reject hotlink-only, low-resolution, watermarked, duplicate, or unclear-rights assets according to policy. |
| `IMG-04` | OPEN | Add deterministic image placement slots to the layout manifest. |
| `IMG-05` | OPEN | Add automatic crop/focal-point handling with safe fallbacks (`contain`, alternate crop, illustration, or text-only). |
| `IMG-06` | OPEN | Add caption and attribution fitting rules. |
| `IMG-07` | OPEN | Validate effective print resolution and prevent unusable assets from reaching print. |
| `IMG-08` | OPEN | Cache selected assets for reproducible archived editions. |
| `IMG-09` | OPEN | Create a fixture suite covering portrait, landscape, square, tiny, missing, and awkward-focal-point images. |

</details>

<details><summary><strong>LAY — 4/11 checked · 36.36%</strong></summary>

| Task ID | Ledger state | Description |
| --- | --- | --- |
| `LAY-01` | OPEN | Define semantic content blocks independent of visual template: lead, brief, practical strip, calendar, weather, quote, image story, table, language item, continuation/QR, etc. |
| `LAY-02` | CHECKED | Define a finite family of page archetypes rather than one rigid template or free-form generated design. |
| `LAY-03` | OPEN | Define layout-slot capacity rules in characters/lines/aspect ratios so the editor can fit copy before rendering. |
| `LAY-04` | CHECKED | Define overflow substitutions: shorten, move, demote, remove image, switch archetype, or cut story. |
| `LAY-05` | CHECKED | Separate **layout archetype** from **visual theme/style tokens** so the same editorial structure can support multiple approved looks. |
| `LAY-06` | OPEN | Build at least three production-ready archetypes: balanced day, news-heavy day, and schedule/practical-heavy day. |
| `LAY-07` | CHECKED | Add deterministic layout scoring/selection based on the publication manifest. |
| `LAY-08` | OPEN | Freeze approved explorations into HTML/CSS/SVG templates and regression fixtures. |
| `LAY-09` | OPEN | Implement/test the six-column A4 base grid with shared inner binding/fold safety. |
| `LAY-10` | OPEN | Test the recovered editorial vocabulary (`WORTH KNOWING`, `FROM YESTERDAY`, `SINCE WE LAST LOOKED`, `NEARBY`, `ONE SMALL THING`, `WORD OF THE DAY`, `TEN MINUTES`, `GO DEEPER →`) without turning every label into a permanent box. |
| `LAY-11` | OPEN | Test small maps, tiny charts/sparklines, source-confidence display, and per-item reading-time estimates for actual print value. |

</details>

<details><summary><strong>DES-EXT — 0/5 checked · 00.00%</strong></summary>

| Task ID | Ledger state | Description |
| --- | --- | --- |
| `DES-EXT-01` | OPEN | Test whether Canva templates can be reliably populated from structured data while preserving exact typography, overflow behaviour, image crops, and four-page ordering. |
| `DES-EXT-02` | OPEN | Test Adobe/Creative Cloud automation paths, including whether an approved InDesign-like template can be populated/exported unattended through available APIs/connectors. |
| `DES-EXT-03` | OPEN | Treat Canva/Adobe as optional authoring/import/export tooling unless the spike proves they can meet unattended deterministic production requirements. |
| `DES-EXT-04` | OPEN | If external templates are used, define a template contract: named text slots, image slots, max copy lengths, style IDs, page IDs, and export profile. |
| `DES-EXT-05` | OPEN | Preserve a renderer-native fallback so Kushluk is not locked to a design SaaS. |

</details>

<details><summary><strong>RES-NEWS — 0/3 checked · 00.00%</strong></summary>

| Task ID | Ledger state | Description |
| --- | --- | --- |
| `RES-NEWS-01` | OPEN | Document how daily newspapers actually close an edition: editorial budget meeting, page plan/dummy, section deadlines, copy desk, photo desk, page design, late-news replacement, preflight, plate/print deadlines. |
| `RES-NEWS-02` | OPEN | Identify which newsroom practices transfer to Kushluk: fixed grids, page budgets, story length classes, edition deadlines, late-breaking replacement slots, and preflight. |
| `RES-NEWS-03` | OPEN | Quantify what is automated versus manually paginated in modern newspaper production systems. |

</details>

<details><summary><strong>RES-AUTO — 0/2 checked · 00.00%</strong></summary>

| Task ID | Ledger state | Description |
| --- | --- | --- |
| `RES-AUTO-01` | OPEN | Compare n8n, native OS schedulers, Apple Shortcuts, and a lightweight Kushluk scheduler for local-first reliability. |
| `RES-AUTO-02` | OPEN | Determine whether the project needs a workflow engine at all, or only a stable trigger/API plus native scheduler. |

</details>

<details><summary><strong>RES-IMG — 0/1 checked · 00.00%</strong></summary>

| Task ID | Ledger state | Description |
| --- | --- | --- |
| `RES-IMG-01` | OPEN | Define a safe image-rights policy for private personal editions versus any future shared/public edition. |

</details>

<details><summary><strong>ED — 0/6 checked · 00.00%</strong></summary>

| Task ID | Ledger state | Description |
| --- | --- | --- |
| `ED-01` | OPEN | Add explicit morning-intent influence to selection explanations. |
| `ED-02` | OPEN | Add durable interest model separate from edition-scoped intent. |
| `ED-03` | OPEN | Add continuity/story threads across editions. |
| `ED-04` | OPEN | Improve serendipity selection using source diversity and learning value. |
| `ED-05` | OPEN | Add user-controlled density modes without changing core layout safety. |
| `ED-06` | OPEN | Add feedback capture that is useful without becoming surveillance telemetry. |

</details>

<details><summary><strong>UX — 0/8 checked · 00.00%</strong></summary>

| Task ID | Ledger state | Description |
| --- | --- | --- |
| `UX-01` | OPEN | Onboarding: printer profile and capabilities. |
| `UX-02` | OPEN | Onboarding: email/newsletter discovery and review. |
| `UX-03` | OPEN | Onboarding: interests/beats and language policy. |
| `UX-04` | OPEN | Controls: pause/snooze, print/digital-only, reprint, generate now. |
| `UX-05` | OPEN | Controls: choose A4 Home Printer / A3 Folded Newspaper when multiple profiles are available. |
| `UX-06` | OPEN | Surface failures in human language without exposing implementation noise. |
| `UX-07` | OPEN | Preserve the physical morning ritual in UX: minimal screen interaction, pick up/optionally staple A4 output, or fold/use A3 output. |
| `UX-08` | OPEN | Add later messaging delivery (WhatsApp was an explicit example in the founding chats) only through an appropriate replaceable connector. |

</details>

<details><summary><strong>TRIAL — 0/7 checked · 00.00%</strong></summary>

| Task ID | Ledger state | Description |
| --- | --- | --- |
| `TRIAL-01` | OPEN | Select the real always-on/local runtime host. |
| `TRIAL-02` | OPEN | Connect the real printer. |
| `TRIAL-03` | OPEN | Configure real calendar/task/mail credentials locally. |
| `TRIAL-04` | OPEN | Print and read at least five consecutive real morning editions. |
| `TRIAL-05` | OPEN | Record generation time, print reliability, what was read, what was ignored, overflow failures, image failures, and binding/fold friction. |
| `TRIAL-06` | OPEN | Run A4 stapled and A3 folded physical comparisons before final typography/layout lock. |
| `TRIAL-07` | OPEN | Use the trial evidence to set final reading-time and density targets. |

</details>

## Update protocol

1. Complete an owning issue's acceptance tests and attach reproducible evidence.
2. Update the relevant WORK_LEDGER.md checkbox only after evidence review.
3. Mark a gate verified only with HTTPS evidence and a verified_on ISO date in progress-manifest.json.
4. Run: python tools/project_health.py write
5. Run: python tools/project_health.py check (enforced by Project health CI).

The [master ledger #43](https://github.com/interzettel/kushluk/issues/43) holds the GitHub issue inventory. This offline report does not fetch live GitHub issue states. [Engineering foundation #54](https://github.com/interzettel/kushluk/issues/54) owns this reporting system.
