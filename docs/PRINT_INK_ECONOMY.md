# Print ink economy — isolated salvage from rejected design PR #153

**Founder decision 4A:** [#153 closed without merge](https://github.com/interzettel/kushluk/pull/153#issuecomment-6277796359). This narrow change salvages only the measurable output-ink improvement; it does **not** approve the rejected typography, editorial grid, story allocations or sparse exemplar pages. The rejected branch remains historically available for comparison.

For the unchanged production `src/kushluk/templates/edition.html`, keep the warm beige **screen** preview but set actual printed CSS `body` and `.sheet` backgrounds to white. Render the small decorative sun in ink rather than a broad yellow solid fill. This avoids a needless simulated paper-stock wash when using typical white paper. Readers may select actual warm paper stock instead. The original four-page contract and layout/spacing/font rules stay identical.

**Quality boundary:** source-level regression tests confirm the CSS segregation and that the old layout has *not* been silently upgraded to the explicitly rejected #153 design. CI/PDF generation may detect breakage but cannot certify ink consumption, actual printer colors, or aesthetic quality. Before claiming paper ink savings on hardware, compare identical fixture output at 100% size on the real approved printer, capture PDF/print settings and paper details, and obtain explicit owner permission to print. This patch is **not** a standalone beta-quality signoff or evidence for G1–G8.

The default print CSS is not a user-selectable full theme engine. Any colored-background publication mode requires separately proven preference, print-cost disclosure and archived recipe version; no provider or media rights implied. No existing Windows/WSL print trial has been altered.
