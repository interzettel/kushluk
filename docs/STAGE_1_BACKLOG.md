# Stage 1 Backlog — Walking Skeleton

## Stage outcome

Produce a real Kushluk edition end to end with no hand-edited HTML or manual design-tool assembly. The accepted target is four logical DIN A4 pages with profile-specific physical output.

Status: **ACTIVE — software walking skeleton implemented; real-world proof pending**

## Epic 1 — Repository foundation — DONE (v0)

Implemented:
- Python project structure;
- environment configuration;
- local output/archive paths;
- test harness;
- Ruff/pytest CI;
- current official checkout/setup-python Actions;
- end-to-end smoke test;
- manually dispatchable sample-edition workflow;
- runtime `kushluk doctor`.

Remaining work is operational hardening discovered through real installations.

## Epic 2 — Canonical models — DONE (v0)

Implemented:
- SourceRef;
- Candidate;
- StoryCluster;
- PracticalItem;
- Story;
- Publication;
- typed Failure;
- DeliveryResult;
- stable edition identity.

Future:
- explicit long-term metadata schema versioning once archive compatibility needs it.

## Epic 3 — Initial connectors — IN PROGRESS

Implemented:
- Open-Meteo weather;
- generic ICS calendar;
- fixture fallback calendar;
- configurable RSS/Atom connector;
- source-specific typed failure reporting.

Still external/provider-dependent:
- native personal calendar provider auth if preferred over ICS;
- task provider connector;
- optional X/Grok connector.

Acceptance remains: each connector fails independently without breaking unrelated connectors.

## Epic 4 — Normalisation and ranking — IN PROGRESS

Implemented:
- canonical candidate conversion;
- deterministic URL/title story clustering;
- ranking v0;
- source-cluster count;
- inspectable selection reason;
- optional-lead layout support without forcing a lead.

Still requires richer source data:
- stronger source-quality signals;
- meaningful serendipity selection across heterogeneous sources;
- later editorial tuning from real reading behaviour.

## Epic 5 — Publication model — IN PROGRESS

Implemented:
- Markdown-first edition;
- Today / For You surfaces;
- source references;
- edition ID;
- JSON archive metadata;
- run/failure summary.

Future:
- explicit metadata schema version;
- first-class cross-edition/story references;
- QR continuation representation once production design is frozen.

## Epic 6 — Deterministic renderer — IN PROGRESS

Implemented:
- Jinja2 A4 HTML template;
- print CSS;
- balanced layout by default;
- optional lead class;
- monochrome-safe warm editorial v0;
- optional WeasyPrint PDF rendering.

Next migration:
- richer page-archetype family and layout manifest beyond the shipped four-page baseline;
- A4 Home Printer and A3 Folded Newspaper output profiles;
- final production typography after physical tests.

## Epic 7 — Validation and cut loop — DONE (v0)

Implemented:
- canonical publication preflight;
- link checks;
- four-page PDF count, geometry and logical page-order validation;
- deterministic editorial compaction;
- repeated render/check/cut loop;
- malformed output prevented from being sent to the printer;
- overflow debug PDF preservation.

Next validation work must deepen text-fit and asset preflight, binding/fold-safe areas, and imposition regression fixtures beyond the baseline four-page page-ID/count/dimension gate.

## Epic 8 — Printing — SOFTWARE DONE (v0), PHYSICAL TRIAL PENDING

Implemented:
- CUPS/`lp` adapter;
- default/configured printer discovery;
- `lpoptions` capability parsing;
- duplex detection;
- A4 media selection;
- duplex-aware job submission;
- explicit print result;
- validated-PDF requirement before printing.

Pending:
- test against the real home printer;
- map device-specific paper/offline states discovered in that trial.

## Epic 9 — Digital fallback — DONE (v0 implementation)

Implemented:
- generic SMTP email delivery;
- HTML body;
- PDF attachment when available;
- explicit `--email`;
- explicit `--email-on-print-failure`;
- typed email failure result.

Activation requires runtime SMTP configuration, not an architectural decision.

## Epic 10 — Archive — DONE (v0)

Implemented:
- publication Markdown;
- structured JSON metadata;
- HTML copy;
- validated PDF copy when available;
- run/failure/delivery summary;
- stable edition directory;
- `kushluk archive-list`.

Future:
- story-thread lookup and first-class cross-edition references.

## Current executable milestone

`Open-Meteo + ICS/fixture calendar + RSS -> candidates -> clustering/ranking -> Markdown -> A4 HTML -> validated PDF -> CUPS or SMTP -> archive`

This path is exercised by CI, including a walking-skeleton smoke test.

## What now genuinely blocks completion

The physical-format decision is resolved by ADR 0013. Completion now depends on implementation and local evidence:

1. **Four-page baseline completed in PR #80:** production archetype and fit tuning remain #51 and physical acceptance remains #13.
2. **Print profiles:** implement A4 two-sheet duplex and A3 folded-newspaper imposition.
3. **Local runtime host:** decide where the scheduled morning job runs so it can reach the printer and private connectors.
4. **Personal connector setup:** provide/configure real calendar, task, and mail sources.
5. **Delivery credentials:** SMTP config if email fallback is wanted.
6. **Physical trial:** print on the actual printer and run at least five real morning editions.
7. **Production visual lock:** final typography/layout after A4/A3 physical tests.
8. **Full automation layer:** stable trigger boundary, idempotent runs, media assets, and optional orchestration via native scheduler/n8n/Apple Shortcuts.

## Reality trial

After the first successful local print, run at least five real editions before expanding scope aggressively.

Record:
- what was actually read;
- what was consistently ignored;
- layout pain;
- missing practical context;
- source failures;
- generation time;
- printer reliability.

Use this evidence to reprioritise Stage 2.

Cross-stage details, research spikes, automation, template, and image-pipeline work live in `WORK_LEDGER.md`.
