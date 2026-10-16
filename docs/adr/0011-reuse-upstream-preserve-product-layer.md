# ADR 0011 — Reuse upstream infrastructure, preserve the product layer

**Status:** Accepted

## Context

Several open-source briefing/printing projects already solve parts of ingestion, rendering, validation, PDF generation, or CUPS printing.

## Decision

Kushluk should reuse permissively licensed upstream infrastructure when it clearly saves effort, but should not wholesale fork another product architecture unless there is a compelling reason.

The Kushluk product model, privacy boundary, editorial system, canonical archive, and design direction remain its own.

## Rationale

Reimplementing solved plumbing wastes time; inheriting someone else's product assumptions creates long-term constraints.

## Consequences

Before implementation, perform an upstream file-level review and record incorporated material in `THIRD_PARTY_NOTICES.md`.
