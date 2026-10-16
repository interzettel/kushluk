# ADR 0012 — Newsletter discovery is explicit and source-specific

**Status:** Accepted

## Context

Users often already subscribe to newsletters that match their interests, but many issues go unread. Email can therefore provide high-value editorial inputs without requiring the user to manually recreate their information diet inside Kushluk.

However, mailbox access is sensitive, newsletter detection is imperfect, and receiving an email does not imply a general right to redistribute its full contents.

## Decision

When email is explicitly connected, Kushluk may discover likely newsletters from a bounded recent mailbox window inside the user's personal data plane.

Kushluk must present discovered newsletters to the user and require a source-specific mode before using them persistently:

- Ignore
- Use as a source
- Create derivatives
- Direct personal inclusion

Newly discovered newsletters may be suggested later, but must not silently become trusted editorial sources.

Direct personal inclusion is intended for the user's private edition and does not imply permission for public redistribution.

## Rationale

This gives Kushluk a low-effort, high-signal onboarding path based on sources the user already selected in real life, while preserving consent and avoiding blanket mailbox ingestion.

## Consequences

- email connectors need newsletter-detection/classification capability;
- newsletter preferences become durable local configuration;
- newsletter source records need attribution and original-message/source references;
- public/shared modes need stricter reuse rules than private local editions;
- the entire mailbox must not become a permanent Kushluk corpus by default.

## Revisit

Revisit if email providers expose a safer structured newsletter/subscription inventory, or if managed-cloud deployment changes the privacy model.
