# Third-Party Notices

**This file already exists at the repository root.** It is the durable legal notice register for material **actually incorporated** into Kushluk, not a list of votes approving reuse. [Research citations](docs/research/newspaper-ecosystem-2026-10-17.md) and independently documented [ChatGPT/Claude reuse ballots](docs/REUSE_REVIEWS.md) are recorded elsewhere. A source may be studied, without its code/assets ever being used.

Kushluk is MIT licensed. This file records third-party code, templates, layouts, and other material incorporated into the repository.

## Policy

Before copying or substantially adapting third-party material:

1. verify the source repository and exact license;
2. record the source URL, project name, copyright holder if available, license, and files/components reused;
3. preserve required notices in the relevant source files when the license requires it;
4. prefer adaptation at clear seams rather than importing an entire product architecture.

## References reviewed — no code incorporated

The following projects were reviewed as architecture/product references. No source code or template from them has been copied into Kushluk by the Stage 1 implementation:

- `cruftbox/firstlight` — MIT; useful reference for Open-Meteo, RSS, single-page local printing and archive patterns.
- `dmthepm/morning-paper` — MIT; useful reference for an owned newsroom, finite editions and CLI/PDF separation.
- `falense/openpaper` — MIT; useful reference for deterministic source fetchers and separating ingestion from curation.
- `vaelkeep/hermes-paper-agent` — **MIT LICENSE verified 17 Oct 2026**; architectural reference for generator/press separation, validation loops and provenance; no code copied.
- `drkpxl/drkpxl-skills` — earlier morning-briefing/print workflow reference; verify exact source and license before copying anything.
- Karen X. Cheng's personal newspaper example — design/product reference only.

- `j6k4m8/goosepaper` — **Apache-2.0 LICENSE verified 17 Oct 2026**; reviewed config/provider and reMarkable delivery boundaries; no code copied.
- `harshit181/RSSPub` — **MIT LICENSE verified 17 Oct 2026**; EPUB, OPDS, local image processing and e-reader transport reference; no code copied.
- `offscroll/offscroll` — **Apache-2.0 LICENSE verified 17 Oct 2026**; OPML, semantic dedup and alternative Typst rendering reference; no code copied.
- `vaelkeep/vael-paper` — **MIT LICENSE verified 17 Oct 2026**; independent Markdown-to-reader pagination reference; no code copied.

For all reviewed sources including **AGPL-3.0-or-later Newsprint** and unlicensed candidates, see [25-project research + rights caveats](docs/research/newspaper-ecosystem-2026-10-17.md) and [the CSV matrix](docs/research/newspaper-project-matrix-2026-10-17.csv). This references their ideas only: **no third-party source code, fonts, article text or images are incorporated by the survey**.

See `docs/UPSTREAM_REVIEW.md` for the current reuse assessment.

## Declared external package dependencies vs copied code

At the current source tree, `pyproject.toml` declares the following **installed, not vendored** packages:
- Runtime: `httpx`, `jinja2`.
- Optional PDF: `weasyprint`, `pypdf` (plus their system/native and transitive dependencies).
- Development/testing: `pytest`, `ruff`.

They are normal Python dependencies subject to their own licenses. Their *exact resolved versions, transitive licenses and any copied fonts/assets* require a package lock/SBOM/license check before a distribution release; declaring them here does not assert that check is complete.

The new OPML parser is **original standard-library Python implementation informed by published feed/OPML interoperability concepts**, not a copy of OffScroll, Goosepaper, RSSPub or other reviewed source. No external license notice is required for original independent implementation.

## Incorporated third-party code

None recorded yet beyond normal declared package dependencies.

When code or substantial adapted material is incorporated, add the exact source, license, copyright notice and affected Kushluk files here.
