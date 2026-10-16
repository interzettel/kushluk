# Kushluk Status

Last implementation verification snapshot: 2026-10-17 (four-page software CI; physical trials outstanding).
Documentation and issue inventory reviewed: 2026-10-16.

**Status caveat:** the 2026-10-16 inventory did **not** independently rerun CI or physical print tests. Do not infer four-page migration, unattended execution, or real-reader trials are done from the new planning issues. [#43](https://github.com/interzettel/kushluk/issues/43) indexes all issues, and [ISSUE_CROSSWALK.md](ISSUE_CROSSWALK.md) maps the 90 existing work-ledger tasks to accountable issues. Execution blockers have dedicated issues: [#45](https://github.com/interzettel/kushluk/issues/45) format, [#46](https://github.com/interzettel/kushluk/issues/46) print profiles, [#47](https://github.com/interzettel/kushluk/issues/47) local scheduler/retries. Docs/ADR ambiguities: [#44](https://github.com/interzettel/kushluk/issues/44).

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

`weather + calendar + RSS -> candidates -> clustering/ranking -> publication -> four-page A4 HTML -> validated PDF -> print/email -> archive`

Available commands:

- `kushluk doctor`
- `kushluk generate --no-pdf`
- `kushluk generate`
- `kushluk generate --print`
- `kushluk generate --email`
- `kushluk generate --print --email-on-print-failure`
- `kushluk archive-list`

## Implemented

### Inputs
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
- CI tests, linting and walking-skeleton smoke test.

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

The next implementation slice is not another format decision. It is:

1. implement and test A4 and A3 physical print profiles against the four-page source;
2. establish real print profile preflight;
3. establish the stable unattended-run boundary;
4. add asset/media handling;
5. run real physical editions.

See `docs/WORK_LEDGER.md` for task IDs and acceptance criteria.
