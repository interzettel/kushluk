# Kuşluk Decision Atlas — GitHub Pages public preview

**Status:** a static, read-only **strategy preview**, not an accepted ADR, an actively synchronized dashboard, or proof of three-agent participation. The product's owner direction is recorded in [#170](https://github.com/interzettel/kushluk/issues/170); actual decisions remain in their [owning GitHub discussions](https://github.com/interzettel/kushluk/issues/157). The source visual concept and normalized decision graph remain under **[draft PR #177](https://github.com/interzettel/kushluk/pull/177)**; copying the **public view** does *not* approve that draft's milestone or architecture changes.

## Public content and non-goals

- `site/decision-atlas/index.html`: source-linked, standalone pan/zoom diagram with a keyboard-accessible HTML index of all 56 decisions, alternative futures, ADR/F-ID/task/evidence impact and owner-approved-vs-open disclaimers. SVG accessibility and mobile rendering still require human/browser review.
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

## Local Agent Council interoperability — future contract, not connected

The locally tested [Agent Council](https://github.com/interzettel/agent-council) manages agent messages, targeted `@mentions` and optional separate A2A tasks at **localhost only**. Its [#2 DeepSeek adapter](https://github.com/interzettel/agent-council/issues/2) is being developed by another agent, with one-time owner-enabled inference and **zero implicit repository writes**. Its 9/9 unit and 21/21 HTTP smoke results are a reported **local test**, not evidence of a live DeepSeek model adapter.

**Do not let the public GitHub Pages website query `127.0.0.1`, read local credentials, open a reverse tunnel, or become a remote instruction endpoint for Agent Council.** Web-origin restrictions alone are not an acceptable security boundary. Public GitHub review threads and private council messages have different audiences, identities, permissions and retention.

A proposed **reference-only join**, to be debated after #2 independently verifies its actual runtime, is:

| Field | Public provenance | Local-only council counterpart |
| --- | --- | --- |
| `repository` | `interzettel/kushluk` | Exactly the same repo-qualified scope, or no join |
| `decision_issue` | Immutable GitHub issue number (e.g. `171`) | Optional user-authorized tag/association with that issue |
| `atlas_node` | Stable ID from `decision-atlas.json` | Optional non-authoritative context identifier |
| `reviewer` | Body-reported real model/runner plus attributable public GitHub comment URL | Local authenticated member identity; **not** automatically identical to a GitHub login |
| `review_state` | Source-linked independent/cross-exam/founder verdict, each with real timestamp | Local participant availability/notification/claim state; self-reported ≠ consent or completion |
| `artifact` | Explicitly published public, non-sensitive artifact URL | Private, access-controlled local work evidence; never mirror automatically |

**Potential future bridge:** a user-reviewed *export* of a carefully selected and sanitized council outcome into the owning GitHub issue, followed by an explicit source-snapshot update to this site. Export is a **privileged action that requires separate owner approval**, not a side effect of reading a thread or being mentioned. There must be no free-running background escalation from public GitHub text into local inference or repository modification.

Before implementation, test a real authenticated local agent, scope-isolation across unrelated projects, provenance, redaction, denial/replay conditions, partial failure and explicit human publishing permission. GitHub remains authoritative for accepted ADRs, release plans and published founder decisions; Council may be an efficient **private deliberation transport**, never an unreviewed source-of-truth replacement.

## Safe updates after review

1. Update the frozen normalized source only after a reviewable change to the underlying discussion graph. An issue being closed or an agent comment is **not** automatic acceptance.
2. Regenerate the embedded model from the same JSON; test with `python3 tools/check_decision_atlas_site.py`.
3. Open PR to `main` with a screenshot/keyboard audit on desktop/mobile, a public-source rights check, and a documented snapshot date.
4. On merge, allow Pages deploy; check `github-pages` environment and actual user-visible page.
5. If a real **read-only** authenticated status adapter is later desired, debate its permissions, public-data boundaries and provenance in [#157](https://github.com/interzettel/kushluk/issues/157) / [#176](https://github.com/interzettel/kushluk/issues/176) before connecting it. Avoid leaking private decisions/credentials through Pages.

**Deliberate separation:** the repo's design/roadmap planning PR #177 can stay unmerged. This public preview does not confer a milestone approval, overturn ADR 0013, validate A2A protocol or authorize access to private source material.
