# Editorial System

## Purpose

Kushluk is not a feed aggregator. Its editorial system exists to **select, compress, connect, and omit**.

Core rule:

> **Selection over collection. Reliability before cleverness.**

## Edition geometry

Default:
- four logical DIN A4 pages;
- early-page priority for **Today** practical material;
- remaining page budget for **For You** editorial material;
- one bounded daily edition rather than an expanding feed;
- QR/link escape hatches for depth.

The same logical pages are later imposed by the print layer into A4-home or A3-folded output. Editorial logic does not redesign the edition per printer.

The editorial system cuts content to fit the artifact. The artifact does not expand indefinitely to fit the feed. Story-length classes and slot capacity should be decided before final rendering so copy fitting is an editorial operation, not emergency font shrinking.

## Morning intent

An edition may receive a short spoken or typed **morning intent** before retrieval/ranking. It can promote or de-emphasise topics, add questions to answer, or request a denser/lighter edition for that morning. It is edition-scoped by default and must not silently rewrite the durable user profile.

Morning intent never bypasses verification, privacy boundaries, or required practical content.

## Lead story

A lead is optional.

Use one only when a candidate clearly deserves disproportionate attention. Do not manufacture hierarchy for visual drama.

On quieter days, use a balanced composition.

## Practical priority

On the printed page:

1. calendar / fixed commitments;
2. tasks / user-selected priorities;
3. relevant weather/context;
4. stable travel reminders;
5. editorial stories and personal columns.

### Why calendar/tasks outrank travel details

Calendar and task commitments are relatively stable during the morning. Travel operations are volatile and live apps such as rail/airline tools provide fresher operational updates.

Therefore Kushluk should print the stable part of travel:
- departure reminder;
- trip identity;
- station/airport;
- planned time;
- a prompt or QR to the live source.

It should not pretend that a static page is the best authority for delays, platform changes, gate changes, or cancellations.

## Candidate pool

Possible sources include:
- calendar and tasks;
- weather;
- RSS bundles;
- newsletters;
- X;
- Reddit;
- Hacker News;
- public web/news search;
- email-derived signals;
- user-selected feeds;
- external AI daily briefings as non-authoritative candidate generators.

The pool should be deliberately larger than the printed edition.

## Normalisation

Every candidate should be normalised into a provider-independent schema containing at least:
- candidate ID;
- source;
- source URL/reference;
- publication/retrieval time;
- title;
- canonical topic/story cluster;
- short factual summary;
- source quality / confidence;
- personal relevance reasons;
- timeliness;
- novelty;
- estimated reading cost;
- verification state.

## Deduplication and story clustering

Multiple sources covering the same underlying event should become one editorial story cluster.

Do not reward repetition as importance by default.

Repeated independent coverage may increase confidence or global-materiality signals, but should not consume multiple print slots.

## Ranking dimensions

Initial ranking should be explicit and inspectable.

Dimensions may include:
- relevance to today;
- personal relevance;
- global/material importance;
- freshness;
- source quality;
- novelty;
- continuity with an ongoing story;
- learning value;
- estimated reading effort;
- diversity / serendipity.

Do not bury the ranking logic entirely inside an opaque LLM prompt.

## Beats

Beats are user-selected, not permanent mandatory boxes.

A user may declare interests such as:
- AI;
- architecture;
- geospatial;
- culture;
- finance;
- local city topics;
- science;
- other natural-language interests.

If nothing material happened in a beat, omit it.

Later versions may propose emerging beats based on user behaviour, but must not silently mutate the profile.

## Serendipity

Protect at least one editorial opportunity for something outside the established profile when it is:
- globally important;
- unusually interesting;
- intellectually useful;
- culturally meaningful;
- locally relevant.

Serendipity must not become random filler.

## Tone

**Factual core, conversational wrapper.**

Facts should remain crisp and attributable.

Headlines, transitions, callbacks, and short editorial notes may be conversational, witty, or personal when appropriate.

Do not distort uncertainty or factual precision for personality.

## Language policy

Language is editorially flexible.

Possible modes:
- single-language edition;
- language by section;
- intentional code-switching;
- language-learning micro-sections.

Mixing must have a reason: comprehension, voice, learning, quotation, or context.

## Continuity and archive references

Stories may refer to prior editions.

Example:
> We first covered this in 2026-07-11 · Edition 042.

Digital editions should make such references clickable.

Print editions may use a compact edition/story reference plus QR code.

## Cut policy

When the edition does not fit, cut in this order:

1. exact duplicates;
2. low-value filler;
3. redundant context already stated elsewhere;
4. secondary detail that can move behind a QR/link;
5. lower-ranked optional stories;
6. optional personal columns.

Only then consider modest copy tightening.

Never solve overflow primarily by making text uncomfortably small.

## Media and asset policy

Images are editorial assets, not decoration. A story may carry one or more image candidates with source, rights/usage status, attribution, caption, dimensions, focal point, crop policy, and verification state.

The layout planner may use only assets that satisfy the target slot's print-resolution and crop constraints. If no suitable asset exists, prefer a text-led or illustrated fallback rather than forcing a bad image.

## Failure-aware editing

Unavailable data should not create an empty card/column.

Instead:
- remove the block and reflow;
- substitute a configured fallback;
- display a compact unavailability note when the missing data materially changes the promise.

## Source integrity

An AI-generated briefing or summary is a lead, not evidence.

Material factual claims should be grounded in original or reputable sources whenever practical.
