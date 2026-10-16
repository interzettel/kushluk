# Product

## Product statement

Kushluk is a local-first, print-first daily briefing system that creates a small personal newspaper rather than another dashboard.

Its job is to answer:

> **What is worth my attention this morning, given my actual day and my longer-term interests?**

The canonical edition is **four logical DIN A4 pages**, designed as one bounded publication. Ordinary home printers can output it as two duplex A4 sheets; A3-capable printers can output the same pages as one duplex A3 sheet imposed and half-folded to A4. Reading-time targets remain deliberately bounded and will be calibrated through physical trials.

## Primary experience

The intended experience is a **morning ritual, not a dashboard session**. When the configured environment allows it, Kushluk should already be generated and physically available around wake-up/breakfast time, with minimal screen interaction.

By the configured morning deadline, default 08:00 local time:

- if the user is home and printing is healthy, produce the physical edition;
- if printing is unavailable, fail visibly and deliver the edition digitally;
- if the user is travelling, avoid wasting paper and deliver the edition digitally;
- adapt weather and relevant context to the travel destination when reliable context exists;
- allow the user to pick up and optionally staple the A4-home edition, or simply fold/use the A3 edition.

The edition should establish **Today** early: stable commitments and immediate orientation receive priority. The remaining page budget can shift toward **For You** material: editorially selected stories, language material, personal columns, and serendipity. The exact page archetype may vary; the logical four-page geometry does not.

## Brand idea

The product direction is summarized by the idea: **“The internet has already been filtered. You can stop scrolling.”** It is a statement of product intent rather than required printed copy.

## Why print

The product deliberately creates a bounded physical object:
- finite rather than infinite;
- editorial rather than feed-like;
- readable away from notification-heavy screens;
- easy to finish;
- physically memorable and archivable.

Digital surfaces exist to complement print, not to turn Kushluk into another scrolling application.

## Personalisation

Personalisation should come from low-effort or passive signals:
- user-declared interests and beats;
- newsletters and RSS;
- optionally connected social sources such as X;
- calendar and tasks;
- historical editions and lightweight feedback;
- future privacy-preserving reading signals.

Recurring manual tagging, manual exports, daily preference maintenance, or daily manual page assembly are not acceptable foundations.

An optional spoken or typed **morning intent** may influence only the current edition unless the user explicitly saves it as a durable preference.

### Recovering value from existing subscriptions

A user's inbox already contains editorial choices they made outside Kushluk.

When email is explicitly connected, onboarding should help discover likely newsletters and recurring editorial mail, then ask the user how each source should participate in Kushluk.

A newsletter may be:
- ignored;
- used only as a source/candidate signal;
- transformed into Kushluk-native summaries or derivatives;
- included more directly in the user's private personal edition.

The purpose is not generic email summarisation. It is to recover value from newsletters the user already chose to receive but may not have time to read.

See `ONBOARDING.md` and ADR 0012.

## Editorial character

- factual core;
- conversational connective tissue;
- references to previous editions when useful;
- no obligation to manufacture a lead story;
- important world events may override narrow interest relevance;
- deliberate room for useful surprise.

## Language

Language is a user-level preference, not a fixed product choice.

An edition may:
- be entirely in one selected language;
- use different languages by section;
- intentionally mix languages within a section when that serves learning or tone.

Initial development should support English, German, and Turkish well, without hard-coding those as the only possible languages.

## Future surfaces

Planned beyond the current physical-production migration:
- e-reader/e-ink editions;
- richer HTML edition;
- animated editorial stories for capable digital displays;
- extended/special editions beyond the canonical four-page daily;
- messaging delivery;
- optional managed-cloud deployment.

## Non-goals

Kushluk is not:
- a generic autonomous-agent framework;
- a replacement for live travel apps;
- a social network;
- an infinite news feed;
- a surveillance/analytics platform;
- a central behavioural-data business;
- a dashboard that requires the user to sit at a computer.

## Product Definition of Done

A mature Kushluk installation should reliably:
1. understand the day's stable commitments;
2. gather a broad but controlled candidate pool;
3. select rather than merely aggregate;
4. produce an attractive bounded four-page edition by the configured deadline without manual layout work;
5. resolve usable images/assets automatically or safely omit them;
6. print through the configured A4/A3 profile when appropriate and fall back digitally when not;
7. explain material failures;
8. preserve a durable edition archive and run trace;
9. keep personal data under user control by default.
