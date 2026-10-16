# ADR 0013 — Four logical A4 pages, multiple print profiles

**Status:** Accepted

**Supersedes:** ADR 0002

## Context

Kushluk must remain printable on ordinary home and office hardware while still being able to feel like a small folded newspaper when larger paper is available.

Treating A4 and A3 as separate editorial/layout systems would duplicate templates, complicate validation, and make daily generation less reliable.

## Decision

The canonical physical publication model is **four logical DIN A4 pages**.

Layout, editorial fitting, validation, and archive identity operate on those four logical pages. Physical output is handled later by a print/imposition profile.

Initial print profiles are:

1. **A4 Home Printer**
   - two DIN A4 sheets;
   - duplex when supported;
   - logical page order 1, 2, 3, 4;
   - sheets are stacked and may be bound along the left edge;
   - the layout may expose three restrained staple registration marks in the binding margin.

2. **A3 Folded Newspaper**
   - one DIN A3 landscape sheet;
   - duplex;
   - half-folded to A4;
   - outside imposition: page 4 | page 1;
   - inside imposition: page 2 | page 3.

A single-sided fallback may emit the logical pages as separate A4 sheets when duplex is unavailable.

The editorial/layout system must not redesign the edition for each printer profile. Print-specific imposition, rotation, marks, and binding/fold metadata belong to the print layer.

## Rationale

This preserves the lowest-common-denominator requirement of ordinary A4 printers while giving A3-capable users a more newspaper-like physical object.

A canonical logical-page model also keeps templates, layout QA, archive references, and editorial fitting independent from printer hardware.

## Consequences

- Four logical A4 pages become the default edition geometry.
- The renderer produces logical pages before physical imposition.
- The print subsystem needs profile-aware imposition.
- A4 layouts need a safe inner/binding margin that also remains comfortable near the A3 fold.
- Staple/fold marks are optional print metadata, not editorial content.
- A3 gatefold exploration is replaced by the simpler A3 half-fold profile unless revisited later.
- Reading-time and cut policies remain bounded; four pages do not permit unbounded feed expansion.

## Revisit conditions

Revisit if physical tests show that the four-page default is materially too long, home stapling is awkward, printer margins make the shared layout unsafe, or another paper format becomes clearly more useful.
