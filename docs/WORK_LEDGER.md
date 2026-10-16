# Kuşluk Work Ledger

Last implementation-status review: 2026-10-07.\nIssue/task reconciliation reviewed: 2026-10-16 (no new implementation completion implied).

This is the cross-stage execution ledger for Kuşluk. It records work that is decided, open, blocked, or research-only. It complements `ROADMAP.md`; the roadmap explains sequencing, while this file is the operational source of truth for unfinished work.\n\n**Traceability:** every numbered task in this file is mapped to its primary GitHub implementation/discussion owner in [ISSUE_CROSSWALK.md](ISSUE_CROSSWALK.md) (90 tasks in the 2026-10-16 snapshot). [GitHub master issue #43](https://github.com/interzettel/kushluk/issues/43) is the issue portfolio index; issue creation/closure alone does **not** change the task checkboxes. The first explicitly scoped implementation packages are #45–#52 and document reconciliation is #44. See [STATUS.md](STATUS.md) for independently verified implementation status.\n\n**Known ADR reconciliation issue:** accepted ADR 0015 (replaceable orchestration and agent runtime) must be indexed; two files currently claim accepted ADR 0012. Resolve the duplicate under #44 before treating either variant as a uniquely canonical decision. Do not silently change accepted-ADR text.

## North star

**Kuşluk should be capable of producing and delivering the morning edition without manual editorial layout work.**

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

Workflow tools such as n8n, Apple Shortcuts, systemd/cron, launchd, or a future hosted scheduler may trigger and coordinate the run, but Kuşluk's canonical data model, editorial rules, renderer, validation, archive, and failure semantics remain in the core application.

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
| D-RENDER | DONE | Approved production layouts are deterministic; generative models do not redesign the edition at print time. |
| D-AUTO | DONE | Full automation is the product target; humans may configure/review, but daily layout assembly must not require manual InDesign/Canva work. |

## Immediate execution queue

### P0 — Make the repository internally consistent

- [x] **DOC-01** Record four-page A4/A3 print-profile decision.
- [x] **DOC-02** Record ephemeral morning intent.
- [x] **DOC-03** Update README, Product, Requirements, Architecture, Editorial System, Design Brief, Status, Roadmap, Open Decisions, and Stage 1 backlog so they no longer describe the superseded one-sheet format as canonical.
- [ ] **DOC-04** Keep this ledger current whenever a consequential task is added, completed, blocked, or abandoned.
- [x] **DOC-05** Reconcile prior project-chat decisions/ideas into `CHAT_RECONCILIATION.md` and promote stable items into canonical docs.

### P1 — Four-page production migration

- [ ] **FMT-01** Replace the one-page publication geometry with four logical A4 pages in the canonical publication schema.
  - Acceptance: page identity/order is explicit and archived.
- [ ] **FMT-02** Refactor renderer/templates to produce four logical A4 pages before physical imposition.
  - Acceptance: deterministic HTML/PDF output, no hand editing.
- [ ] **FMT-03** Update validation from “exactly one page” to four-page geometry and per-page overflow checks.
- [ ] **FMT-04** Implement **A4 Home Printer** profile: two A4 sheets, duplex where supported, logical order 1–4.
- [ ] **FMT-05** Add optional three-point staple registration marks inside the safe binding margin.
- [ ] **FMT-06** Implement **A3 Folded Newspaper** imposition: outside `4 | 1`, inside `2 | 3`, then half-fold to A4.
- [ ] **FMT-07** Add single-sided A4 fallback when duplex is unavailable.
- [ ] **FMT-08** Extend printer capability/profile selection without changing editorial layout.
- [ ] **FMT-09** Add print fixtures for margins, fold safety, binding safety, rotation, and duplex edge choice.
- [ ] **FMT-10** Add paper/profile preflight: detect incompatible media where the platform exposes it; otherwise rely on explicit paper-profile configuration without pretending the printer knows stock/colour.

### P1 — Daily full automation

- [ ] **AUT-01** Define a stable run request/response contract so external orchestrators can trigger Kuşluk without knowing internal implementation details.
- [ ] **AUT-02** Add a scheduler-safe CLI/API entrypoint that is idempotent for a date/edition.
- [ ] **AUT-03** Add deadline and “already generated/printed” guards to prevent accidental duplicate morning prints.
- [ ] **AUT-04** Add optional `morning_intent` input to the run model and ranking trace.
- [ ] **AUT-05** Provide an unattended local-host recipe (systemd/cron/launchd) as the baseline.
- [ ] **AUT-06** Prototype an n8n orchestration that calls the same stable Kuşluk run boundary rather than reimplementing editorial logic inside n8n.
- [ ] **AUT-07** Prototype Apple Shortcuts as a trigger/control surface: generate now, pause today, digital-only, reprint, and optional voice morning intent.
- [ ] **AUT-08** Investigate the practical Apple printing path: what can be automated through macOS printing/CUPS versus what AirPrint/iOS requires interactively.
- [ ] **AUT-09** Add run-state observability: started, sources complete, editorial complete, rendered, validated, submitted to printer, printed/failed, digitally delivered.
- [ ] **AUT-10** Add recovery semantics so a failed print never causes editorial regeneration unless explicitly requested.
- [ ] **AUT-11 (RESEARCH)** Test wake-up, local-host-availability, and printer-reachability triggers as optional release signals without weakening the configured deadline.
- [ ] **AUT-12** Keep exact pipeline start time adaptive/configurable; an earlier ~07:30 idea is only a scheduling heuristic for an 08:00-ready edition.
- [ ] **AUT-13 (RESEARCH)** Test driverless/network CUPS/IPP from the chosen local/home-server deployment, including containerised operation only if it simplifies printer reachability rather than complicating it.

### P1 — Source acquisition and editorial input

- [ ] **SRC-01** Implement connected-mail newsletter discovery over a bounded recent window.
- [ ] **SRC-02** Implement per-newsletter modes from ADR 0012.
- [ ] **SRC-03** Add a real task connector.
- [ ] **SRC-04** Add public-web/news research as a provider-independent candidate source.
- [ ] **SRC-05** Add Reddit/Hacker News connectors.
- [ ] **SRC-06** Investigate/implement X/social source adapter without making it a hard dependency.
- [ ] **SRC-07** Preserve original source URLs/message references and timestamps through synthesis.
- [ ] **SRC-08** Strengthen claim verification for material stories.
- [ ] **SRC-09** Deduplicate newsletters, RSS, social, and web coverage into story clusters.
- [ ] **SRC-10** Add travel-context signal adapters from calendar plus connected ticket/confirmation/provider sources without building a permanent travel-history corpus.

### P1 — Automated image acquisition and placement

- [ ] **IMG-01** Add a first-class media asset model: source URL, local/cache path, licence/usage status, attribution, caption, alt text, aspect ratio, dimensions, focal point, crop policy, and verification state.
- [ ] **IMG-02** Build image candidate acquisition for stories from original/reputable sources where lawful and technically available.
- [ ] **IMG-03** Reject hotlink-only, low-resolution, watermarked, duplicate, or unclear-rights assets according to policy.
- [ ] **IMG-04** Add deterministic image placement slots to the layout manifest.
- [ ] **IMG-05** Add automatic crop/focal-point handling with safe fallbacks (`contain`, alternate crop, illustration, or text-only).
- [ ] **IMG-06** Add caption and attribution fitting rules.
- [ ] **IMG-07** Validate effective print resolution and prevent unusable assets from reaching print.
- [ ] **IMG-08** Cache selected assets for reproducible archived editions.
- [ ] **IMG-09** Create a fixture suite covering portrait, landscape, square, tiny, missing, and awkward-focal-point images.

### P1 — Layout grammar and template family

- [ ] **LAY-01** Define semantic content blocks independent of visual template: lead, brief, practical strip, calendar, weather, quote, image story, table, language item, continuation/QR, etc.
- [ ] **LAY-02** Define a finite family of page archetypes rather than one rigid template or free-form generated design.
- [ ] **LAY-03** Define layout-slot capacity rules in characters/lines/aspect ratios so the editor can fit copy before rendering.
- [ ] **LAY-04** Define overflow substitutions: shorten, move, demote, remove image, switch archetype, or cut story.
- [ ] **LAY-05** Separate **layout archetype** from **visual theme/style tokens** so the same editorial structure can support multiple approved looks.
- [ ] **LAY-06** Build at least three production-ready archetypes: balanced day, news-heavy day, and schedule/practical-heavy day.
- [ ] **LAY-07** Add deterministic layout scoring/selection based on the publication manifest.
- [ ] **LAY-08** Freeze approved explorations into HTML/CSS/SVG templates and regression fixtures.
- [ ] **LAY-09** Implement/test the six-column A4 base grid with shared inner binding/fold safety.
- [ ] **LAY-10 (RESEARCH)** Test the recovered editorial vocabulary (`WORTH KNOWING`, `FROM YESTERDAY`, `SINCE WE LAST LOOKED`, `NEARBY`, `ONE SMALL THING`, `WORD OF THE DAY`, `TEN MINUTES`, `GO DEEPER →`) without turning every label into a permanent box.
- [ ] **LAY-11 (RESEARCH)** Test small maps, tiny charts/sparklines, source-confidence display, and per-item reading-time estimates for actual print value.

### P2 — External design-tool integration

- [ ] **DES-EXT-01 (RESEARCH)** Test whether Canva templates can be reliably populated from structured data while preserving exact typography, overflow behaviour, image crops, and four-page ordering.
- [ ] **DES-EXT-02 (RESEARCH)** Test Adobe/Creative Cloud automation paths, including whether an approved InDesign-like template can be populated/exported unattended through available APIs/connectors.
- [ ] **DES-EXT-03** Treat Canva/Adobe as optional authoring/import/export tooling unless the spike proves they can meet unattended deterministic production requirements.
- [ ] **DES-EXT-04** If external templates are used, define a template contract: named text slots, image slots, max copy lengths, style IDs, page IDs, and export profile.
- [ ] **DES-EXT-05** Preserve a renderer-native fallback so Kuşluk is not locked to a design SaaS.

### P2 — Production research

- [ ] **RES-NEWS-01 (RESEARCH)** Document how daily newspapers actually close an edition: editorial budget meeting, page plan/dummy, section deadlines, copy desk, photo desk, page design, late-news replacement, preflight, plate/print deadlines.
- [ ] **RES-NEWS-02 (RESEARCH)** Identify which newsroom practices transfer to Kuşluk: fixed grids, page budgets, story length classes, edition deadlines, late-breaking replacement slots, and preflight.
- [ ] **RES-NEWS-03 (RESEARCH)** Quantify what is automated versus manually paginated in modern newspaper production systems.
- [ ] **RES-AUTO-01 (RESEARCH)** Compare n8n, native OS schedulers, Apple Shortcuts, and a lightweight Kuşluk scheduler for local-first reliability.
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

Kuşluk reaches full-automation v1 when all of the following are true:

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
