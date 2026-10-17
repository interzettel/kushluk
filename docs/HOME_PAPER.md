# Home paper format: A4 or US Letter

Kuşluk recommends **DIN A4 (210 × 297 mm / 595.28 × 841.89 pt)** and **US Letter (8.5 × 11 in / 612 × 792 pt)** for ordinary home printing. A3 folding remains an advanced option and is not included in the home-paper selector.

The first-run browser (`kushluk setup-web`) and CLI (`kushluk setup --paper-size a4|letter`) now store a local paper preference. New installations default to A4 **without guessing from IP/location**, and existing schema-v1 profiles missing `paper_size` continue to read as A4 without rewriting the file. The home profile is private, create-only, and carries no print permission.

After creating a profile, use the setup browser’s **printer** step to explicitly change the paper size; the change is bounded to `a4` or `letter`, and retains the selected printer and other home preferences. `KUSHLUK_PAPER_SIZE` can override the saved preference for a running process; unsupported values fail closed.

## Printable output

For home printing, `generate` and `run` now resolve the saved `paper_size` when no explicit `--print-profile` is supplied:

- `a4` → `a4-home`: four canonical A4 PDF pages.
- `letter` → `letter-home`: a **separate** `edition.letter.pdf` with four real **612 × 792 pt** Letter MediaBox pages, uniformly scaled and centered from the same **unchanged** A4 source.
- Explicit `--print-profile a4-home|letter-home|a3-folded` wins over the saved preference; A3 remains advanced.

Letter uses proportional fit of the complete A4 page, not a reflowed Letter-specific editorial design. That reduces the printed typography slightly; visual/physical legibility must be checked. CUPS submission uses `media=Letter` **only after** validating Letter PDF geometry and confirming the queue advertises Letter (`Letter` or driverless `na_letter_...`), otherwise the job is refused. No printer jobs are run merely by saving the preference.

Archives retain `edition.pdf` (canonical A4) and separately keep `edition.letter.pdf` when Letter was generated. To reprint an old Letter edition, the owner must explicitly select `deliver-archived --print-profile letter-home`, supply a distinct request ID and acknowledge possible duplication; missing or invalid Letter files are refused. Existing A4 archives are never silently converted/reprinted. The printed Letter file is **not** automatically produced from an old A4 archive.

Use `kushluk print-proof` and `kushluk inspect-print --profile letter-home --pdf PATH --output-dir NEW_DIR` for synthetic and structural inspection. The real printer, margins, feed direction, page quality and five unattended mornings remain **unverified** under #129/#13 and G2/G3. No physical acceptance or unattended scheduling permission follows from a setting or CI result.
