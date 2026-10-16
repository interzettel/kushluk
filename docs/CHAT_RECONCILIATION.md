# Project Chat Reconciliation

Last updated: 2026-10-07.

## Purpose

This document reconciles substantive product ideas and decisions recovered from prior Kushluk / Morning Paper project conversations with the repository.

It exists for two reasons:

1. useful decisions and ideas must not live only in chat history;
2. brainstorms must not silently become requirements.

Status labels:

- **CURRENT** — accepted direction and compatible with current ADRs.
- **CANDIDATE** — useful idea worth testing; not yet a product requirement.
- **OPEN** — unresolved question that could materially affect implementation.
- **SUPERSEDED** — previously accepted/explored direction replaced by a later decision.
- **REJECTED** — explicitly abandoned or contrary to current direction.
- **HISTORICAL** — useful context/reference, not a current requirement.

Accepted ADRs and normative requirements still outrank this file.

---

## 1. Name, identity, and product language

### CURRENT — Product name: Kushluk (ASCII display decision, 16 Oct 2026)

The current project/product name is **Kushluk**.

Brand rationale recovered from the conversations:
- "kuşluk vakti" refers to the late-morning period after sunrise and before noon, commonly associated roughly with 09:00–11:00 and especially around 10:00;
- the name connects naturally to morning, observation, a domestic ritual, and the existing bird motif;
- official product uses **Kushluk** with ASCII letters; the Turkish spelling **kuşluk** belongs in etymology only.

### REJECTED — Morning Paper as the final product name

"Morning Paper" was useful as a working descriptor but was abandoned as the final name.

### REJECTED/HISTORICAL — Earlier naming directions

Earlier explorations included:
- Gazette;
- Daybreak Gazette;
- Meridian Gazette;
- Signal Gazette;
- Daily Signal;
- Personal Gazette;
- Morning Edition;
- Daybook;
- Edition.

They are not current naming work.

### CURRENT — Brand promise / conceptual line

The conversation repeatedly converged on the idea:

> **The internet has already been filtered. You can stop scrolling.**

An earlier variant was:

> The internet has already been filtered. You do not need to keep scrolling.

Treat this as brand/product language, not a guaranteed masthead tagline on every edition.

### CURRENT — Warm Editorial Computing

The design/product direction is **Warm Editorial Computing**:
- computation should feel invisible;
- the output should feel like a publication/physical ritual, not an AI interface;
- warm, tactile, literate, contemporary, observant;
- technology disappears into editorial craft.

---

## 2. Physical ritual and morning experience

### CURRENT — The desired ritual

The intended experience is not simply "download a PDF."

The user should be able to:
1. wake up;
2. find the morning edition already generated/printed when the configured environment allows it;
3. pick up the A4 sheets;
4. staple the A4-home edition at the marked binding points when desired;
5. read it away from the screen, typically as a breakfast/morning ritual.

The A3-capable path should produce the same logical edition as a folded newspaper-like object.

### CURRENT — Four logical A4 pages

ADR 0013 is current:
- four logical A4 pages are canonical;
- A4 and A3 are output/imposition profiles;
- the editorial system does not maintain separate A4 and A3 designs.

### CURRENT — A4 Home Printer profile

Recovered physical details:
- two A4 sheets;
- duplex when possible;
- stack in logical reading order;
- optional **three-point staple registration** along the left binding margin;
- shared safe inner gutter must protect text/images from the binding area.

### CURRENT — A3 Folded Newspaper profile

- one A3 landscape sheet;
- duplex;
- outside: `4 | 1`;
- inside: `2 | 3`;
- half-fold to A4.

### SUPERSEDED — A3 105/210/105 gatefold

A previous identity exploration used:
- A3 landscape 420 × 297 mm;
- flaps 105 / 210 / 105 mm;
- closed A4.

That gatefold was useful in the visual exploration but is superseded by ADR 0013's simpler half-fold profile.

### SUPERSEDED — "No binding" as an absolute rule

Earlier brand-board work rejected binding/stacks because the concept was one ultra-thin folded sheet.

The current A4 Home Printer profile explicitly permits simple stapling. The surviving constraint is:
- no fake thick book/magazine stack;
- no invented spine;
- represent the actual thin-sheet construction honestly.

---

## 3. Visual system recovered from chat

### CURRENT — Visual references and exclusions

Direction:
- Le Monde-like compositional discipline;
- Financial Times-like material/tactile identity;
- restrained Guardian-like editorial energy;
- European/Swiss-influenced grid discipline;
- warm post-screen sensibility.

Avoid:
- SaaS dashboard cards;
- glassmorphism;
- neon AI gradients;
- cyberpunk;
- glowing-brain/AI symbolism;
- ornamental fake-vintage newspaper distress;
- logo inflation;
- lifestyle mockup dominance.

### CURRENT — Base grid idea

Use a **six-column editorial base grid** on the logical A4 page as the primary prototype grid.

Columns may be merged into wider story measures; the six-column structure is a compositional framework, not a requirement that every page visibly show six equal text columns.

Physical print tests may tune gutters/margins without discarding the underlying six-column logic.

### CURRENT — Typography relationship

- high-contrast editorial serif for the masthead and major headlines;
- quiet/utilitarian sans for metadata, annotations, utility text;
- small uppercase metadata where appropriate;
- thin rules;
- variable headline scale;
- restrained asymmetry.

### CURRENT — Palette / paper-led colour

Prototype palette:
- Paper Cream — `#F3EFE4`
- Soft Salmon — `#E8C9B8`
- Morning Yellow — `#F3D77B`
- Warm Grey — `#9A958D`
- Ink Black — `#1A1A1A`

Recovered production preference:
- let colour come from **paper stock** where practical;
- black/low-coverage ink on coloured or warm paper is preferable to flooding home-printed pages with background colour;
- monochrome must still work.

### CURRENT — Bird + sun

- bird = observation, messages, curiosity, morning;
- sun = morning, warmth, cycle;
- use sparingly;
- not a mascot or a compulsory badge in every block.

### HISTORICAL/CURRENT — Identity-board presentation grammar

The original brand-system exploration was explicitly an **identity board/system diagram**, not a fake lifestyle newspaper mockup. Useful presentation rules from that phase:
- front-facing/orthographic views where geometry matters;
- show open / partially folded / closed physical states when explaining the object;
- prefer editable SVG/flat geometry for fold and grid diagrams;
- keep lifestyle photography secondary to the system itself.

The exact old gatefold geometry is superseded, but the presentation discipline remains useful for documenting the current A4/A3 profiles.

### CURRENT — Edition identity

Previously proposed/accepted examples remain useful:
- human-facing: `EDITION 0042`;
- machine/archive: `20260920-042` style identity;
- QR is a small functional "escape hatch," not decoration.

---

## 4. Editorial grammar and candidate vocabulary

### CURRENT — Editorial principle

Kushluk is an editor, not a feed:
- select;
- compress;
- connect;
- omit;
- deduplicate;
- verify;
- preserve useful surprise.

### CURRENT — Today-first, For-You-later

The earlier one-sheet grammar "front = Today / back = For You" is physically superseded.

Its editorial principle survives:
- immediate practical orientation comes first;
- personal/editorial curiosity follows;
- page archetypes may vary without losing that reading logic.

### CURRENT — Protected serendipity

Protect space for something outside the user's established profile when it is:
- globally important;
- unusually interesting;
- culturally worthwhile;
- intellectually useful;
- locally relevant.

### CURRENT — Optional lead

Do not manufacture a hero/lead story merely to make the page dramatic.

### CURRENT — Morning intent

A short spoken or typed morning input may:
- emphasize a topic;
- de-emphasize a topic;
- ask a question;
- note what matters specifically today;
- request a lighter/denser edition.

It is edition-scoped unless explicitly saved.

### CANDIDATE — Editorial section/microcopy vocabulary

Earlier conversations produced useful names that may become modules, labels, or rotating section heads:

- **TODAY**
- **FOR YOU**
- **WORTH KNOWING**
- **FROM YESTERDAY**
- **SINCE WE LAST LOOKED**
- **NEARBY**
- **ONE SMALL THING**
- **WORD OF THE DAY**
- **TEN MINUTES**
- **GO DEEPER →**

These are a vocabulary bank, not mandatory recurring boxes.

### CANDIDATE — Additional editorial block types

Ideas discussed but not all promoted to requirements:
- tiny charts / sparklines;
- small maps;
- quotes;
- short exercises;
- finance snippets;
- local-city observations;
- culture item;
- "things you may have missed";
- language-learning micro-sections;
- source-confidence indicators;
- estimated reading time.

These should be tested for editorial value before becoming permanent modules.

---

## 5. Source acquisition and personalisation

### CURRENT — Core source direction

Source families discussed across the project:
- calendar;
- tasks;
- weather;
- RSS/news;
- newsletters/email;
- public web/news research;
- X/social;
- Reddit;
- Hacker News;
- external AI briefings as non-authoritative candidate generators.

### CURRENT — Newsletter discovery

On explicit email connection:
- scan a bounded recent mailbox window;
- identify likely recurring newsletters;
- show them to the user;
- do not silently trust/subscribe them as Kushluk sources;
- support per-source modes:
  - Ignore
  - Reference only
  - Derivative / editorial synthesis
  - Personal-copy / direct inclusion

### CURRENT — No permanent whole-inbox mirror

Mailbox discovery should be incremental/local-first and retain only what is needed for source configuration, provenance, deduplication, and reproducibility.

### CURRENT — Travel/context inference

Travel state may be inferred from reliable signals such as:
- calendar;
- travel documents;
- train/flight tickets in connected mail;
- travel-app/provider signals where a connector safely exposes them.

When the user is away:
- do not waste paper at home by default;
- switch to digital delivery according to user policy;
- adapt weather/context to the reliable destination;
- volatile gate/platform/delay data should still point to live sources.

### CURRENT — Passive learning must stay inspectable

Personalisation should not require recurring manual tagging/exports.

Durable preferences and affinities remain:
- provider-independent;
- inspectable;
- editable/exportable/deletable.

Transient morning intent must not silently become durable preference data.

---

## 6. Full automation and orchestration

### CURRENT — Daily operation should be unattended

The target is a full morning press line:
- gather sources;
- research/verify;
- select;
- write/fit copy;
- resolve images;
- choose an approved layout archetype;
- render;
- validate;
- impose;
- print/deliver;
- archive.

No daily InDesign/Canva page assembly should be required.

### CURRENT — Human governance vs automated run

Earlier conversations correctly preserved human judgement around:
- product direction;
- physical-object decisions;
- editorial voice/taste;
- layout-system design;
- tuning after real reading/printing.

This does **not** mean the human manually lays out each daily edition.

The intended split is:
- humans govern and design the system;
- the normal daily run is unattended.

### CANDIDATE — Local print deployment tactic

Earlier architecture discussion treated driverless/network **CUPS/IPP**, including a container/home-server style deployment, as a viable boring-infrastructure path. This is an implementation option rather than a product invariant and should be tested against the actual printer/network.

### CANDIDATE — Trigger surfaces

Potential triggers/control surfaces:
- OS scheduler (`systemd`, cron, launchd);
- n8n;
- Apple Shortcuts;
- CLI/API;
- future managed scheduler.

### CANDIDATE — Wake/device-connected trigger

A desired interaction discussed in chat:
- generation/printing may be triggered or released after the user wakes;
- or when the relevant computer/printer becomes available/connected.

This needs platform-specific reliability testing; it is not yet a guaranteed trigger contract.

### CURRENT — Apple Shortcuts role

Best initial role:
- Generate now;
- Pause today;
- Digital only today;
- Reprint;
- provide voice morning intent.

Direct unattended iOS AirPrint must be treated as a separate technical investigation from the more controllable Mac/CUPS path.

### CURRENT — Idempotency

Retrying or resuming a morning run must not silently produce duplicate print jobs.

### CANDIDATE — Exact generation start time

An early brainstorm used ~07:30 for a pipeline targeting an 08:00-ready edition.

The actual product rule is:
- ready by the configured deadline, default 08:00;
- exact generation start time is implementation/configuration detail and may vary by source latency and hardware.

---

## 7. Delivery, printer, and failure behaviour

### CURRENT — Printer preflight

Before physical delivery, the system should know as much as the platform exposes about:
- configured/default printer;
- availability;
- duplex capability;
- supported media/paper size;
- selected print profile.

### CURRENT — Paper profiles

Paper stock/colour is explicit user/configuration data.

The printer must not be assumed to correctly infer:
- paper colour;
- stock;
- user intent.

### CANDIDATE — Declared/detected paper mismatch

If the active paper/media configuration is detectably incompatible with the requested profile, Kushluk should:
- avoid knowingly submitting a bad job;
- preserve the edition;
- use the configured digital fallback;
- notify the user with remediation.

Hardware often cannot reliably identify actual paper colour/stock, so this is capability-dependent.

### CURRENT — Digital fallback

Email is the first implemented digital fallback.

Later messaging delivery remains valid; earlier conversations explicitly mentioned WhatsApp as a desired example when an appropriate connector exists.

### CURRENT — Failure transparency

The edition should survive source/print failures where possible:
- missing block -> reflow;
- bad image -> replace or go text-only;
- layout overflow -> cut/switch archetype/rerender;
- print failure -> keep digital edition and archive;
- notify on material failures.

---

## 8. Media and image ideas recovered from chat

### CURRENT — Images are part of the production system

The image problem was explicitly identified as separate from text acquisition.

The system should automate:
- image discovery/download;
- provenance;
- rights/usage status;
- quality/resolution checks;
- focal point;
- crop;
- caption;
- credit;
- placement;
- fallback.

### CURRENT — Do not force imagery

If no suitable image exists:
- use a different image;
- use an approved illustration/diagram where appropriate;
- or render text-led.

A bad image is worse than no image.

### CANDIDATE — Small visual formats

Potential useful visuals:
- maps;
- diagrams;
- small line illustrations;
- halftone treatments;
- tiny charts/sparklines.

They must remain legible on inexpensive printers.

---

## 9. External design tools

### CANDIDATE — Canva templates

Earlier discussion proposed buying/using a Canva newspaper template and filling it automatically.

This remains a technical spike, not the production commitment.

It is acceptable only if automation can reliably control:
- named text slots;
- max copy;
- overflow;
- page order;
- image slots/crops;
- export;
- failure detection.

### CANDIDATE — Adobe / InDesign-like template workflow

Same standard:
- useful for authoring/locking approved designs;
- potentially useful for unattended output only after a successful automation spike;
- do not make daily production depend on manual GUI work.

### CURRENT — Renderer-native fallback

Kushluk must keep a deterministic renderer-native path so the product does not become hostage to a design SaaS or desktop application.

---

## 10. Newspaper workflow ideas to transfer

### CURRENT — Use newsroom concepts, not newsroom staffing

Useful newspaper-production ideas discussed:
- editorial budget/page plan;
- fixed grids;
- story length classes;
- section/page deadlines;
- copy fitting;
- photo/asset desk;
- late-news replacement slots;
- preflight before print;
- edition archive.

Kushluk should encode these as software contracts rather than recreate a large newsroom process.

### CANDIDATE — Late-news slot

Reserve one or more slots/archetype positions that can be replaced late in the run without redesigning every page.

This is worth testing once the layout manifest exists.

---

## 11. Deployment and upstream ideas

### CURRENT — No agent/provider hard dependency

Earlier experiments discussed Hermes/Grok/agent-style orchestration.

Current principle:
- no Hermes, Grok, n8n, OpenAI, or other provider is allowed to become a hard dependency of the canonical publication loop;
- adapters remain replaceable.

### HISTORICAL — Upstream/reference projects

Previously discussed references include:
- Firstlight;
- dmthepm Morning Paper;
- OpenPaper;
- Hermes Paper Agent / Vael;
- drkpxl print workflow;
- Karen X. Cheng's personal newspaper reference.

These are already represented in the upstream/third-party review.

### HISTORICAL / RESEARCH UPDATE (17 Oct 2026) — Earlier reference names

Earlier chat also mentioned:
- **RSSPub** — now matched to [harshit181/RSSPub](https://github.com/harshit181/RSSPub), a Rust EPUB/OPDS and read-later tool with an MIT LICENSE verified in our [source-backed 2026 ecosystem review](research/newspaper-ecosystem-2026-10-17.md). This does not approve a new dependency or full-article copying.
- **Atlas** — the original research/scoring project is **still unidentified**; its exact URL and license remain unknown.

Do not depend on or copy unverified source code. The independent current survey and matrix are recorded under [#84](https://github.com/interzettel/kushluk/issues/84).

---

## 12. Hardware ideas from chat

### CANDIDATE / NOT A PRODUCT DECISION

A previous printer discussion mentioned larger-format devices such as Canon imagePROGRAF TC-series and an Epson SureColor alternative for easier A3/roll workflows.

These are not Kushluk architecture decisions.

The product requirement remains:
- ordinary A4 home printing must remain a first-class path;
- A3 is an enhancement, not a prerequisite.

Printer purchasing recommendations should be revisited against current models, cost, noise, consumables, duplex support, and the user's actual deployment environment.

---

## 13. Project working-method decisions

### CURRENT — Proceed without unnecessary decision gates

Earlier project work explicitly preferred continuing autonomously on reversible implementation/research work and stopping only for genuine user decisions, credentials, or physical access.

Repository hygiene should avoid abandoned active branches/PRs. Historical merged PR records are GitHub records and should not be treated as deletable project state.

### CURRENT — Review upstream before rebuilding plumbing

Before greenfield implementation of generic infrastructure, check the reviewed upstream/reference projects first. Reuse/adapt only at clear seams with licence/provenance discipline; do not wholesale-fork another product's assumptions.

## 14. Reconciliation summary

### Current decisions that must survive future refactors

- Kushluk name and exact casing.
- Local-first, print-first.
- Four logical A4 pages.
- A4 Home Printer + A3 Folded Newspaper profiles.
- Full automation of the normal daily run.
- Human governance of product/design; no daily manual layout.
- Deterministic geometry/render/validation/imposition.
- Optional edition-scoped morning intent.
- Newsletter discovery with explicit per-source modes.
- Today-first / For-You-later editorial priority.
- Protected serendipity.
- Optional lead story.
- Six-column prototype grid.
- Warm Editorial Computing.
- Paper-led colour and monochrome safety.
- Automated media handling with safe text-only fallback.
- Travel-aware print-vs-digital behavior.
- Archive/provenance/inspectability.
- Orchestrators and providers remain replaceable.

### Ideas intentionally left as candidates

- named recurring micro-sections;
- tiny charts/sparklines;
- source-confidence badge;
- per-item reading-time estimates;
- wake/printer-availability trigger semantics;
- Canva/Adobe unattended runtime;
- late-news replaceable slot;
- WhatsApp/messaging delivery;
- specific printer hardware.

These belong in experiments/backlog until evidence promotes them.
