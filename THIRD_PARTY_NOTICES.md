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
- Core runtime: `httpx`, `jinja2`.
- Optional print/PDF: `weasyprint`, `pypdf`, `Pillow` (plus their system/native and transitive dependencies).
- Optional raster/image-only: `Pillow`.
- Optional user-local Google OAuth: `google-auth`, `google-auth-oauthlib` (and their transitive dependencies).
- Development/testing: `pytest`, `ruff`, `Pillow`.
- Distribution build backend: `hatchling`; the independent M1 checker also installs `build` in CI.

These are package install requirements, **not copied third-party source files**. The M1 clean-install check now produces an offline installed-version/licensing-*metadata* inventory for wheel and sdist environments, documenting missing or legacy license declarations as **review required**, not legal clearance. See [Dependency audit boundaries](docs/DEPENDENCY_AUDIT.md). For the narrowly scoped first **GitHub source-only alpha**, the wheel and source archives are audited to contain only first-party MIT-licensed Python modules, original HTML template and legal/documentation text. Python dependencies install separately through the user's package manager; no Pango/Cairo/HarfBuzz/Fontconfig libraries, fonts, generated PDFs, publisher article bodies or third-party photographs are included in release assets. This restriction does not approve future font embedding, native binary redistribution, or third-party content reuse, which require separate rights checks. A passing automated metadata inventory does not complete that work.

The new OPML parser is **original standard-library Python implementation informed by published feed/OPML interoperability concepts**, not a copy of OffScroll, Goosepaper, RSSPub or other reviewed source. No external license notice is required for original independent implementation.

## Incorporated third-party text: Phase III design skills (19 October 2026)

Six text-only third-party skills (unaltered `SKILL.md` entrypoints, selected Markdown references and full original licences) are now copied to `.agents/skills/`. **Executable scripts, browser probes, downloaded assets, package dependencies, remote installation and global agent configuration are not incorporated.** This is skill guidance, not confirmation that an external runtime executed it. See [audit](docs/design/PHASE3_SKILLS_AUDIT.md).

| Local files | Pinned source | Attribution / licence |
| --- | --- | --- |
| `.agents/skills/design-maturity-review/` | [Stiprā](https://github.com/yigit-denktas/stipra/tree/a72969932bd4fb850eafd9694a5b54a62c68dd9f/.agents/skills/design-maturity-review) | Stiprā contributors / repo MIT |
| `.agents/skills/design-taste-frontend/` | [Stiprā](https://github.com/yigit-denktas/stipra/tree/a72969932bd4fb850eafd9694a5b54a62c68dd9f/.agents/skills/design-taste-frontend) | Leonxlnx / MIT |
| `.agents/skills/good-css/` | [Stiprā](https://github.com/yigit-denktas/stipra/tree/a72969932bd4fb850eafd9694a5b54a62c68dd9f/.agents/skills/good-css) | Vojta Holik / MIT |
| `.agents/skills/impeccable/` | [Stiprā](https://github.com/yigit-denktas/stipra/tree/a72969932bd4fb850eafd9694a5b54a62c68dd9f/.agents/skills/impeccable) | Original upstream licence, Apache-2.0 |
| `.agents/skills/awwwards/` | [juliobsz/skills](https://github.com/juliobsz/skills/tree/f193f6745aae738e9d54a0ca28792822e4777a63/awwwards) | Julio (juliobsz) / MIT |
| `.agents/skills/jury/` | [juliobsz/skills](https://github.com/juliobsz/skills/tree/f193f6745aae738e9d54a0ca28792822e4777a63/jury) | Julio (juliobsz) / MIT |

Original licence files are present beside each skill, including Apache-2.0 under `impeccable/`. Incorporation does not relicense the rest of Kushluk, and does not authorize npm/pip installs or outside asset downloads.

