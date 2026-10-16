# Visual evidence and diagram production

Kuşluk visual work should look like an **editorial system printed on warm paper**, not a glossy product dashboard. Authoritative values come from [DESIGN_BRIEF.md](DESIGN_BRIEF.md) and the current `src/kushluk/templates/edition.html`.

## Design tokens (prototype, currently documented)

| Role | Value |
| --- | --- |
| Paper Cream | `#F3EFE4` |
| Soft Salmon | `#E8C9B8` |
| Morning Yellow | `#F3D77B` |
| Warm Grey | `#9A958D` |
| Ink Black | `#1A1A1A` |

These colors are **visual vocabulary, not evidence status semantics**. Every status graphic must remain understandable in monochrome; use plain labels and accessible titles/descriptions. Restrained emphasis, strong rules, print legibility, and editable SVG are preferred to decorative gradients. Avoid simulated printing results when no physical evidence exists.

## Candidate skills and provenance

The founder requested that diagram and proof methods be explicitly considered:
- **[diagram-design](https://github.com/cathrynlavery/diagram-design)** — a publicly documented skill for branded HTML/SVG diagrams. Confirm install, version, editable profile and output license before using its templates; it is **not a required Kuşluk dependency**.
- **proof visualization / proof-visualization** — desired evidence-first visual inspection method; exact upstream package, skill text and provenance **not yet verified** in Kuşluk or the consulted personal repos. Locate and review the actual user-provided skill before adopting its instructions.
- **Sheeha visualization** — exact name/version/source **unverified**. Preserve this user-supplied name in the discussion; don't silently equate it with a different library or claim the skill is installed.
- Kuşluk-native progress visualization currently uses a **small Python standard-library SVG generator**, derived from [project_health.py](../tools/project_health.py), for a transparent source→output chain.

See [#59](https://github.com/interzettel/kushluk/issues/59) for the skill-provenance investigation and optional improvements. Skill examples remain research inputs, not authoritative product requirements or automatically installed code.

## Visual proof types to prioritize

1. **Architecture:** one readable high-level flow in README; detailed trust/data movement in the architecture docs and decisions. Separate public source research from private reader data and provider calls.
2. **Editorial fixture:** identical content under alternative layouts, paper sizes and color profiles, with original/licensed sample material and logged manifest.
3. **Physical construction:** dimensioned orthographic SVGs, A4/A3 duplex face ordering, fold/bind gutters, exact page imposition and actual photographed print evidence where possible.
4. **Runtime failure:** show source unavailable, PDF overflow, printer offline, email unavailable and recovery transitions, with scrubbed logs.
5. **Progress:** separate checked tasks, evidence-verified gates, decisions still open, and readiness grade. A visually complete chart is not proof of completed work.

## Acceptance

Each visualization needs a question, intended reader, evidence source, date/version, editability and readable alt text. Inspect whether the image contradicts the canonical edition model or subtly implies verified printer results not yet demonstrated. Link accepted diagrams to exact fixtures or tests where possible.
