# Configurable publishing decision council and agent handoff

**Status:** Proposed process clarification for founder/multi-agent review, 19 October 2026. **Canonical discussion hub:** [#157](https://github.com/interzettel/kushluk/issues/157). **Portfolio owner:** [#43](https://github.com/interzettel/kushluk/issues/43). **Planning owner:** [#87](https://github.com/interzettel/kushluk/issues/87). No new Project board, release gate, accepted ADR, or 90-task completion authority is created by this file.

## Product principle — already established intent

Kuşluk is a local-first, print-first, **configurable personal publishing system**. Readers should be able to select substantive information modules and different art-directed publishing recipes/styles. A reliable normal morning never requires manual layout; a user may configure choices in an editor. There is a finite, rights-aware, beautiful publication and an optional interactive surface with the *same semantic edition identities*. See [#9](https://github.com/interzettel/kushluk/issues/9), [#15](https://github.com/interzettel/kushluk/issues/15), [#21](https://github.com/interzettel/kushluk/issues/21), [#33](https://github.com/interzettel/kushluk/issues/33) and `docs/PRODUCT.md`. The owner **rejected PR #153 visually**; PDF validity is not approval of art direction.

The accepted **four logical A4 pages** (ADR 0013), deterministic production (ADR 0008), source-specific rights, Today-first editorial priorities, finite content and the local private data plane still apply. The proposed design-studio path cannot silently supersede them. Full tile-canvas animation and public recipe exchange remain **future research/features** unless separately accepted.

## Category discipline

- **Actual documentary contradiction:** two accepted ADR 0012 records, owned by [#44](https://github.com/interzettel/kushluk/issues/44). Resolve by reviewing the full text and publishing a maintainer-approved canonical ADR change, not by picking one filename arbitrarily.
- **Roadmap tension:** [F-024](FEATURE_CATALOG.md) and [F-015](FEATURE_CATALOG.md) are post-stable, yet desirable user-selected visual design now defines founder quality for a private beta. **This is a proposed sequencing change**, not a contradiction in accepted ADRs.
- **Code/specification gap:** the renderer has one production HTML template and only three allocation archetypes; the semantic model has four block kinds, one small approved image role, and no saved modular/style arrangements. #9/#21/#33 describe richer ambitions. No missing capability is marked completed merely because its specification exists.
- **Policy boundary to decide:** user ability to hide/priority-pin modules vs Today-first, significant events, protected serendipity and truthful failure/attribution. Separate edition-scoped intent from durable private preferences.
- **Interface boundary to decide:** user-owned private configuration vs safe **declarative shareable** publication recipe vs independently verified issue/archive content; no articles, tokens, calendars or accounts in shared recipes.
- **Aesthetic gate:** passed PDF page/geometry CI is engineering evidence. A separate real human/paper art-direction review is needed for product acceptance but is **not** a new G9 independent delivery gate without explicit governance action.

## Council rooms and work units

| Decision room | Main issue ownership | Questions / dependent atomic work |
| --- | --- | --- |
| [R1 #158](https://github.com/interzettel/kushluk/issues/158) | #14 editorial constitution, #33 UX, #51 semantic blocks | Module precedence, personal/private vs public, per-edition vs durable configuration · [A01 #163](https://github.com/interzettel/kushluk/issues/163), [A05 #167](https://github.com/interzettel/kushluk/issues/167) |
| [R2 #159](https://github.com/interzettel/kushluk/issues/159) | #9 visual system, #21 renderer, #13 physical quality | Genuine visual families, ink and type quality, owner design approval · [A02 #164](https://github.com/interzettel/kushluk/issues/164), [A06 #168](https://github.com/interzettel/kushluk/issues/168) |
| [R3 #160](https://github.com/interzettel/kushluk/issues/160) | #4 source rights, #6 editorial, #50 image pipeline | Substantive copy, safe images, source trail and page-four content · [A01 #163](https://github.com/interzettel/kushluk/issues/163), [A04 #166](https://github.com/interzettel/kushluk/issues/166) |
| [R4 #161](https://github.com/interzettel/kushluk/issues/161) | #15 recipe portability, #33 fluid surfaces, #51 renderer schema | Visual profile, shared semantic identity, safe local-to-shared export · [A03 #165](https://github.com/interzettel/kushluk/issues/165), [A05 #167](https://github.com/interzettel/kushluk/issues/167) |
| [R5 #162](https://github.com/interzettel/kushluk/issues/162) | #87 release plan; #43 portfolio | Revised proposed M2a art-direction slice, feature-ID preservation, founder release decision · [milestone proposal](RELEASE_PLAN.md) |

**Status of atomic units (initial)**: A01 and A06 are READY; A02 is READY for isolated visual experiment; A03 is READY for a non-production schema proposal but source-model code changes are BLOCKED; A04 and A05 are BLOCKED on source decisions for production changes. Branches/PRs must not overlap specified file ownership without coordination. GitHub issue state OPEN ≠ implementation IN PROGRESS.

## Independent-review contract

Multiple AI tools may review, argue and create proposed revisions in the same issue threads. The coordinator must **not** synthesize fictional agreement or attribute one agent's text to another.

Use this per-reviewer comment structure (copy into R1–R5):

```md
## Independent review — [agent or human / model] — [YYYY-MM-DD]
Status recommendation: EVIDENCE READY | CONTESTED | ACCEPT | REJECT | DEFER
Read exact sources: [URLs, branch/commit, relevant issue comments]
Observed facts: [files/tests/real print evidence, distinct from personal interpretation]
Proposed options: A / B / C, including keep-current-baseline
Preferred option + why: [tradeoffs; UX, quality, source rights, privacy, cost, accessibility]
Strongest counterargument / failure mode: [...]
Evidence needed to falsify or accept: [specific fixture, test, human decision]
Impact if accepted: [existing ADR/requirements, F-IDs, milestone, ledger tasks, atomic issue links]
Dissent / questions for founder: [...]
```

Review does not imply authorization to publish, merge, change a licence, contact outsiders, import private source data or use user printers. Comment provenance and **actual independent** positions are required before claiming cross-agent consensus. Founder/maintainers decide consequential art direction, release scope, privacy and normative changes.

## Decision-to-build handoff

1. R1–R5 owner collects attributed alternatives; label contradictions vs gaps vs preferences.
2. Founder records `ACCEPT / ADAPT / DEFER / REJECT` in the owning room, with explicit scope and effects on accepted ADRs.
3. If accepted baseline changes, open a reviewed ADR/doc/release-plan PR following `AGENTS.md` precedence; update #87, #43 and the relevant existing epic. Do not edit accepted documents merely because an AI proposed a better design.
4. Pull READY atomic issues into distinct feature branches. Each deliverable has one source issue owner, review thread, input fixture, measurable proof and negative tests; integration agent checks schema and media rights.
5. Evaluate real physical design approval separately from page-size/clipping CI, and independently from G1–G8 source/security/hardware acceptance.
6. Do **not** update the current user's WSL2 five-morning digital-only pilot checkout or send jobs to their printer when design prototypes are created.

## Example independent task distribution (roles, not identities or assignments)

| Work unit | Proposed primary lane | Required independent challenge | Files |
| --- | --- | --- | --- |
| A01 | Editorial/provenance agent | Rights reviewer | `tests/fixtures/editorial_studio/` |
| A02 | Art-direction/creative coding agent | Layout & print QA reviewer | `tools/visual_studio_spike/` |
| A03 | Data-schema agent | Security/privacy reviewer | `docs/design/VISUAL_PROFILE_RFC.md` |
| A04 | Media rendering agent | Image rights and PDF geometry reviewers | `tools/media_layout_spike/` |
| A05 | UX interaction agent | Accessibility and privacy reviewers | `tools/studio_ui_spike/` |
| A06 | Physical/design QA agent | Founder/novice reader | `docs/design/VISUAL_ACCEPTANCE.md` |

These are **recommended lanes** for agent handoff, not fictitious named workers or assignments. A dedicated agent can own one ready issue without waiting for the five-day reliability trial; other issues remain design-review work until accepted.

## Governance and metrics

The **32 existing stable feature IDs**, 90 original implementation task IDs, G1–G8 independent delivery gates, and historical roadmap stages stay authoritative. The current GitHub catalogue [#43](https://github.com/interzettel/kushluk/issues/43) indexes **78** issue records as observed on 19 October after creating council issues #157–#168; native Project #3 membership/field backfill remains separate work under #65.

**Milestone rebaseline:** [R5 #162](https://github.com/interzettel/kushluk/issues/162) and the adjacent **proposed** changes in [RELEASE_PLAN.md](RELEASE_PLAN.md), [FEATURE_CATALOG.md](FEATURE_CATALOG.md) and [ROADMAP.md](ROADMAP.md). Proposed M2a-design is an **additional discussion checkpoint**, not evidence that an extra product feature or approved milestone already exists.
