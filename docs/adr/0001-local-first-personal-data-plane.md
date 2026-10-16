# ADR 0001 — Local-first personal data plane

**Status:** Accepted

## Context

Kushluk may process calendars, tasks, email signals, interests, travel context, and behavioural preferences. Centralising this data creates unnecessary privacy, security, and compliance exposure.

## Decision

Personal data remains on infrastructure controlled by the user by default.

Supported deployment may include local machines, home servers, or the user's own cloud/VPS.

A future Kushluk-managed cloud mode is allowed only as a clearly separate operating mode with explicit privacy, security, retention, and compliance design.

## Rationale

The product can deliver its core value without owning a central behavioural database.

## Consequences

Connectors and models must work with a local/self-hosted data plane. Cloud convenience must not silently weaken the default.

## Revisit

Revisit only if a specific product capability cannot reasonably exist under this model; document that capability separately.
