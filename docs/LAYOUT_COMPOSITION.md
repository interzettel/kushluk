# Editorial composition engine — three deterministic print archetypes

**Owner:** [#51](https://github.com/interzettel/kushluk/issues/51) · **Renderer integration:** [#21](https://github.com/interzettel/kushluk/issues/21) · **Status:** software implementation and synthetic proofs; layout signoff/physical print remain open.

## Architecture

Kushluk still has four logical A4 page kinds — front, day, stories and sources — regardless of theme or A4/A3 printer imposition. The composition engine converts a ranked canonical story/practical pool into typed `CompositionBlock` references and `SlotBudget` values. Blocks reference immutable source IDs or practical indices; they do not duplicate the source content. Every edition records its `archetype` and `composition_decisions` in its publication metadata.

Theme remains separate: printer geometry/imposition has no input to `choose_archetype`; paper and ink color tokens live in the print template. There is **no runtime AI placement** or paid orchestration dependency.

## Archetypes and capacities

| Archetype | Front-page practical | Front-page leads | Day-page practical | Day-page leads | Page-3 briefs | Front lead-deck limit |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Balanced | 3 | 1 | 3 | 0 | 3 | 500 characters |
| News-heavy | 2 | 2 | 4 | 0 | 3 | 270 characters |
| Practical-heavy | 4 | 0 | 4 | 1 | 3 | 360 characters |

All story headlines have a 96-character maximum, source display names 55 characters, page-3 brief decks 330 characters. Each practical item has label/value/detail ceilings of 34/70/118 characters. **These are copy estimates**, not guarantees that every font, script, emoji, image or print driver will fit; the PDF and WeasyPrint geometry checks remain a separate stage.

A six-column A4 CSS grid places practical entries in half-width cells. News-heavy covers can place two short leads side by side. The page kinds, logical numbering, masthead and paper-profile handling are shared across archetypes.

### Image capacity

`SlotBudget` includes `image_slots` and `caption_chars`, but all production archetypes currently permit **zero images**. This is intentional: #50 has not yet delivered a rights-checked, locally preflighted raster/vector asset path. Unverified image references are stripped from printable selections and logged as a `remove_image` decision. There is no automatic remote image fetch, fake image, or undeclared attribution. Aspect-ratio and caption/crop resolution work remains open under LAY-03/#50.

## Deterministic archetype choice

The production pipeline requests `archetype="auto"`. A practical-heavy edition is selected when it has at least four practical items and at least two more practical items than valid stories; news-heavy is selected when at least three valid stories compete with at most two practical items; otherwise balanced is used. No randomness, font shrinkage, private user profiling or printer settings alter this decision. The edition's audit includes a `select_archetype` decision with the manifest counts.

**Compatibility boundary:** direct `build_publication(...)` calls retain **balanced** as the default for previously accepted EPUB/archived-client page expectations. Callers may explicitly select an archetype; the actual `run_pipeline` passes `auto`.

## Copy-fitting and source integrity

- Important calendar/task entries outrank optional weather/reminder entries. If required entries exceed that archetype's capacity, composition **fails** rather than silently deleting commitments.
- The composer normalizes whitespace and shortens at a word boundary where feasible; very long unspaced German/Turkish words are bounded character-by-character and CSS `overflow-wrap:anywhere` prevents widening the page.
- Overflowing front practical entries `move` to the day page. Secondary news `demote` to briefs. A missing headline or unattributed candidate is `replace`d by the next ranked eligible story, when one exists. Lower-ranked optional extras are explicitly `omit`ted once the edition is full.
- Included source IDs and source URLs survive fitting. The source index follows included/printed stories; omitted items are retained only as reason-coded composition decisions.
- Rendering never silently expands the paper length: each variant must pass four-page A4 validation and visible text safe-bound checks before a test declares the PDF valid.

**Known limits:** capacity budgets are rough Unicode character counts, not true glyph-width/line-break predictions. The inspector detects fragmented pages, text outside the print-safe rectangle, article/footer intersection and a minimum text-size floor; it is not yet a full optical/content-clipping analyzer (FMT-03 remains open). Six-column binding/fold physical proof (LAY-09), image budgets beyond zero (LAY-03), editorial approval of frozen layout variants (LAY-08) and production validation (LAY-06) require further work.

## Generate the comparison kit

```bash
python -m pip install -e '.[dev,pdf]'
python -m tools.layout_compare --output-dir output/layout-compare
```

One frozen **synthetic** edition (same date, title/deck inputs and edition ID) is forced into balanced, news-heavy and practical-heavy archetypes. The output contains three HTML layouts, **three A4 PDFs** and `comparison.json` with per-page slot contracts, omitted/replaced/shortened item decisions, page counts, geometry findings and legibility-floor evidence. The PDFs are not physically printed; no feeds/calendar/printer/SMTP are contacted. Current CI creates downloadable layout-comparison ZIP artifacts for **both macOS architectures**; approved visual baselines and physical sample photos are a future acceptance step.

The manual review should inspect each four-page PDF at actual print size, compare front-page hierarchy, check a long German and Turkish headline, readability, page count/footers, margins and source attributions, then feed concrete adjustments back to #51. No software score is a substitute for that judgment.
