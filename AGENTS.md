# AGENTS.md

This file is durable project memory for human maintainers and orchestrator agents.

## Mission

Build **Kushluk**, a local-first, print-first personal daily newspaper that turns a user's day, interests, and trusted information sources into a concise morning edition.

The project must remain useful when the original user, original conversation, original LLM provider, or original integration disappears.

## Non-negotiable product principles

1. **Local-first personal data plane.** Personal data remains on infrastructure controlled by the user by default.
2. **Print-first.** The physical morning edition is the primary product surface.
3. **Four logical DIN A4 pages by default.** Treat A4-home and A3-folded output as print/imposition profiles, not separate editorial designs.
4. **08:00 local target.** The edition should be ready by 08:00 local time unless the user configures another time.
5. **Selection over collection.** The product is an editor, not a feed reader.
6. **Reliability before cleverness.** A modest edition that arrives is better than a brilliant edition that fails.
7. **Provider independence.** LLM, search, social, mail, calendar, weather, printer, and delivery systems are adapters.
8. **Deterministic production geometry.** Generative systems may research, select, write, fit copy, and suggest assets; layout geometry, validation, imposition, printing, and archiving must be deterministic.
9. **Graceful degradation.** Missing data removes or replaces a block; it must never create silent holes or corrupt layout.
10. **No recurring manual data labour.** Personalisation may ask for initial preferences, but must not depend on routine manual exports, tagging, or curation.
11. **Serendipity is intentional.** Protect space for material outside the user's existing interest bubble.
12. **Archive is first-class.** Editions and stories need stable identifiers and durable references.
13. **Full automation is the target.** A normal morning run must not require opening a visual editor or manually placing text/images.
14. **Orchestrators are replaceable.** n8n, Apple Shortcuts, OS schedulers, and future services may trigger/control Kushluk but must not own canonical editorial/layout state.

## Documentation precedence

When documents conflict, resolve in this order:

1. Accepted ADRs under `docs/adr/`
2. `docs/REQUIREMENTS.md`
3. `docs/PRODUCT.md`
4. `docs/ARCHITECTURE.md`
5. `docs/EDITORIAL_SYSTEM.md`
6. `docs/DESIGN_BRIEF.md`
7. `docs/WORK_LEDGER.md`
8. `docs/ROADMAP.md` and stage-specific implementation backlog

`docs/CHAT_RECONCILIATION.md` is a non-normative recovery register: it preserves ideas and historical decisions from project chats, including candidates/rejected/superseded items. It never overrides ADRs or canonical requirements.

`docs/OPEN_DECISIONS.md` records unresolved choices and never overrides accepted ADRs.

Do not silently reinterpret a recorded decision. Propose a new ADR when changing architecture or a non-trivial product invariant.

## Working method

Use vertical slices. Prefer a working bicycle over disconnected car parts.

For each stage:
- proceed autonomously on reversible work that does not require a genuine product decision, credentials, or physical access;
- keep repository state clean and avoid abandoned active branches/PRs;
- state the user-visible outcome;
- define acceptance criteria;
- implement the smallest end-to-end path;
- test with real editions;
- record what changed and why;
- only then deepen integrations.

## Current implementation

Stage 1 is active and the software walking skeleton is executable.

Current path:

`Open-Meteo + ICS/fixture calendar + RSS -> canonical candidates -> clustering/ranking -> publication -> current one-page A4 HTML/PDF -> CUPS/SMTP -> archive`

This executable path predates ADR 0013. The accepted target is four logical A4 pages plus A4/A3 print profiles; migration work is tracked in `docs/WORK_LEDGER.md`.

Implemented infrastructure includes:
- typed failures and run summaries;
- deterministic story clustering and ranking;
- optional lead support with no forced lead;
- one-page PDF validation and editorial cut/retry in the current walking skeleton;
- printer capability/duplex detection;
- SMTP delivery and print-failure fallback;
- archive listing;
- runtime doctor;
- CI lint/tests plus an end-to-end smoke test.

Do not claim Stage 1 is finished until a real local print path and repeated real-edition trial have been completed.

## Stage 1 boundary

The implementation must prove:

`real inputs -> normalized candidates -> ranked publication -> four logical A4 pages -> validated output -> selected A4/A3 print profile or digital fallback -> archive`

The original walking-skeleton code path exists. Remaining work includes four-page migration, print-profile imposition, unattended orchestration, media handling, real local connectors, printer access, and repeated usage.

Do not build a broad agent platform before this loop is proven in reality.

## Privacy boundary

Public information may be researched externally. Personal context must not be sent to third-party services unless a connector explicitly needs the minimum required subset and the user has configured it.

A future managed-cloud product is allowed, but it is a separate operating mode with its own privacy/compliance obligations. Do not weaken local-first defaults to make managed hosting easier.

Calendar URLs may contain private tokens; do not persist full private ICS URLs into edition/source metadata.

SMTP credentials belong in environment/runtime secret storage, never Git.

## Upstream reuse

Reuse permissively licensed upstream components when they save time, but:
- preserve Kushluk's product and editorial layer;
- record reused code or substantial adapted material in `THIRD_PARTY_NOTICES.md`;
- preserve required copyright/license notices;
- do not make an upstream project a hard product dependency without an ADR.

See `docs/UPSTREAM_REVIEW.md` before introducing a new upstream dependency.

When a future conversation introduces a consequential idea or decision, classify it and persist it in the appropriate canonical document/ADR or in `docs/CHAT_RECONCILIATION.md`; do not leave durable project state only in chat history.

## Stop conditions / decisions

Do not make choices recorded in `docs/OPEN_DECISIONS.md` on the user's behalf.

External credentials, a local deployment host, and physical printer access are setup prerequisites rather than reasons to redesign the architecture.

## Naming and etymology

- Official public-facing name: **Kushluk** (ASCII). This overrides earlier branding references throughout historical records and templates.
- Repository, Python package and CLI: `kushluk`.
- Explain the Turkish source **kuşluk** only when discussing etymology, not as the product's display name.
- Never silently revert to the old special-character masthead.

## GitHub issue, Project and development traceability (mandatory for maintainers and agents)

Every substantive idea, bug, decision or implementation has an auditable record. **Check for an existing issue before creating another.** Use one solo-steward workflow, not Scrum sprint theater.

For **every new issue**:

1. **Type** — choose a native GitHub Issue Type where supported (Bug, Feature, Task / Research); otherwise encode the category in its title and issue-body `Kind` field. Do not claim a native type was set unless it really was.
2. **Labels** — choose existing workstream, priority and maturity/status labels from the approved taxonomy; if a label does not exist, record the intended label in the issue and in #62 rather than silently omitting it or inventing one.
3. **Assignee** — set `@yigit-denktas` as accountable human steward when creating the issue (unless expressly delegated to a different real account). AI executors belong in the issue description/PR; do not pretend an agent is a GitHub account.
4. **Project and fields** — use the owner's real [**Kushluk GitHub Project #3**](https://github.com/orgs/interzettel/projects/3). Confirm each issue actually belongs to the Project, rather than assuming the board's count is exhaustive. Use its existing **Status** (Backlog, Ready, In progress, In review, Done) as workflow stage; do **not** create a duplicate Stage field. Proposed complementary fields are Priority, Workstream, Maturity and Evidence; their actual options and editing permissions remain under #62. If Project field mutation isn't supported in the current integration, record the missing metadata in the issue and #62 and do not claim it was set.
5. **Milestone** — use an existing verified outcome milestone with exit criteria, or explicitly mark `TBD`; never fabricate a number.
6. **Relationships** — identify `Parent`, `Sub-issues`, `Blocks` and `Blocked by`. Use native GitHub relationships if the integration supports them; always cross-reference issues in Markdown as a fallback.
7. **Development** — once code starts, create a dedicated issue-scoped branch and a PR referencing the issue with `Refs #N` or `Closes #N`; attach PR, CI, review, commit, test or print evidence in both directions. Research-only issues may legitimately have no development branch.
8. **Ledger** — index each new issue exactly once in [master ledger #43](https://github.com/interzettel/kushluk/issues/43), map actionable WORK_LEDGER IDs using `docs/ISSUE_CROSSWALK.md`, and align stage/priority/owner/evidence. No progress without verification.

Use the issue templates, [working method](docs/WORKING_METHOD.md), and [Project configuration issue #62](https://github.com/interzettel/kushluk/issues/62). The *actual board status* is **Backlog → Ready → In progress → In review → Done**; idea/research maturity and parked/rejected disposition are separate meanings, not extra duplicate status fields. The distinctions `proposed`, `accepted`, `implemented`, and `verified` are not interchangeable.

Before **closing or merging**: link the real outcome; confirm actual tests/hardware evidence and issue-to-PR references; use `completed`, `duplicate`, or `not planned` honestly; redirect duplicate issues to one canonical successor and preserve unique findings. After closure update #43, the work ledger / evidence gates only where warranted, and the dated work journal for meaningful events. GitHub Projects fields are not assumed to synchronize with the offline progress report automatically.

A weekly maintenance sweep may reconcile stale metadata, orphaned PRs, duplicate issues and unclear blockers; no recurring automation or bot is implied by this policy. Do not merge security/licensing/privacy-changing PRs merely because automated tests pass.
