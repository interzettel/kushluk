# ADR 0012 — Newsletter discovery and ingestion modes

**Status:** Accepted

## Context

Many users already receive high-value editorial material by email but do not consistently open or read it. Asking users to manually recreate this source list inside Kushluk would create unnecessary onboarding work.

Email is also private personal data, so Kushluk must distinguish source discovery, editorial transformation, and direct personal reuse.

## Decision

When the user explicitly connects an email account, Kushluk may perform a local-first discovery pass to identify likely newsletters and recurring editorial mail.

The user must be shown the discovered sources and choose how each may be used.

Supported source modes are:

1. **Ignore**
2. **Reference only**
3. **Derivative / editorial synthesis**
4. **Personal-copy / direct inclusion**

The default recommended bulk mode is derivative/editorial synthesis, subject to user confirmation.

Direct inclusion is a private-personal-use mode for content delivered to that user's account. It must not be interpreted as permission to publicly republish, redistribute, or use the publisher's material as a shared commercial corpus.

## Rationale

This makes onboarding useful immediately while respecting the local-first data model and avoiding repeated manual source configuration.

It also recognises that a newsletter can serve several different roles:
- a signal that something happened;
- an editorial source to summarise;
- an ingredient in cross-source synthesis;
- a private item the user wants to print/read directly.

Those roles should not be conflated.

## Consequences

- Email connectors need newsletter discovery/classification.
- Source configuration needs an explicit per-newsletter mode.
- Newsletter-derived candidates must retain attribution and original-message/source references.
- The system should not mirror the user's entire mailbox.
- Public/shared product modes require a stricter policy than private local printing.
- Newsletter content must be deduplicated against other candidate sources.

## Revisit conditions

Revisit if:
- managed cloud becomes a primary deployment mode;
- Kushluk introduces public/shared editions;
- publisher-specific licensing integrations become available;
- legal/compliance requirements materially change the allowed processing model.
