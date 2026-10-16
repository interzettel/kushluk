# Design Brief

## Working direction: Warm Editorial Computing

Kushluk should feel like a small publication made by a thoughtful editor, not a SaaS dashboard printed on paper.

The central tension is:

**digital intelligence → editorial judgment → physical object**

Technology should disappear into editorial craft. The final object should feel finite, calm, warm, tactile, literate, and contemporary.

A recurring product/brand line from the founding conversations is:

> **The internet has already been filtered. You can stop scrolling.**

Treat it as conceptual brand language rather than compulsory masthead copy.

## Identity

The primary identity is the exact wordmark:

**Kushluk**

Use capital **K** followed by lowercase **uşluk**. Preserve the Turkish **ş**. Do not make all-caps `KUSHLUK` the primary masthead.

The name comes from **kuşluk vakti**, the late-morning period after sunrise and before noon; the intended association is roughly the 09:00–11:00 part of the day rather than a fixed clock time. This reinforces the product as a morning ritual, not a generic news app.

The wordmark should use a high-contrast editorial serif with:
- a strong capital K;
- compact editorial proportions;
- enough stroke robustness for inexpensive home printing;
- literary rather than luxury-fashion character.

The production typeface is not yet locked. Prototype layouts may use Playfair Display as a stand-in.

## Bird + sun

Bird and sun are recurring editorial motifs, not a compulsory corporate logo lockup.

- bird: observation, morning, messages, curiosity;
- sun: morning, warmth, cycle.

Use them sparsely. The wordmark must work alone. Do not repeat a bird/yellow-circle badge in every module.

## Palette

Material-first prototype palette:

- Paper Cream — `#F3EFE4`
- Soft Salmon — `#E8C9B8`
- Morning Yellow — `#F3D77B`
- Warm Grey — `#9A958D`
- Ink Black — `#1A1A1A`

Colour should often come from paper stock or a restrained spot-like accent rather than full-page ink coverage. Prefer real coloured/warm stock plus black or low-coverage ink to printing large synthetic background fields on ordinary home printers.

The system must remain legible in monochrome.

## References

The design may learn from:
- **Le Monde** — compositional discipline and calm editorial hierarchy;
- **Financial Times** — material/paper as part of identity;
- **The Guardian** — restrained moments of energy and editorial confidence;
- **Daylight Computer** — warm, tactile, anti-glare, non-sci-fi digital sensibility;
- contemporary tactile/analogue technology branding — used critically, not as lifestyle cosplay;
- independent literary publications and European editorial identity systems.

These are references, not templates to copy.

## Desired feeling

- warm;
- literate;
- tactile;
- contemporary;
- observant;
- slightly idiosyncratic;
- calm enough to read at breakfast;
- designed, but not precious;
- physical without fake vintage affectation.

## Avoid

- glassmorphism;
- neon AI gradients;
- glowing brains;
- cyberpunk motifs;
- generic rounded SaaS cards;
- dashboard density;
- tiny text to force fit;
- fake newsprint distress;
- ornamental nostalgia;
- giant repeated bird/sun badges;
- thick newspaper-stack mockups;
- lifestyle-mockup dominance.

## Typography

Use a serif-led editorial system.

Prototype relationship:
- expressive high-contrast serif for masthead and major headlines;
- highly legible quiet sans for body/utility/metadata where appropriate;
- optional restrained monospace only for identifiers and technical micro-data.

Prototype fonts may use Playfair Display + Inter; final production fonts require later print and licensing review.

Typography should survive inexpensive home printers.

## Layout

Start from newspaper/magazine composition rather than a component-card UI.

Use:
- a **six-column editorial base grid** on each logical A4 page; merge columns into wider measures as needed rather than forcing six visible text columns;
- a rigorous underlying column grid;
- thin rules;
- variable headline scale;
- asymmetry in moderation;
- active negative space;
- restrained photography/illustration;
- small uppercase metadata.

The page should feel composed by an editor, not assembled from dashboard cards.

Across the four logical pages:
- page 1 should provide calm arrival and immediate orientation;
- practical material should appear early and remain easy to scan;
- later pages may carry denser editorial stories, language material, illustration, and curiosity;
- no page is required to manufacture a hero story;
- page archetypes may vary while the underlying grid and design tokens remain stable.

## Morning ritual

The designed object is part of a domestic morning ritual: the edition should be ready with as little screen interaction as possible, picked up from the printer, optionally stapled in the A4-home profile, and read away from notifications. Computation should feel invisible at the point of reading.

## Physical object

ADR 0013 fixes the canonical edition as **four logical DIN A4 pages** and separates editorial layout from physical imposition.

Supported production directions:
- **A4 Home Printer** — two A4 sheets, preferably duplex, stacked and optionally bound along the left edge; three restrained staple registration marks may be exposed inside the binding margin.
- **A3 Folded Newspaper** — one A3 landscape sheet, duplex, imposed as outside `4 | 1` and inside `2 | 3`, then half-folded to A4.
- **Single-sided fallback** — logical A4 pages emitted separately when duplex is unavailable.

The design must reserve a safe inner margin that works both beside the A4 binding edge and near the A3 fold. Print-profile marks belong to the print layer, not editorial content.

Mockups should represent the actual thin-sheet construction; do not invent a book spine or thick bound magazine.

## Paper as a design token

Potential home-printable profiles:
- standard white;
- warm white / cream;
- recycled grey;
- pale yellow;
- pale pink / salmon;
- pale orange.

Prefer uncoated, matte, slightly fibrous stock. Real paper variation is welcome; fake vintage texture is not.

The printer is not assumed to detect paper colour or stock automatically.

## Imagery and illustration

Photography should be observational rather than advertising-like:
- streets;
- architecture;
- public transport;
- neighbourhood life;
- people at a distance;
- landscapes;
- objects;
- maps.

Preferred illustration vocabulary:
- small editorial line drawings;
- natural-history-like bird studies;
- diagrams;
- maps;
- restrained collage;
- halftone;
- simple iconography.

Do not rely on photoreal AI imagery as the default aesthetic.

## Edition identity and digital escape hatches

Edition identity should be stable and collectible, for example:

`20 SEP 2026 · EDITION 0042`

Machine/archive identity:

`20260920-042`

QR codes are functional escape hatches for deeper/live material, not decoration. Keep them small and attributable.

## Prototype and identity-board guidance

When documenting the physical/design system, prefer system-board clarity over lifestyle mockup theatre:
- use front-facing/orthographic diagrams for page, fold, grid, and binding geometry;
- show relevant open / partial / closed states when explaining a physical transformation;
- keep fold/grid diagrams editable as SVG or equivalent vector geometry;
- let the design system dominate the board rather than coffee-cup/desk photography.

Use generative visual tools to explore directions, but freeze approved layouts into deterministic HTML/CSS/SVG templates.

Daily generation must fill a design system; it must not redesign the publication from scratch each morning.

The production system should separate **semantic blocks**, **layout archetypes**, and **visual themes**. Canva/Adobe/InDesign-style tools may be used to author or test templates, but unattended daily production should depend on them only if a technical spike proves exact slot addressing, overflow control, crop control, predictable export, and programmatic failure reporting.
