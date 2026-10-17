# Home paper format: A4 or US Letter

Kuşluk recommends **DIN A4 (210 × 297 mm / 595.28 × 841.89 pt)** and **US Letter (8.5 × 11 in / 612 × 792 pt)** for ordinary home printing. A3 folding remains an advanced option and is not included in the home-paper selector.

The first-run browser (`kushluk setup-web`) and CLI (`kushluk setup --paper-size a4|letter`) now store a local paper preference. New installations default to A4 **without guessing from IP/location**, and existing schema-v1 profiles missing `paper_size` continue to read as A4 without rewriting the file. The home profile is private, create-only, and carries no print permission.

After creating a profile, use the setup browser’s **printer** step to explicitly change the paper size; the change is bounded to `a4` or `letter`, and retains the selected printer and other home preferences. `KUSHLUK_PAPER_SIZE` can override the saved preference for a running process; unsupported values fail closed.

**Development phase boundary:** the form/persistence work alone does not transform the canonical four-page A4 PDF or certify `media=Letter` output. Before shipping Letter printing, the [tracked issue #129](https://github.com/interzettel/kushluk/issues/129) also requires a genuine Letter MediaBox PDF, matching printer preflight, archived copy/reprint parity and software tests. A choice recorded in setup is **not** physical-print acceptance, permission for an unattended job or a guarantee of printer support.
