# Kuşluk Decision Atlas — GitHub Pages public preview

**Status:** a static, read-only **strategy preview**, not an accepted ADR, an actively synchronized dashboard, or proof of three-agent participation. The product's owner direction is recorded in [#170](https://github.com/interzettel/kushluk/issues/170); actual decisions remain in their [owning GitHub discussions](https://github.com/interzettel/kushluk/issues/157). The source visual concept and normalized decision graph remain under **[draft PR #177](https://github.com/interzettel/kushluk/pull/177)**; copying the **public view** does *not* approve that draft's milestone or architecture changes.

## Public content and non-goals

- `site/decision-atlas/index.html`: source-linked, standalone, accessible-attempting pan/zoom diagram with domain filters, alternative futures, ADR/F-ID/task/evidence impact and owner-approved-vs-open disclaimers.
- `site/decision-atlas/decision-atlas.json`: exact public JSON snapshot **embedded in the HTML**, so the app opens without a backend.
- All inputs are **public Kuşluk issues and strategy drafts**. No personal email, project secrets, source article bodies, private Drive content, AGENT Council credential, local printer or private log is incorporated.
- JavaScript does **not** poll by default. A user explicitly clicking **Load discussion comments** makes a **read-only unauthenticated HTTPS GET** to `api.github.com` for the selected public GitHub issue; comment bodies are displayed with `textContent`, not executed as HTML. This may fail due to rate limits, network controls or private/restricted repository policies. GitHub remains authoritative; this view may be stale or truncated.
- **No live Agent Council integration.** Council is under development in [its own repository](https://github.com/interzettel/agent-council) and remains local-only. This Pages site will not connect to localhost, auto-wake models, publish GitHub comments or claim live model quotas.
- The frozen snapshot can become stale; its public visible date is **19 October 2026**, not an automated status sync.

## GitHub Pages rollout and protection

The official route is via [`.github/workflows/decision-atlas-pages.yml`](../.github/workflows/decision-atlas-pages.yml). The workflow has two jobs:

1. **Verify:** on relevant PRs, pushes or manual dispatch, check embedded JSON equality, graph integrity, offline script syntax (Node if available), safety boundaries, meaningful issue links and no background polling.
2. **Deploy:** on approved **`main` only**, after Verify passes, publish `site/decision-atlas/index.html` as the Pages **root `index.html`** and the JSON file; no other repository files are copied into the public artifact. GitHub's `github-pages` environment and the standard short-lived OIDC `GITHUB_TOKEN` permissions are used. No external hosting credentials or domain purchases.

**One-time GitHub setting may be required:** open [repository Pages settings](https://github.com/interzettel/kushluk/settings/pages) → **Build and deployment** → **Source: GitHub Actions**. The GitHub connector in this session does **not** expose Pages settings writes or a Pages status read, so do not call this step complete unless the Pages deployment job succeeds and the returned URL serves the actual atlas. If `configure-pages` fails because Pages is disabled, change the repository Pages source and **rerun the workflow**; do not change the permissions scope or paste PATs into workflows.

The normal GitHub.com repository URL shape is `https://interzettel.github.io/kushluk/`; this is a **candidate, not a verified live URL** until GitHub's deployment job reports success and a browser fetch confirms the published content. A custom domain or Pages restriction can change the actual URL.

## Safe updates after review

1. Update the frozen normalized source only after a reviewable change to the underlying discussion graph. An issue being closed or an agent comment is **not** automatic acceptance.
2. Regenerate the embedded model from the same JSON; test with `python3 tools/check_decision_atlas_site.py`.
3. Open PR to `main` with a screenshot/keyboard audit on desktop/mobile, a public-source rights check, and a documented snapshot date.
4. On merge, allow Pages deploy; check `github-pages` environment and actual user-visible page.
5. If a real **read-only** authenticated status adapter is later desired, debate its permissions, public-data boundaries and provenance in [#157](https://github.com/interzettel/kushluk/issues/157) / [#176](https://github.com/interzettel/kushluk/issues/176) before connecting it. Avoid leaking private decisions/credentials through Pages.

**Deliberate separation:** the repo's design/roadmap planning PR #177 can stay unmerged. This public preview does not confer a milestone approval, overturn ADR 0013, validate A2A protocol or authorize access to private source material.
