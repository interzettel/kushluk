# Real-device acceptance and private proof receipts

**Owners:** [#13](https://github.com/interzettel/kushluk/issues/13), [#33](https://github.com/interzettel/kushluk/issues/33), [#46](https://github.com/interzettel/kushluk/issues/46), [#47](https://github.com/interzettel/kushluk/issues/47) · **Critical stable-release gates remain open**.

This is the **operator-side** stage after the software's synthetic PDFs/EPUB and automated validators. GitHub Actions runners do not have your actual printer, e-reader or sleeping home host. No CI can certify ink alignment, real page turn behavior, disconnected Wi-Fi, hardware sleep/wake, or a five-morning unattended run just by making PDFs.

## 1 — Print real A4, record the exact PDF fingerprint

```bash
kushluk print-proof --output-dir output/print-proof
kushluk inspect-print --pdf output/print-proof/kushluk-proof-a4.pdf \
  --output-dir output/proof-a4-visual --rasterize

# After a real A4 print, physical inspection and a local photograph:
kushluk record-field-proof --kind paper-a4 \
  --artifact output/print-proof/kushluk-proof-a4.pdf \
  --inspection output/proof-a4-visual/inspection.json \
  --evidence ~/Pictures/kushluk-real-a4-photo.jpg \
  --device "Exact printer model / driver / paper stock" \
  --operator "Operator initials" \
  --observations "Page order, duplex long-edge, margins, clips, text and print contrast observed" \
  --result pass --acknowledge-direct-observation \
  --output ~/kushluk-private-evidence/a4-field-001.json
```

On real A3 duplex/fold-capable hardware use `--kind paper-a3`, the **actual A3 booklet PDF**, and `--inspection` from `kushluk inspect-print --profile a3-folded`. Confirm outside **4|1**, inside **2|3**, short-edge orientation, fold and trim; record failures as `--result fail` with actual observed defects and retry only after corrective action. Do not mark A3 supported when testing only A4.

To record a **passing** physical sample, the CLI requires one or more evidence files, explicit direct-observation attestation, and a structurally clean PDF inspection JSON with the **same PDF SHA-256**. It records only evidence hashes and byte counts, never copies photographs into Git or transmits anything. If the printer failed, `--result fail` records the failure without a false positive.

## 2 — Test EPUB on a real reader

First run the independent [W3C EPUBCheck conformance job](../.github/workflows/epub-conformance.yml) or install EPUBCheck locally. A successful validator checks **file conformance**, not device layout, page navigation, screen-reader semantics or publisher-content rights.

```bash
kushluk export-epub --date 2026-10-17 \
  --output ~/Books/kushluk-test.epub

# Inspect the EPUB on a specific Kindle/Kobo/KOReader or equivalent, then:
kushluk record-field-proof --kind epub-reader \
  --artifact ~/Books/kushluk-test.epub \
  --evidence ~/Pictures/kushluk-real-reader-photo.jpg \
  --device "Exact e-reader device / firmware / reading app" \
  --operator "Operator initials" \
  --observations "TOC page 1-4, source credits, reflow, fonts, dark mode and offline reading" \
  --result pass --acknowledge-direct-observation \
  --output ~/kushluk-private-evidence/reader-field-001.json
```

Use synthetic or otherwise rights-cleared data for shared screenshots. A private EPUB may contain personal calendar information or references from subscriptions. Never publish it as a public CI artifact.

The [host trial cross-check](HOST_TRIAL_REVIEW.md) can compare a consecutive local-date window against actual archived run receipts and operator observations, without creating, sending or accepting any evidence. It is a helper for the independent reviewer, **not** a five-morning certification.

## 3 — Five unattended real-host mornings

For each genuine morning, retain the run receipt (including date/edition ID), offline and online outcome, actual printer queue ID if applicable, whether duplicate printing was observed, restart/sleep/wake behavior, readiness against configured deadline, and any manual intervention. Use `kushluk run-status --date YYYY-MM-DD` as evidence; use the manual archive-recovery command **only with its existing explicit duplicate-risk acknowledgement**. After physical observation, record `--kind host-resume --artifact SOME_RUN_RECEIPT.json` and at least one additional log/photo as evidence.

Do **not** synthesize five runs or count CI simulation as real five-morning reliability. Five genuine mornings can be reviewed as a collection when available; host-safe scheduling, sleep/reboot and physical delivery remain unverified until these are independently assessed.

## Receipt safety and acceptance

`record-field-proof` creates a new mode-0600 local JSON file. It stores observation date, operator-entered name/initials, device/OS description, observed result and defects, the artifact checksum, optional matching print inspection checksum, and hashes of up to eight evidence files (each max 50 MiB). It **never** uploads, embeds or copies the evidence files. It refuses overwriting previous receipts and symlink evidence.

**Important:** a `pass` is only an **operator self-report**. Every receipt deliberately includes `independently_verified: false` and `release_gate_accepted: false`. This tool cannot know whether evidence actually depicts the tested document and device. The owner/reviewer must examine the real evidence and document the accepted gate in #13/#33/#47, respecting privacy and source rights; no work-ledger or G1–G8 progress changes merely because a receipt exists.
