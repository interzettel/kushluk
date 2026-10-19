# Owner manifesto — The Paper Is the Product

**Owner direction received 19 October 2026; explicit R5/R6 rulings added later that day.** This document expands [strategic issue #170](https://github.com/interzettel/kushluk/issues/170) for humans and AI contributors. It records the founder's product intent; it does **not** automatically supersede accepted ADRs or grant new source/print permissions. The name is **Kuşluk** with `ş`; `Kushluk` remains the ASCII repository/CLI shorthand where supported.

## Recorded subsequent founder decisions — 19 October 2026

**Direction, not finished implementation.** The founder selected [1A / R5 #162](https://github.com/interzettel/kushluk/issues/162#issuecomment-6277792815): invited private beta requires rights-cleared editorial content, two genuinely distinct same-content art directions, economical grayscale output, real-paper/first-reader evaluation and **explicit founder visual signoff** *in addition* to the existing host/printer/rights criteria. Details are tracked in [RELEASE_PLAN.md](../RELEASE_PLAN.md); this is not approval of rejected PR #153 or a full early studio.

The founder also selected [2A / R6 #171](https://github.com/interzettel/kushluk/issues/171#issuecomment-6277794493): **keep the four-page daily core** and investigate bounded, optional **separate future supplements**. Today's accepted ADR 0013 remains binding; supplement manifests/imposition/archive migration require separate design, proof and a reviewed ADR/requirements change. The founder explicitly kept the Windows printer bridge [PR #152](https://github.com/interzettel/kushluk/pull/152) on hold, closed rejected design [PR #153](https://github.com/interzettel/kushluk/pull/153), and authorized [only non-binding strategy-source extraction from draft #177](https://github.com/interzettel/kushluk/issues/177#issuecomment-6277797384). No three-peer review or Phase I integration is claimed.

## What Kuşluk does

The reader already has enough information arriving in their inbox, timelines, subscriptions, feeds and personal context. The problem is not the shortage of content, but the failure to **read, understand, remember and finish** the material they legitimately choose.

Kuşluk is a **personal publishing engine** for a finite, thoughtfully assembled, visually remarkable edition of the reader's own authorized information. Let their preferred agent help choose, annotate and arrange it. Let the reader restyle it with a prompt, select a design family or rearrange information modules. Deliver a trustworthy, bounded object, not an algorithmically endless app.

If the paper is beautiful enough, the printer waking you up is not a nuisance; it is the beginning of a ritual. Carry it on a commute, finish a piece, put a magazine in your bag, archive an edition, pass around original art where rights permit. Or choose an e-reader or a finite scroll with a clear ending. **The paper is the product; the engine is how we make it.**

The founding line remains: *The internet has already been filtered. You can stop scrolling.* See [#2](https://github.com/interzettel/kushluk/issues/2) and [#6](https://github.com/interzettel/kushluk/issues/6).

## Owner-approved directional principles

1. **Beauty is foundational.** A valid PDF is a necessary technical constraint, not permission to ship an ugly publication. Compelling typography, photography, illustration, editorial narrative, ink, paper and print production craft must be judged by humans on real output.
2. **The reader chooses what matters.** Optional morning intelligence, personally important information, private events/tasks, interesting diversions, sports, original newsletter compilations, professional material. The edition should adapt to the person; no need for daily manual layout work.
3. **Finish, don't linger.** The edition is finite with an intentional end. A four-page daily profile is useful, but not a statement that all future print products must be exactly four pages. Sports inserts, topic supplements, weekend/periodic personal magazines may be longer if proven and explicitly bounded.
4. **Agents are clients, not owners.** Readers should be able to use ChatGPT, Claude, DeepSeek, Hermes, OpenClaw or future compatible agents through neutral documented interfaces, subject to real availability, account entitlement and permissions. No provider is assumed integrated merely by naming it.
5. **Prompt-aided restyling, validated outputs.** A prompt can produce a design/arrangement proposal; all externally generated instructions/artwork must pass license, truth, privacy, safety, font, geometry and reproducibility checks. Ordinary daily delivery must remain dependable if AI is unavailable.
6. **Rights and privacy remain real.** The reader's source authorization does not equal a public redistribution right. Never centralize paid articles or private editions by default, treat an email subscription as blanket copying permission, or expose protected material in shareable recipes. Explicit consent for accessing mailboxes, publishing or printing.
7. **Open useful core and optional physical commerce.** Make the open-source platform independently useful. Commercial opportunity may be unusually good original paper stock, physical print kits, beautiful typography/packs, services or support—not artificial restrictions, personal data resale, compulsory SaaS or “engagement” extraction.
8. **People before vanity metrics.** A thousand GitHub stars may follow good work; they do not prove users finish reading. Track desirability, first successful publication, comprehension and independent authorship with proportionate privacy-safe evidence.

## What this owner statement explicitly reopens

- **ADR 0013:** exactly four logical A4 pages. Owner selected **four-page core + optional finite supplements** as the intended future direction [R6 #171](https://github.com/interzettel/kushluk/issues/171); compare detailed implementation and migration choices while ADR 0013 remains binding. Preserve the existing working 4-page profile and archive migration.
- **#31:** skepticism of runtime AI layout. Discuss [R7 #172](https://github.com/interzettel/kushluk/issues/172): prompt-to-declarative recipe, sandboxed template bundle or curated gallery. Preserve deterministic final validation and fail-safe operations.
- **Existing #14/#33/#15 and #51:** modular controls and reader styles. Discuss [R1 #158](https://github.com/interzettel/kushluk/issues/158) and [R4 #161](https://github.com/interzettel/kushluk/issues/161) for a sane state model; no untrusted executable recipes.
- **ADR 0012 / #44 and #4:** source modes, direct newsletter assembly and any private vs public output rights. Discuss [R8 #173](https://github.com/interzettel/kushluk/issues/173) and preserve explicit approval.
- **#38/#35/#36:** MIT/MPL/AGPL engine rights, neutral SDK, independently licensed original creative goods and brand. Discuss [R10 #175](https://github.com/interzettel/kushluk/issues/175). Existing MIT remains until formal decision.
- **#87/#162:** what should ship first to deliver the promise, and which proofs release gates require. Rebaseline under founder authority through explicit ADR/doc PRs, rather than allowing technical conveniences to dictate product purpose.

The **design council #157** and **R6–R11 issues #171–#176** remain the discussion record. The [published, dated Decision Atlas](https://interzettel.github.io/kushluk/) maps the branches; [IMPACT_MATRIX.md](IMPACT_MATRIX.md) is an impact-hypothesis index. Neither is an accepted ADR.

## The first customer journey worth proving

A reader independently authorizes an inbox/newsletter selection, an RSS or saved-article collection, perhaps a calendar and an optional topic such as sports. They choose **what** enters the edition, **how much** of their morning it deserves, and **how** it should look. They can ask their preferred agent: “Make this weekend's issue quieter, photographic, and add a sports insert.” Kuşluk proposes a lawful content/visual manifest, produces real print-safe pages, validates and archives, and—only with delivery permission—prints on their own mundane home printer. They take it out, read it, reach the end. There is no invisible infinite feed.

**This is a target journey, not an implemented or demonstrated end-to-end feature.** Native email/content authorization, N-page output, prompt-to-recipe, agent contracts and automatic HP paper are unverified or proposed, as tracked in their existing issues.

## What success would look like

- **Desire:** choose the Kuşluk artifact over a trivial browser summary, enjoy the physical paper and keep/carry it.
- **Editorial truth:** read/finish/remember; a source trail is obvious; no fabricated news or unlicensed images.
- **Reader agency:** simple personal module, topic, style and finite reading-budget choices with overrides and privacy controls.
- **Interoperability:** one generic, versioned, read-only-first agent API/CLI test that two independent clients can operate safely; named vendor integrations only after actually proven.
- **Operational quality:** cold-start install and reliable mornings, at-most-once source/print action, clear failure states, no surprise output.
- **Community:** approachable schemas, original recipes, contributors, licensed art/paper goods; no misleading KPI targets.

## Founder operating principle

The founder is the **final editor and accountable decision-maker**, not a project manager distributing narrow permanent roles to three models. ChatGPT, Claude and local DeepSeek V4.1 Flash are **three broad reasoning peers** who can all critique architecture, aesthetics, legal/rights assumptions, product strategy, source credibility, cost and testing. Their independent input is evidence/argument, not a ballot that mechanically outvotes the owner. See [THREE_AI_OPERATING_SYSTEM.md](THREE_AI_OPERATING_SYSTEM.md).

**Important:** issue authoring and this document do **not** assert that any other AI has actually reviewed anything. The laptop-hosted DeepSeek instance is user operated and requires manual integration; remote agents cannot assume local file or model access.

## Not a carte-blanche policy

The existing four-logical-A4-page edition, accepted ADRs, archive compatibility, source rights and release gate bookkeeping are historically true and remain current until an explicitly reviewed change. Future longer paper formats must be tested and versioned rather than unilaterally retrofitted. Do not change the owner's current five-day local WSL2 digital-only trial, activate external inbox reading or spool printers because this document exists.
