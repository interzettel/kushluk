# Phase III · Design skill provenance, threat boundary and Atlas UX audit

**Snapshot:** 19 October 2026. **Scoped project:** Kushluk Decision Atlas at https://interzettel.github.io/kushluk/. **Owner instruction:** add the four canonical Stiprā skills plus [juliobsz/skills](https://github.com/juliobsz/skills) (two skills), then fix demonstrable UX problems. **Phase I Agent Council stays independent.** This is documentation and one reversible static-site patch, **not** a new ADR, release approval, or strategy merge.

## Source and licensing verification

- Stiprā source pinned at `a72969932bd4fb850eafd9694a5b54a62c68dd9f`: `design-maturity-review` (Stiprā root MIT), `design-taste-frontend` (Leonxlnx, MIT), `good-css` (Vojta Holik, MIT), `impeccable` (Apache-2.0 with its complete bundled licence).
- juliobsz/skills pinned at `f193f6745aae738e9d54a0ca28792822e4777a63`: distinct `awwwards` and `jury` skills (Julio/juliobsz, MIT). Its README recommends the remote `npx skills` installer; **not run** in this review. Helper scripts require Node 20+, Playwright/Chromium and for a full jury report `axe-core`. Some design-taste scripts perform network asset fetches. Different stacks/defaults do not imply Kushluk should migrate away from zero-dependency static HTML.
- Reviewed upstream file inventories and six entrypoints. Vended only text `SKILL.md`, selected text references and original licence notices. Explicitly **not** vended: executable JS/browser scripts, terminal wrappers, image/photo libraries, downloaded assets or transitive tools. Do not claim full upstream functionality or a verified local Claude/DeepSeek installation. No shell install, execution or model calls were performed as part of the upstream audit.

## Honest runtime compatibility

| Surface | Present status | To qualify as actually working |
| --- | --- | --- |
| GitHub repository | Six local discoverable guidance entrypoints under `.agents/skills/` | Static provenance/links check and PR CI |
| ChatGPT via GitHub connector | Can inspect and apply text instructions to audited source | Do not imply local skill-loader import or helper-script execution |
| Claude Code | Candidate portable Markdown install, **unverified** runtime | A real Claude session must show paths loaded and a bounded sample review |
| Local DeepSeek | **Unverified;** no attachment to the other agent's local council | Owner-operated runtime must demonstrate reading one skill and citing a test result |
| Browser scripts / jury automation | **Not installed** | Audit complete executable sources, pin packages, run limited offline/local browser harness and report axe/CPU outcomes |

## First Atlas findings (existing 1440 × 900 and 390 × 844 Chrome screenshots + main HTML source)

1. **Mobile branching (observed):** a one-row horizontally scrolling sidebar shows only parts of topics 01–03 and clips the active #03 label. It obscures the number of available groups. Fix: native accessible topic selector with explicit All topics choice at ≤850 px; retain desktop sidebar.
2. **Search result control (observed from source):** `#find` silently selects the first matching node when typing ≥2 characters; there is no list or zero-result feedback, search across groups looks unpredictable. Fix: show numbered, clickable matches with topic/status, no automatic selection, and a clear state.
3. **Focused navigation (inferred):** the site has an index but no skip-to-detail target; keyboard users traverse numerous controls before the inspector. Fix: visible-on-focus skip link and mobile inspector access from selected cards; preserve focus-visible.
4. **Context/truthfulness (keep):** owner versus contested versus open states and the prominent PUBLIC PREVIEW prevent proposals being presented as accepted. Retain frozen `decision-atlas.json`, 56 nodes, 87 links, zero confirmed independent peer reviews and public click-only GitHub issue comments.
5. **Creative direction (judgment):** printed-paper serif headings, deep forest and restrained coral are distinctive enough to keep. Avoid the temptation to add heavyweight animated effects simply because `awwwards` mentions them. Prefer clarity and generous touch targets over marketing-site theatrics.

**Evidence method:** source/Chrome assertions may substantiate DOM behaviors and screenshots may substantiate layout; neither substitutes for actual screen reader, color profile or founder art-direction judgment. No invented blind jury score. The corrective patch should extend headless Chrome smoke and source invariants; record exact-head CI separately in the PR.

## Decision / authority boundary

Do not change source JSON, accepted ADRs, #177 strategy proposal, source licensing, hardware/printing gates, or Phase I's Agent Council. The site's public preview never reads localhost, credentials, personal newsletters or local model conversations. Improvements are not an endorsement of the visual direction beyond the bug fixes. Keep a fallback path for index navigation and for missing JavaScript; no remote analytics.
