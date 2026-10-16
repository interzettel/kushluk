# Programmatic print inspection and private page proofs

**First implemented QA slice:** [#21](https://github.com/interzettel/kushluk/issues/21), [#45](https://github.com/interzettel/kushluk/issues/45), [#51](https://github.com/interzettel/kushluk/issues/51) · F-023 · **not physical printer verification**.

```bash
# Input can be an existing archive PDF or the synthetic print-proof kit:
kushluk print-proof --output-dir output/print-proof
kushluk inspect-print \
  --pdf output/print-proof/kushluk-proof-a4.pdf \
  --output-dir output/print-review-a4 \
  --rasterize

kushluk inspect-print \
  --pdf output/print-proof/kushluk-proof-a3.pdf \
  --profile a3-folded \
  --output-dir output/print-review-a3 \
  --rasterize --dpi 120
```

This creates a **new, private** evidence directory (refuses to overwrite a previous review) with `inspection.json` and, if the freely available Poppler `pdftoppm` executable is present, one `page-N.png` per A4 logical page or A3 sheet side. Poppler is optional; when not installed, the report honestly reads `renderer_unavailable`, with no fake images. PDF structural page count, dimensions and page-marker/order checks still run using optional `pypdf` (`pip install -e '.[pdf]'`). The inspector calculates, per page, extractable text counts, PDF visitor text anchor positions, out-of-media-box anchors and tiny font fragments; it fingerprints source PDF and any PNG output with SHA-256.

**Limits of automation:** PDF visitor positions are text *anchors*, not pixel-accurate glyph outlines. Text may still overlap, have clipped descenders, inaccessible image alt text or hide text in images. Inspect actual PNG proofs for these cases and repeat on real home printer stock before claiming a reader-visible milestone. A successful report is `automated_checks_passed_pending_visual_review`; it **never sets** `visual_verified` or `physical_verified` true. Generated raster snapshots themselves have not been automatically visually reviewed. For real paper tests, document printer model, tray, media, duplex edge, physical photo and measured defects on [#13](https://github.com/interzettel/kushluk/issues/13).

**Privacy:** Proof PNGs and PDF geometry reports may reveal private edition content. Their directory and output files are locally restricted; never upload them to CI artifacts or GitHub issues without redaction. `pdftoppm` never connects to the network. Avoid using an existing shared folder as the output directory.

The existing `kushluk print-proof` remains the synthetic offline A4/A3 calibration producer; `inspect-print` is an additional read-only inspection phase, not a substituted printer submission or a change to printed composition.
