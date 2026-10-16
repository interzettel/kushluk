# Full Automation and Production Plan

## Purpose

This document defines the production architecture Kushluk is aiming for. The goal is not “AI generates a pretty PDF.” The goal is a repeatable editorial production line that can run every morning with newsroom-like discipline and without manual page assembly.

## Core principle

Use generative intelligence for **research, selection, synthesis, copy fitting, and editorial judgement**.

Use deterministic software for **geometry, typography rules, image-slot placement, pagination, validation, imposition, printing, and archiving**.

External workflow/design tools may participate, but no external tool should own the canonical publication model.

## Human governance vs unattended operation

Full automation applies to the **normal daily run**. Human judgement remains appropriate for product direction, editorial voice, physical-object choices, template design, source policy, and tuning after real reading/printing. The goal is not to remove design judgement; it is to avoid repeating that judgement manually every morning.

## Target production chain

```text
TRIGGER
  schedule / shortcut / API / CLI
    |
    v
RUN CONTEXT
  date + location + printer profile + optional morning intent
    |
    v
SOURCE INGESTION
  calendar + tasks + weather + RSS + newsletters + web/news + social
    |
    v
NORMALISE / CLUSTER / VERIFY
    |
    v
EDITORIAL BUDGET
  what matters, story classes, length budgets, required practical blocks
    |
    v
ASSET DESK
  image candidates -> rights/quality check -> caption/credit -> crop/focal point
    |
    v
LAYOUT MANIFEST
  chosen archetype + slots + story assignments + asset assignments
    |
    v
DETERMINISTIC RENDERER
  four logical A4 pages
    |
    v
PREFLIGHT
  overflow + typography + links/QR + image resolution + required blocks
    |
    +---- fail -> editorial/layout cut policy -> rerender
    |
    v
IMPOSITION / PRINT PROFILE
  A4 two-sheet duplex + optional staple marks
  OR
  A3 duplex booklet imposition 4|1 / 2|3
    |
    v
DELIVERY
  printer + digital fallback
    |
    v
ARCHIVE / RUN LEDGER
```

## Orchestrator boundary

n8n, Apple Shortcuts, cron/systemd/launchd, or another workflow engine should be treated as **orchestrators**, not as the newspaper itself.

An orchestrator may:
- trigger a run;
- pass morning intent;
- choose generate/print/digital/reprint/pause actions;
- wait for completion;
- route success/failure notifications.

An orchestrator should not:
- contain the ranking rules;
- contain canonical source schemas;
- contain page layout logic;
- manually map every story to coordinates;
- become the only store of edition history;
- hold more private content than necessary.

This keeps the project replaceable and local-first.

## Newspaper-production analogy

Kushluk should model the useful parts of a newsroom:

- **news desk** -> candidate acquisition;
- **editorial meeting/budget** -> decide what deserves space today;
- **copy desk** -> verify, tighten, headline, caption;
- **photo desk** -> source, clear, crop, credit;
- **page plan/dummy** -> choose page archetype and assign stories to slots;
- **page design** -> deterministic templates and style system;
- **late-news desk** -> replace lower-priority slot without redesigning the entire edition;
- **prepress** -> validate geometry, assets, fonts, links, imposition;
- **press** -> printer adapter;
- **morgue/archive** -> edition archive and story continuity.

The key transferable idea is **page budgeting**. Every story gets a size class before layout: for example XS brief, S brief, M story, L story, lead. The renderer should not discover at the last second that arbitrary copy does not fit.

## Layout system

The production design system should have three layers:

1. **Semantic blocks**
   - calendar;
   - weather;
   - task/practical strip;
   - brief;
   - standard story;
   - visual story;
   - lead;
   - quote;
   - language item;
   - table/data block;
   - QR/continuation.

2. **Layout archetypes**
   - balanced;
   - news-heavy;
   - practical/schedule-heavy;
   - later: visual/weekend/special.

3. **Visual themes**
   - typography;
   - rules;
   - spacing;
   - accent/paper assumptions;
   - image treatment.

A theme must not change the semantic meaning of a block. An archetype must not depend on a specific content provider.

## Image pipeline

Images need their own automated production path.

For each candidate image, store:
- source;
- original URL/reference;
- local/cache copy;
- usage/licence state;
- attribution;
- caption;
- alt text;
- width/height;
- effective print resolution;
- aspect ratio;
- focal point;
- allowed crop;
- verification state.

Placement then becomes a constrained problem rather than “ask an AI to drag the image until it looks nice.”

A slot declares:
- aspect-ratio range;
- minimum resolution;
- crop policy;
- caption capacity;
- whether text-only fallback is allowed.

If no safe/useful image fits, the edition should remain text-led rather than forcing a bad image.

## Canva / Adobe role

Canva or Adobe may be useful for:
- creating the initial visual system;
- designing template families;
- importing/exporting approved layouts;
- occasional human refinement;
- generating reference assets.

They should only become part of the unattended daily runtime if a technical spike proves that they can reliably:
- address named text/image slots;
- preserve exact page geometry;
- handle variable copy length;
- control image cropping;
- export predictably;
- run unattended;
- expose failures programmatically.

Until that proof exists, the production renderer remains HTML/CSS/SVG/PDF based.

## Trigger modes recovered from the founding flow

The default contract should be deadline-based, but the orchestration layer may test additional release/trigger signals:
- fixed schedule;
- explicit generate-now action;
- user wake-up automation;
- local host becoming available;
- configured printer becoming reachable.

Wake/device/printer triggers are **capability-dependent experiments**, not requirements that should make the 08:00 deadline unreliable. An early brainstorm used ~07:30 as a possible generation start for an 08:00-ready edition; the exact start time remains configuration/latency logic, not a product invariant.

## Apple integration

Apple Shortcuts is best treated first as a control/trigger surface:
- “Generate Kushluk now.”
- “Use this voice note as morning intent.”
- “Pause today.”
- “Digital only today.”
- “Reprint today’s edition.”

Direct unattended AirPrint behaviour must be verified separately. On a Mac host, the existing CUPS/print path may be a more controllable automation surface than relying on an iPhone/iPad print sheet.

Travel state may be informed by calendar entries, connected travel documents/tickets, or provider/app signals where reliable connectors expose them. When away from the print location, orchestration should default to the configured digital path rather than printing unattended at home.

## Failure policy

A failed source should not kill the whole edition unless it removes essential context.

A failed image should downgrade to another image or text-only.

A failed layout should trigger the cut/switch-archetype loop.

A failed printer should preserve the generated edition and attempt the configured digital fallback.

A retry must be idempotent and must not silently create duplicate print jobs.

## What to test before committing to external tools

1. Can an external design template be filled with variable-length real copy without manual repairs?
2. Can image crops be controlled deterministically?
3. Can it export four pages and the A3 booklet imposition reliably?
4. Can the workflow run without a GUI session?
5. Can failures be detected before printing?
6. Can the whole edition be reproduced later from archived inputs and manifest?

If any answer is no, use the tool for design authoring, not for the daily press line.

## Next work

The detailed queue and acceptance criteria live in `WORK_LEDGER.md`.
