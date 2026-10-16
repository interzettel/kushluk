# Onboarding

## Purpose

Kushluk onboarding should convert existing user context into a useful first edition with as little manual configuration as possible.

The user should not have to remember every newsletter, feed, or recurring source they already receive. Where the user explicitly connects an account, Kushluk should help discover useful sources and ask how each source should participate in the publication.

Onboarding also needs to establish the physical/delivery environment without turning setup into printer administration.

## Morning and delivery setup

The first-run flow should establish, where relevant:
- configured edition-ready deadline (default 08:00 local time);
- home/default location;
- A4 Home Printer and/or A3 Folded Newspaper profile;
- printer selection/capabilities when a local host can inspect them;
- explicit paper profile when the user cares about stock/colour;
- print vs digital fallback policy;
- travel behaviour (pause, digital-only while away, or another explicit policy);
- optional control surfaces such as Apple Shortcuts;
- languages and initial beats/interests.

The normal daily experience should not require reopening onboarding.

## Newsletter discovery

If the user connects an email account, Kushluk should be able to identify likely newsletters and recurring editorial mail.

The discovery pass should prefer low-risk signals such as:
- sender identity and sending domain;
- recurring sender frequency;
- `List-Unsubscribe`, `List-ID`, and similar mailing-list headers when available;
- repeated subject patterns;
- newsletter-like HTML structure;
- user mailbox labels/categories where exposed by the provider.

The goal is source discovery, not indexing the entire mailbox.

The onboarding UI should present a concise list such as:

> We found 18 recurring newsletters. Which ones should Kushluk use?

For each discovered source, show enough context to make a decision:
- sender/newsletter name;
- sending address/domain;
- approximate frequency;
- most recent delivery;
- a small sample of recent subject lines;
- whether it appears to be a newsletter, transactional mail, or uncertain.

Uncertain classifications should be marked as uncertain rather than silently treated as newsletters.

## Per-newsletter modes

The user should choose how each newsletter may be used.

### Ignore

Do not use this source for Kushluk.

### Reference only

Kushluk may notice that a new issue arrived and use its title/metadata as a candidate signal, but should not ingest the body for editorial synthesis.

Example:

> Dense Discovery published a new issue this morning.

### Derivative / editorial synthesis

Kushluk may read the delivered newsletter locally, extract the useful ideas, and create a shorter Kushluk-native derivative such as:
- a summary;
- key takeaways;
- a “why this matters” note;
- one or more candidate stories;
- a cross-source synthesis;
- a pointer to the original issue.

The generated item should preserve source attribution and a path back to the original newsletter.

### Personal-copy / direct inclusion

For a private/local edition, the user may choose to include material from a newsletter they personally received more directly in their own Kushluk output.

Examples:
- reproduce a user-selected section for personal reading;
- preserve the newsletter's own wording in a private print view;
- print the issue or a chosen portion as part of the user's personal morning packet.

This mode is for the user's private copy of material already delivered to their account. It must not be treated as a blanket right to publicly republish or redistribute the publisher's content.

If Kushluk later offers shared, public, or managed publication features, direct inclusion must be re-evaluated against the source's terms and applicable copyright/licensing rules.

## Recommended onboarding interaction

A possible flow:

1. User connects email.
2. Kushluk performs a local-first newsletter discovery pass.
3. Kushluk shows likely newsletters with confidence and recent examples.
4. User selects newsletters individually or in bulk.
5. For each selected newsletter, the user chooses:
   - Ignore
   - Reference only
   - Derivative / editorial synthesis
   - Personal-copy / direct inclusion
6. User may optionally assign a priority:
   - Core
   - Normal
   - Low
7. Kushluk creates source rules and previews how they will appear in an edition.
8. User confirms.

The onboarding should support a simple bulk default, for example:

> Use all detected newsletters for derivative summaries, except the ones I deselect.

This prevents onboarding from becoming administrative work.

## Runtime behaviour

Newsletter ingestion should be incremental.

Kushluk should:
- process only new or recently relevant issues;
- avoid repeatedly re-reading the full mailbox;
- deduplicate newsletter stories against public-web and social candidates;
- keep source identity and original message references;
- allow one newsletter to contribute zero, one, or multiple candidate items;
- omit newsletter content when nothing is worth printing.

A newsletter subscription is a source signal, not a guaranteed print slot.

## Attribution

Every newsletter-derived Kushluk item should retain:
- newsletter/publication name;
- issue/message identity;
- original sender;
- received/published time where available;
- link back to the original web version or source email where supported;
- transformation mode: reference, derivative, or personal-copy.

## Privacy

Newsletter discovery and parsing belong to the personal data plane.

By default:
- mailbox contents stay local or on user-controlled infrastructure;
- Kushluk should not mirror the entire mailbox into its own database;
- only the minimum needed message metadata/content should be retained;
- remote LLM services should receive only the minimum required content when the user has enabled such processing.

A local model or deterministic parser may be used for discovery/classification where practical.

## Travel-source discovery

Where the user enables relevant connectors, Kushluk may use reliable travel signals from calendar events, train/flight tickets or confirmations in connected mail, and provider/app data exposed through a connector. These signals are used to decide print-vs-digital behaviour and destination context; they are not a reason to build a permanent travel-history database.

## Reconfiguration

Newsletter rules are not permanent.

The user should be able to:
- change a source mode;
- mute a newsletter;
- promote/demote priority;
- remove it from Kushluk;
- rescan for newly subscribed newsletters;
- review sources that have gone inactive;
- change printer/print profile;
- change edition deadline;
- pause/snooze printing;
- choose digital-only for a day;
- reprint the current archived edition.

A periodic lightweight “new sources found” prompt is preferable to forcing the user to repeat onboarding.
