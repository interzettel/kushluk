# Offline e-reader export (experimental)

**Feature:** F-016 · **Owners:** [#33](https://github.com/interzettel/kushluk/issues/33), [#7](https://github.com/interzettel/kushluk/issues/7) · **Release proposal:** v1.1.0 (research/implementation may occur before the release).

This is the first runnable EPUB3 output adapter for Kuşluk, intentionally separate from the four-A4 print geometry and the morning source intake. It reads only the archived v2 `metadata.json` publication snapshot. It does **not** fetch new RSS articles, copy archived HTML articles or regenerate prose; it exports existing compact stories, practical items, attributions and notes as **four reflowable EPUB chapters**, with a navigation page.

```bash
# First generate and archive an edition through the normal CLI:
kushluk generate --date 2026-10-17

# Produce a private EPUB from the archived semantic edition:
kushluk export-epub --date 2026-10-17
# Default: archive/20261017-001/edition.epub

# Or write a new private file elsewhere:
kushluk export-epub --date 2026-10-17 --output ~/Books/my-kushluk.epub
```

The exporter writes `mimetype` as the first **uncompressed** ZIP entry, the standard `META-INF/container.xml`, package OPF3, `nav.xhtml`, four chapter XHTML files and simple offline CSS. It checks generated XML structure and ZIP integrity; returns a SHA-256 digest and a truthful `reader_hardware_verified: false`. It uses original article/source IDs and links from the frozen edition, not raw paid/third-party article bodies. File creation is restricted to a new local file with 0600 permissions; repeat exports must use a new path. No OPDS endpoint, HTTP server, SMTP sending, external service, new package dependency or existing PDF replacement is added.

**Not independently completed:** running `epubcheck` against every package, screen-reader/Kindle/KOReader/Kobo hardware testing, image optimization/alt text, localization of `xml:lang` (currently `und` for unknown), verified reflow and actual OPDS authentication. EPUB is therefore a **prototype**, not a stable v1.1 e-reader feature despite valid synthetic structure/unit tests. Do not expose an EPUB containing a private calendar or subscribed excerpts in a public catalog. Further tests and transport scope remain open under #33 and #7.

## Independent W3C EPUBCheck conformance in GitHub CI

The [EPUB conformance workflow](../.github/workflows/epub-conformance.yml) builds a **synthetic offline edition** from `tools/make_epub_fixture.py` and runs the official [W3C EPUBCheck](https://github.com/w3c/epubcheck) **v5.4.0**, with its downloaded ZIP checked against the release asset's SHA-256. The official validator is not a package dependency or copied into the repository. Only artificial/public fixture content is used; no private archives or subscribed feeds are uploaded.

**This is a real validator execution only when the workflow's `W3C EPUBCheck 5.4.0` job succeeds.** The earlier home-made ZIP/XML checks are necessary but not equivalent. Even a valid EPUB under EPUBCheck still needs **Ace by DAISY accessibility checks, screen-reader navigation, and actual Kobo/Kindle/KOReader hardware evidence**; do not turn a green validator into a false reader acceptance gate. 

## Declared publication language for screen readers

The archived v2 schema does not know the primary language of your reading material. Instead of guessing from your location or timezone, offline export now accepts an **explicit language**:

```bash
kushluk export-epub --date 2026-10-17 --language en
kushluk export-epub --date 2026-10-17 --language de-DE --output ~/Books/edition-de.epub
kushluk export-epub --date 2026-10-17 --language tr --output ~/Books/edition-tr.epub
```

Omitting `--language` retains `und` (“undetermined”), rather than falsely asserting that a reader's multilingual sources are English or German. The value is checked against a conservative BCP 47 subset, used consistently in `dc:language`, OPF `xml:lang`, navigation and chapter root `lang`/`xml:lang`. Navigation section names are translated for **English, German and Turkish**; other languages currently use English navigation labels while retaining the selected tag. The result reports the selected language.

This is an **accessibility metadata improvement**, not an assertion that each article, its generated text, pronunciation or full WCAG accessibility is validated. Mixed-language excerpts still need item-level tags and accessible-reader trials. Both explicit English and German synthetic editions are now checked by the independent W3C EPUBCheck 5.4.0 workflow, without transmitting private archives.
