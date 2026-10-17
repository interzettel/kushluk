# Roadmap

Kushluk uses iterative vertical slices rather than a long waterfall build.

The operational task source is `WORK_LEDGER.md`; this roadmap describes stage-level sequencing. The **cross-stage 32-feature registry** and proposed semantic-version milestones now live in [FEATURE_CATALOG.md](FEATURE_CATALOG.md) and [RELEASE_PLAN.md](RELEASE_PLAN.md). Neither changes the existing 90 task IDs or evidence gates. The first formal *proposed* prerelease is `v0.2.0-alpha.1` after M1 package/source-preview checks; stable `v1.0.0` is gated by real unattended/paper proof, not a date or a closed-issue count.

## Stage 0 — Define the product

Status: **implementation-ready**

Goal: preserve intent before implementation.

Deliverables:
- Product
- Requirements
- Architecture
- Editorial System
- Design Brief
- Data Map
- Onboarding
- Failure Matrix
- ADRs
- Stage 1 backlog
- Third-party reuse policy
- Open-decisions register

Definition of Done:
A future maintainer/orchestrator can explain what Kushluk is, what it is not, the non-negotiable decisions, and the next executable slice without relying on the founding conversation.

## Stage 1 — Walking skeleton

Status: **ACTIVE — software path exists; real local proof pending**

Goal: make the implemented four-page software path safe, autonomous and ready for real-world validation; do not conflate synthetic CI with actual paper.

Implemented software walking-skeleton path:
- Köln/default weather;
- generic ICS calendar with fixture fallback;
- real RSS/Atom stories;
- canonical candidate and story-cluster models;
- inspectable deterministic ranking;
- publication Markdown/metadata;
- deterministic four-page logical A4 HTML and versioned page identities;
- four-page PDF count, geometry, marker order and editorial cut/retry (not glyph-accurate overflow);
- CUPS capability detection and printing;
- SMTP digital delivery/fallback;
- archive and run summary;
- runtime doctor;
- CI smoke test.

Four-page canonical software migration landed under #45 and A4/single-sided/A3-folded software paths under #46; **remaining software** (ADR 0013/0014):
- full binding/fold/overflow and device-specific print preflight, optional staple marks;
- optional morning-intent input and stable versioned scheduler/orchestrator boundary;
- media asset acquisition/placement layer and richer layout archetypes;
- source/transport exception redaction and hermetic CI smoke tests (#54).

**Remaining physical evidence:** real A4 duplex/A3 paper behavior and unattended host reliability, under #13.

Remaining real-world proof:
- configure a real private calendar/task/mail source;
- run on the chosen local host;
- reach the real printer;
- complete at least five real editions;
- tune from observed failures/read behaviour.

Definition of Done:
One unattended trigger produces a real four-page morning edition with no manual HTML/design editing, the selected A4/A3 print or digital path works in the actual environment, and multiple real editions have been completed.

## Stage 2 — Understand the day

Add:
- richer calendar/task intelligence;
- robust travel-state detection;
- travel-aware destination weather;
- pause/snooze controls;
- stronger device-specific printer-state handling;
- user-facing typed failure notifications.

Definition of Done:
The system makes correct print-vs-digital decisions for normal home and travel scenarios and degrades cleanly when key context is missing.

## Stage 3 — Understand the user

Add:
- durable provider-independent interest model;
- newsletter discovery from a bounded connected-mailbox window;
- per-newsletter source modes: ignore, reference/source, derivative, private direct inclusion;
- connected newsletters;
- RSS bundles;
- X/social connector;
- Reddit/Hacker News;
- lightweight feedback;
- passive privacy-preserving learning.

Definition of Done:
Two materially different user profiles produce meaningfully different editions without recurring manual curation, and an existing newsletter diet can be converted into explicit source configuration without manually entering every subscription.

## Stage 3.5 — Editorial intelligence

Add:
- richer clustering/source diversity;
- claim verification;
- continuity across editions;
- story threads;
- stronger serendipity;
- user-controlled editorial modes.

Definition of Done:
The edition routinely demonstrates useful synthesis rather than feed aggregation.

## Stage 4 — Physical and visual product

Some foundation work begins earlier because four-page migration requires real templates. Stage 4 completes and hardens it.

Add:
- production design system and approved layout-archetype family;
- paper profiles;
- monochrome/colour modes;
- printer compatibility testing;
- refined typography;
- editorial illustration;
- automated image-slot/crop/credit quality tuning;
- external Canva/Adobe template integration only if reliability spikes justify it;
- accessibility and print legibility testing.

Definition of Done:
A run of editions looks unmistakably like the same publication across supported printers/paper profiles.

## Stage 5 — Productise

Add:
- onboarding/configuration;
- newsletter discovery/review UI;
- install packaging;
- connector setup;
- self-hosting docs;
- e-reader surface;
- optional messaging;
- plugin/extension model;
- contributor docs.

Managed cloud, if pursued, receives its own privacy/security/product track.

Definition of Done:
A new user can install Kushluk, connect supported services, review discovered sources, and produce an edition without editing source code.

## Open investigations

Detailed investigation tasks are tracked in `WORK_LEDGER.md`. Current themes include:

- modern newspaper closing/page-production practices and what transfers to Kushluk;
- n8n vs native scheduling vs Apple Shortcuts as orchestration/control surfaces;
- Canva and Adobe structured template population/export reliability;
- image acquisition, placement, rights, and attribution automation;
- exact X/Grok Bot capabilities, costs, and reliability;
- home-printer paper stocks and supported grammage;
- long-term printer upgrade path, especially monochrome laser/duplex;
- newsletter detection precision and provider-specific mail APIs;
- delivery channels beyond email;
- e-reader packaging;
- motion/animated digital edition semantics.
