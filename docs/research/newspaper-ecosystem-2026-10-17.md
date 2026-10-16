# Newspaper ecosystem review — GitHub topic + adjacent personal press tools

**Research snapshot:** 17 October 2026 · **Owner:** [Kushluk issue #84](https://github.com/interzettel/kushluk/issues/84) · **Status:** literature/code review, **not** runtime or UX/hardware testing.  
**Downloadable machine-readable matrix:** [25 reviewed candidates](newspaper-project-matrix-2026-10-17.csv).  
**Stable reuse policy:** [ADR 0011](../adr/0011-reuse-upstream-preserve-product-layer.md) and [THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md).

## Scope and method

Discovery used GitHub's [`newspaper` topic](https://github.com/topics/newspaper) (GitHub displayed **548 public repositories** when opened during this review), GitHub repository searches for personal/printable newspapers and RSS-to-PDF/EPUB, plus adjacent e-reader, newsroom and printing projects. **548 is the discovery population, not 548 individually reviewed repositories.** The topic contains lots of publisher websites, OCR/crawling/data projects and templates unrelated to personal physical publishing. Twenty-five were selected and inspected at repository-metadata + README levels; for the strongest candidates, inspected actual `LICENSE`, project layout, config, renderer, source adapter, scheduler, QA/test files. Search-suggested projects without a real executable or license were downgraded rather than counted as viable competitors.

**Audit discipline:** `LICENSE verified` means we read its actual GitHub file; `metadata/README` means weaker evidence. **No license** does **not** mean public domain or MIT. `NOASSERTION` requires inspecting actual terms. Latest code push dates and stars were retrieved from GitHub repository metadata on the review date; they are **not** quality/security scores. Claims about advertised features are grounded in README and the named code paths, **not a successful local build, security audit, demo benchmark, or legal conclusion**. Unverified or omitted entries are explicitly treated as such.

### Top candidates — relevance to Kushluk

| Priority | Project | Category | Licence / verification | What to learn | Decision |
| --- | --- | --- | --- | --- | --- |
| **P1** | [Goosepaper](https://github.com/j6k4m8/goosepaper) | Closest print/e-reader counterpart | **Apache-2.0 — LICENSE checked** | Schema v2, modular providers, article source modes, reMarkable page profiles, delivery policies | Study adapter/config seams; **no automatic fork** |
| **P1** | [RSSPub](https://github.com/harshit181/RSSPub) | EPUB/OPDS newspaper | **MIT — LICENSE checked** | EPUB, OPDS, grayscale assets, reader delivery, mobile save-later shortcut | Target **optional EPUB/OPDS** experiments |
| **P1** | [Morning Paper](https://github.com/dmthepm/morning-paper) | Reader-owned press workflow | **MIT — LICENSE checked** | Newsroom files, feedback routing, copy/paper budgets, PDF visual QA | Adopt original feedback + proof contracts |
| **P1** | [Firstlight](https://github.com/cruftbox/firstlight) | Home-printer personal digest | **MIT — LICENSE checked** | Onboarding wizard, tasks/calendar/sports, printer reachability and local archive | Compare actual setup + CUPS preflight |
| **P1** | [OpenPaper](https://github.com/falense/openpaper) | Agent-fed newsroom | **MIT — LICENSE checked** | Listing-before-body fetch, centralized dedup, shared browser, source adapters | Evaluate metadata-first intake, rights gate |
| **P1** | [OffScroll](https://github.com/offscroll/offscroll) | Local-model personal press | **Apache-2.0 — LICENSE checked** | OPML import, embeddings/clusters, Typst vs WeasyPrint | Isolated tests, no compulsory Ollama |
| **P1** | [Hermes Paper Agent](https://github.com/vaelkeep/hermes-paper-agent) | Verified agent press line | **MIT — LICENSE checked** | Code-generated numbers, desk write/check/fix, per-edition provenance | Verification and deterministic desk contracts |
| **P2** | [Vael Paper](https://github.com/vaelkeep/vael-paper) | Independent pagination/reader | **MIT — LICENSE checked** | Renderer-only Markdown contract, continuation, responsive page turns | Digital reading prototype only; preserve A4 invariant |
| **P2** | [Curio](https://github.com/CyberDNS/Curio) | Self-hosted digital RSS paper | **MIT — LICENSE checked** | Preference/source management and reading state | UX reference; avoid mandatory DB/OpenAI |
| **P2** | [git-newspaper](https://github.com/LordAizen1/git-newspaper) | Data-driven genres | **Unverified: README claims MIT, LICENSE absent** | Seeded deterministic archetype selection from git metrics | Conceptual selection rules only |
| **P2** | [Newsprint](https://github.com/brennanbrown/newsprint) | Editorial CSS/theme | **AGPL-3.0-or-later — LICENSE checked** | Accessible print styles and responsive newsprint rules | **No code/asset copy** pending licence review |
| **P2** | [Tiny Times](https://github.com/The-Relational-Technology-Project/tiny-times) | Small-format audience edition | **MIT — LICENSE checked** | Age/density-sensitive content, print-first coloring-page idea | Conceptual; cloud and child-content caveats |

The [CSV](newspaper-project-matrix-2026-10-17.csv) includes the remaining 13 screened repos: [RSS Newspaper Generator](https://github.com/tiborpilz/RSS-Newspaper-Generator), [Morning Press](https://github.com/rdewolff/morning-press), [Pressbrief](https://github.com/rootkovska/pressbrief), [Readwise to Newspaper](https://github.com/benbarten/readwise-to-newspaper), [HN Print](https://github.com/ahmetomerv/hn-print), [ThermalTimes](https://github.com/ZombieNW/ThermalTimes), [HTML Newspaper for E-readers](https://github.com/Flybell/HTML-newspaper-for-e-readers), [Kindle Daily Digest](https://github.com/jmbluhm/kindle-daily-digest), [Unim.press](https://github.com/thesephist/unim.press), [Daily Paper](https://github.com/philgyford/daily-paper), [Broadsheet](https://github.com/maetl/broadsheet), [Personal Newspaper Printer](https://github.com/consul-design/personal-newspaper-printer) and [Gazette](https://github.com/jasonrdsouza/gazette).

## Code-level investigations / highest-value transfers

### 1. Goosepaper — credible direct comparator, not a candidate for a wholesale port

**Primary evidence:** [README](https://github.com/j6k4m8/goosepaper/blob/master/README.md), [config.py](https://github.com/j6k4m8/goosepaper/blob/master/goosepaper/config.py), [RSS provider](https://github.com/j6k4m8/goosepaper/blob/master/goosepaper/storyprovider/rss.py), [Readwise provider](https://github.com/j6k4m8/goosepaper/blob/master/goosepaper/storyprovider/readwise.py), [delivery implementation](https://github.com/j6k4m8/goosepaper/blob/master/goosepaper/upload.py), [tests](https://github.com/j6k4m8/goosepaper/blob/master/goosepaper/test_config.py), [Apache licence](https://github.com/j6k4m8/goosepaper/blob/master/LICENSE). Last observed code push: **2026-10-05**.

The source has a genuinely versioned **v2 paper config** with dataclasses for paper, source and delivery preferences; user-level delivery defaults remain separate from each paper's configuration. Theme, page profile and columns are independently configurable: `layout=auto|1col|2col|3col`; profiles for reMarkable, US Letter and A4. Source modules include `rss.py`, `reddit.py`, `mastodon.py`, `bluesky.py`, `readwise.py`, `wikipedia.py`, `comic.py`, `weather.py`. There is meaningful configuration-validation/test coverage. `rss.py` provides `body_source=auto|content|summary|article` and `byline=all|none|first`; Readwise supports filter by location/category/tags and cursor pagination. Delivery code handles no-replace / exact / case-insensitive replacement, destination folder, optional cleanup and PDF/EPUB upload.

**Transfer decisions:** (1) prototype a versioned, source-specific adapter options contract; (2) benchmark source-derived summary vs publisher-page retrieval under [#4](https://github.com/interzettel/kushluk/issues/4) with rights and attribution constraints; (3) adopt the *concept* of independent user defaults/paper recipe and page/device output profiles; (4) prototype a **reMarkable-only optional** destination adapter after paper-print baseline; (5) use config and provider tests as fixture inspiration. **Anti-pattern:** Goosepaper can remove a previous remote document and optionally delete local output; do not duplicate that without a user-owned archive, explicit permissions and recoverable delivery receipts. Its variable-page newspaper output is not Kushluk's immutable four-logical-A4-page composition for printing.

**Concrete owner/gate:** [#48](https://github.com/interzettel/kushluk/issues/48)/[#49](https://github.com/interzettel/kushluk/issues/49) source modes, [#33](https://github.com/interzettel/kushluk/issues/33) digital profile, [#7](https://github.com/interzettel/kushluk/issues/7) delivery. Build one synthetic per-provider fixture and verify missing/denied sources do not create fabricated text.

### 2. RSSPub — recovered historical reference, now positively identified

**Primary evidence:** [README](https://github.com/harshit181/RSSPub/blob/main/README.md), [Cargo.toml](https://github.com/harshit181/RSSPub/blob/main/Cargo.toml), [MIT licence](https://github.com/harshit181/RSSPub/blob/main/LICENSE). GitHub metadata shows code push **2026-10-16**, with a Rust/Axum/Tokio/SQLite/EPUB stack.

RSSPub directly addresses the missing non-paper route: configured RSS and saved articles produce an **EPUB**, exposed by **OPDS** or email and configured via a web UI. It describes image grayscale/resizing, cron scheduling, reader download links, iOS/Android HTTP-shortcut input, and optional Basic authentication. The `epub-builder` dependency is declared in Rust; this is not merely a design mockup.

**Transfer decisions:** create a provider-independent **EPUB renderer/export adapter** for the already completed editorial edition; an **optional, private OPDS service** can serve these archives without handing subscribed material to a shared SaaS. Add read-later and Shortcuts intake as opt-in source types. Keep HTML/PDF archive canonical and do not introduce Rust runtime as compulsory infrastructure. Privacy/security gate: OPDS and latest-download endpoints must be private where material is non-public; authorisation and per-user content rights must be explicit. The project's one-click deployment example contains placeholder/root credentials: **never use those defaults for a production service**.

**Concrete owner/gate:** [#33](https://github.com/interzettel/kushluk/issues/33) and [#7](https://github.com/interzettel/kushluk/issues/7): produce a validating EPUB with clickable ToC, four editorial chapters, correct attribution, grayscale rendition and no leak of private user data in a public catalog. This **resolves the identity** of RSSPub flagged in the old upstream document; it does not prove production-level suitability.

### 3. Morning Paper — the strongest source for editorial proof culture

**Primary evidence:** [README](https://github.com/dmthepm/morning-paper/blob/main/README.md), [proofs.py](https://github.com/dmthepm/morning-paper/blob/main/src/morning_paper/proofs.py), [edition_workspace.py](https://github.com/dmthepm/morning-paper/blob/main/src/morning_paper/edition_workspace.py), [tests](https://github.com/dmthepm/morning-paper/tree/main/tests), [MIT licence](https://github.com/dmthepm/morning-paper/blob/main/LICENSE).

Its most valuable feature is *not* a broadsheet filter. The private newsroom is made of inspectable files and feedback routes, separating editorial, visuals, sources, delivery, interests, voice, budget and checks. The `edition_workspace.py` source includes persistent review and proof artifacts, page-budget controls and local run tickets. `proofs.py` inspects PDF validity and pages and can rasterize for visual inspection; its tests include visual snapshots and workflows. Kushluk's existing PDF geometry checks are a baseline, not a complete visual layout proof.

**Transfer:** a concise **feedback-to-editable-policy mapping** (e.g., "less finance", "shorter headlines", "images less often") with inspectable scope and reversible overrides; proof receipts including per-page text fit, raster screenshots and manifest hashes. Keep sensitive reader preferences local. **Do not** bundle other project's templates/fonts without checking separately licensed font files. Owner: [#19](https://github.com/interzettel/kushluk/issues/19), [#14](https://github.com/interzettel/kushluk/issues/14), [#51](https://github.com/interzettel/kushluk/issues/51), [#21](https://github.com/interzettel/kushluk/issues/21).

### 4. Firstlight — dependable morning UX, with idempotency caveat

**Primary evidence:** [README](https://github.com/cruftbox/firstlight/blob/master/README.md), [scheduler.py](https://github.com/cruftbox/firstlight/blob/master/app/scheduler.py), [printer.py](https://github.com/cruftbox/firstlight/blob/master/app/print/printer.py), [setup templates](https://github.com/cruftbox/firstlight/tree/master/app/templates/setup), [MIT licence](https://github.com/cruftbox/firstlight/blob/master/LICENSE).

Concrete onboarding exists: ~10 setup screens spanning location, print time, printer, calendar, sports, news and email. The Docker-first app combines an always-on home host, web archive, preview and controlled print. The scheduler uses APScheduler with timezone-aware cron and a misfire grace period; its `last_printed.txt` is updated **after** the pipeline. The network printer adapter has CUPS/IPP queue registration and `lpr` submission.

**Transfer:** onboarding and failure UX, real queue connection guidance, task + sports practical modules. **Avoid copying the thin `last_printed` pattern as an at-most-once barrier**: a crash after CUPS submission but before the marker can cause a duplicate. Kushluk already has early archive + intent receipts; keep that stronger safety boundary. Avoid assuming network IPP discovery is universally reliable or that one page meets the four-page print contract. Owner [#5](https://github.com/interzettel/kushluk/issues/5)/[#47](https://github.com/interzettel/kushluk/issues/47)/[#13](https://github.com/interzettel/kushluk/issues/13).

### 5. OpenPaper — avoid wasted browser/network work

**Primary evidence:** [README](https://github.com/falense/openpaper/blob/main/README.md), [template](https://github.com/falense/openpaper/blob/main/skills/openpaper/templates/broadsheet.html.j2), [MIT licence](https://github.com/falense/openpaper/blob/main/LICENSE).

A Claude Code plugin, **not** a self-contained provider-independent scheduled daemon. It runs source fetchers in **listing-only** mode to acquire title/link/date metadata; checks `seen.txt` before fetching article bodies; then shares one Playwright browser only among content sources that need it. Feed/API sources can avoid Chromium in the listing pass. This is an unusually direct answer to minimizing retrieval cost, source fatigue and duplicate analysis.

**Transfer:** bounded metadata discovery → dedup across feeds → approved content acquisition; source-specific fetchers can be learned from but should be generated, validated, sandboxed and provenance-tagged only under user authorization. Scraping paid article bodies is not a consequence of having network access; [#4](https://github.com/interzettel/kushluk/issues/4) governs allowed summarization/reference/direct inclusion. No mandatory Claude Code dependency. Owner [#48](https://github.com/interzettel/kushluk/issues/48), [#49](https://github.com/interzettel/kushluk/issues/49).

### 6. OffScroll — alternative rendering and semantic dedup, but substantially heavier

**Primary evidence:** [README](https://github.com/offscroll/offscroll/blob/master/README.md), [OPML import](https://github.com/offscroll/offscroll/blob/master/src/offscroll/ingestion/opml.py), [clustering](https://github.com/offscroll/offscroll/blob/master/src/offscroll/ingestion/clustering.py), [WeasyPrint renderer](https://github.com/offscroll/offscroll/blob/master/src/offscroll/layout/renderer.py), [Typst renderer](https://github.com/offscroll/offscroll/blob/master/src/offscroll/layout/typst_renderer.py), [Apache licence](https://github.com/offscroll/offscroll/blob/master/LICENSE).

The repo offers a real `import_opml` implementation with URL deduplication, embedded vectors and HDBSCAN-based `cluster_items`, an HTML/WeasyPrint renderer and separate `typst_renderer.py` backend that preprocesses content and escapes Typst special characters. It has renderer matrix tests. Ollama embeddings and curation models are described as functional; cloud model interfaces are explicitly **planned, not implemented** in its README.

**Transfer:** prioritize portable OPML feed import/export first (small surface). Evaluate semantic clustering only against an annotated duplicate corpus: demonstrate improvement beyond cheap URL/title rules without uncontrolled resource or inference costs. In [#26](https://github.com/interzettel/kushluk/issues/26), use its dual-engine approach to frame a **bounded Typst spike** with identical content, typography, page count, images and raster diffs. The repository metadata reports a very large source tree and ~1.2 GB repository size, so cloning or importing it is **not** an appropriate first step. Never make 8B local model weights compulsory for readers. Owner [#49](https://github.com/interzettel/kushluk/issues/49), [#26](https://github.com/interzettel/kushluk/issues/26), [#51](https://github.com/interzettel/kushluk/issues/51).

### 7. Hermes Paper Agent + Vael Paper — useful split of source, press, reader

**Evidence:** [Hermes README](https://github.com/vaelkeep/hermes-paper-agent/blob/main/README.md), [Hermes tests](https://github.com/vaelkeep/hermes-paper-agent/tree/main/tests), [Vael README](https://github.com/vaelkeep/vael-paper/blob/main/README.md), their separate [MIT](https://github.com/vaelkeep/hermes-paper-agent/blob/main/LICENSE) [licenses](https://github.com/vaelkeep/vael-paper/blob/main/LICENSE).

Hermes provides short numeric/code-driven "desks" for weather, finances and similar data; agent-generated prose is checked and corrected against a press contract. The renderer Vael Paper consumes finished articles and explicitly does not write them. Vael's browser reader advertises re-pagination, continuation slugs, accessible text-size adjustment, and position retention across screen sizes.

**Transfer:** source-of-truth numerics must come from code and attached provenance; an agent can propose wording but cannot falsify them. Adopt typed checker output, agent-safe bounded repair requests and reproducible fixtures. Test a separate optional browser reading surface independently from the print PDF's four-page invariant. Do not adopt Hermes/Vael as hard runtime dependencies or represent their live demo as a Kuşluk test. Owner [#20](https://github.com/interzettel/kushluk/issues/20), [#21](https://github.com/interzettel/kushluk/issues/21), [#33](https://github.com/interzettel/kushluk/issues/33).

### 8. Licence and publisher-rights landmines

- **Newsprint theme:** [README](https://github.com/brennanbrown/newsprint/blob/main/README.md) contains an **MIT** badge, but the actual [LICENSE](https://github.com/brennanbrown/newsprint/blob/main/LICENSE) begins with GNU **Affero GPL v3 or later** terms. Treat **AGPL-3.0-or-later as the repo's operative notice**, verify any exceptional file-level licensing before use, and **do not copy CSS, templates or assets** into MIT Kushluk without a legal review. General principles such as semantic headings, print contrast or skippable navigation are fine to independently implement.
- **Unlicensed candidates** (e.g., Pressbrief, Readwise-to-Newspaper, HN Print, Kindle Assist, ThermalTimes, Broadsheet, Gazette): absent public licence is a **stop for code reuse**, not a reason to guess MIT. Some README text says "open source" without a LICENSE file; treat as unverified. `git-newspaper` README says MIT but our `LICENSE` fetch returned 404; do not claim a verified MIT grant. `Morning Press` README likewise claims MIT but its `LICENSE` fetch was unavailable.
- **Daily Paper/Guardian:** [README](https://github.com/philgyford/daily-paper/blob/main/README.md) says publisher API data can only be kept for **24 hours**. This demonstrates why licensing of *software* and rights to *article content* must be separate. Do not copy the bulk-content import/retention pattern into Kuşluk's durable archive.
- **Goosepaper/Readwise/RSSPub:** API access may authorize ingestion without authorizing public republication of source articles. Keep each provider's reference/derivative/personal-copy modes explicit. Never expose private OPDS or e-mail archive endpoints accidentally.
- **Third-party fonts and images** may have **different licenses** from the program itself. A repository-wide MIT/Apache tag does not by itself prove a bundled photo, publisher masthead, article or font is free to redistribute.
- **No code, layouts, images or fonts from these external repos were copied by this research.** Therefore `THIRD_PARTY_NOTICES.md` remains an incorporation ledger, not a bibliography; source URLs remain in this investigation and [UPSTREAM_REVIEW.md](../UPSTREAM_REVIEW.md).

## Category-level market picture

| Category | Relevant projects | What Kushluk should be able to do better |
| --- | --- | --- |
| Direct personal newspaper engines | Goosepaper, Firstlight, Morning Paper, OffScroll, OpenPaper, Curio | **Same four editorial pages** across A4 and A3, rightfully sourced, reproducibly validated, user-owned, provider-neutral, no mandatory inference subscription |
| E-reader output / reading-list products | RSSPub, Goosepaper, Kindle Assist, HTML Newspaper for E-readers | Same canonical edition exported as accessible EPUB/OPDS/e-reader PDF with private distribution, source rights and controlled user auth |
| Agent-run newsroom/press | Morning Paper, Hermes, OpenPaper, Vael | Explicit data desk / prose desk / press boundaries, deterministic figures, source provenance, bounded correction and confidence in every edition |
| Visual/print composition | Newsprint, Unim.press, git-newspaper, HN Print, RSS Rust Generator | Readable monochrome-first geometry, fixed slots/typography, print preflight, traceable theme IDs instead of a collection of filters |
| Personal hardware / implementation research | Firstlight, ThermalTimes, Personal Newspaper Printer | Native Mac/Linux printing, printable dry-run kits, safe deduplicated CUPS delivery and real A4/A3 proof evidence |
| Publisher-data or general news aggregators | Daily Paper, Broadsheet, Pressbrief | Preserve source-specific rights, retention and user control; don't build a centrally hosted article mirror |

## Explicit transfer decisions / engineering queue

These are **recommendations for experiments**, not approved dependency imports or new issues.

| Order | Candidate experiment | Origin | Owning issue | Pass / fail evidence |
| --- | --- | --- | --- | --- |
| **1** | **RSS/OPML setup**: import/export OPML, show deduped subscriptions and per-source reference/summary modes | OffScroll + Goosepaper + OpenPaper | [#48](https://github.com/interzettel/kushluk/issues/48), [#49](https://github.com/interzettel/kushluk/issues/49) | Real OPML fixtures, duplicates removed; consented source list editable; no unapproved article body retrieval |
| **2** | **EPUB export** of canonical print edition with navigation and per-source credit; optional private OPDS follows | RSSPub + Goosepaper | [#33](https://github.com/interzettel/kushluk/issues/33), [#7](https://github.com/interzettel/kushluk/issues/7) | epubcheck/reader QA, stable issue identity, no leaked credentials, correct images and rights; no new required service |
| **3** | **Page-by-page visual proof**: rasterize PDF, compare baseline, generate inspectable error receipts | Morning Paper + Hermes | [#21](https://github.com/interzettel/kushluk/issues/21), [#45](https://github.com/interzettel/kushluk/issues/45) | Four A4 and imposed A3 outputs checked for actual text fit, type scale, margins and source markers; print hardware still separate |
| **4** | **Onboarding + printer diagnostic** for Mac/Linux using existing CUPS, with honest offline/fallback behavior | Firstlight | [#5](https://github.com/interzettel/kushluk/issues/5), [#47](https://github.com/interzettel/kushluk/issues/47) | User can select printer/profile and see correct capability/errors without writing printer admin config automatically |
| **5** | **Source listing → dedup → content fetch** staged architecture | OpenPaper + Goosepaper | [#49](https://github.com/interzettel/kushluk/issues/49), [#4](https://github.com/interzettel/kushluk/issues/4) | Fewer repeated requests, no unnecessary Playwright, no rights escalation, evidence that summaries trace to approved sources |
| **6** | **Offline/optional Typst** comparative renderer + clustering benchmarks | OffScroll | [#26](https://github.com/interzettel/kushluk/issues/26), [#30](https://github.com/interzettel/kushluk/issues/30) | Controlled equal-content four-page test with timing, memory and font/crop differences; adopt only if reliably better |
| **7** | **Reader-owned feedback and style budgets** | Morning Paper + Curio | [#19](https://github.com/interzettel/kushluk/issues/19), [#14](https://github.com/interzettel/kushluk/issues/14) | Reversible, inspectable local preference change affecting next edition without remote profiling or forced engagement |

## Rejections and follow-up verification

**Reject for Kushluk core:** mandatory Claude/OpenAI/Ollama to render a newspaper; wholesale forks of another publisher product; unaudited scraping and full text replication; hidden remote upload/telemetry; automatic delete/re-upload as "dedup"; internet-exposed private OPDS; breaking the four-A4 logical print contract for reMarkable page proportions; third-party fonts/assets copied on the strength of a top-level badge.

**Defer unless tested:** fancy paper art, paper-only thermal receipts, unrelated web news portal templates, centralised "one news provider" subscription infrastructure, heavy per-user Postgres/LLM stacks, page-animation as a blocker for paper delivery.

**Evidence still missing:** independent installation/execution of external tools, print/raster side-by-side examples under identical content, fresh audit of every transitive dependency and asset's license, source-usage permission review with rights counsel where appropriate, maintained benchmark of current versions, and full topic-wide crawl. Those limitations must survive future progress reports: this is a **source-backed research review**, not a claim that all 25 are production-ready.

**Next review trigger:** when starting [#48](https://github.com/interzettel/kushluk/issues/48), [#33](https://github.com/interzettel/kushluk/issues/33), [#21](https://github.com/interzettel/kushluk/issues/21), or changing the project's own license under [#38](https://github.com/interzettel/kushluk/issues/38), revisit the precise upstream commit and file-specific license/asset situation before implementing.

