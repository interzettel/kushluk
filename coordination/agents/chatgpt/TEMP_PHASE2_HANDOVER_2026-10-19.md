# TEMPORARY SESSION HANDOVER — Kuşluk Phase II / Decision Atlas

**Created:** 2026-10-19 by ChatGPT GPT-6 (repository GitHub connector).  
**Status:** TRANSIENT RESTART CHECKPOINT, **not** an ADR, issue, release approval, maintained ledger or permanent source of truth.  
**File location:** `coordination/agents/chatgpt/TEMP_PHASE2_HANDOVER_2026-10-19.md` on **branch `site/decision-atlas-pages-v1`**, which backs [PR #181](https://github.com/interzettel/kushluk/pull/181).  
**CRITICAL CLEANUP:** The **next ChatGPT session MUST delete this file from that same branch before merging PR #181**, once it has read, verified and incorporated the useful current state into the existing durable [ChatGPT handover](https://github.com/interzettel/kushluk/blob/main/coordination/agents/chatgpt/HANDOVER.md), normal PR descriptions/issues or its conversation. Do not delete `coordination/agents/chatgpt/HANDOVER.md` (permanent), the collective memory files, other agents' handovers, source website files, or any unrelated A2A code. Read this entire temporary file first; confirm the removal is visible in the branch diff. Use a focused GitHub file deletion via the current blob SHA rather than risky cleanup scripts.

## 0. Why a new session is necessary

The founder explicitly requested handover to prevent loss of working context while the three-agent local council is under construction and ChatGPT focuses on **Phase II**, the **public Decision Atlas and GitHub Pages**. The founder wants this temporary handover removed after successful takeover, so the repository does not accumulate session dumps. This file is a snapshot of a ChatGPT session, **not persistent background work**; when you resume, check live GitHub instead of trusting time-sensitive status here.

**User's operative direction:** Continue Phase II **in parallel** with a separate agent developing the local Agent Council; **wait** to launch synchronized three-AI debates until genuine live model adapters and consent are ready. Do not interfere with that other agent's branch or local runtime. The founder values extraordinary editorial/print design, editable vector-first assets, user-owned sources, finite reading, multiple selectable layouts, and explicit high-level product decisions more than raw engineering throughput.

## 1. Repository and authority map

- Main repository: [`interzettel/kushluk`](https://github.com/interzettel/kushluk).
- **main verified at time of checkpoint:** `fe25c90fa14e6875845074247a8a2b75e19e249c`; verify live HEAD.
- Root `AGENTS.md` document precedence applies first. Accepted [collaboration constitution](https://github.com/interzettel/kushluk/blob/main/docs/coordination/CONSTITUTION.md) via [merged PR #178](https://github.com/interzettel/kushluk/pull/178), then durable restart/handovers via [merged PR #179](https://github.com/interzettel/kushluk/pull/179).
- Founder product north star [#170](https://github.com/interzettel/kushluk/issues/170). Central strategy discussion [#157](https://github.com/interzettel/kushluk/issues/157), three-peer governance + other A2A agent status [#176](https://github.com/interzettel/kushluk/issues/176); [master issue catalogue #43](https://github.com/interzettel/kushluk/issues/43), [release/feature owner #87](https://github.com/interzettel/kushluk/issues/87).
- Initial substantive discussion rooms: [#171 variable-length paper](https://github.com/interzettel/kushluk/issues/171), [#172 prompt-directed aesthetic](https://github.com/interzettel/kushluk/issues/172), [#173 authorized user sources](https://github.com/interzettel/kushluk/issues/173). ChatGPT has already posted its own attributed facilitator/continuation views. Claude Code and DeepSeek genuine independent responses remain **unverified**. Don't present a new ChatGPT chat as a second independent vote.
- Binding today: accepted ADR 0013 exactly four logical A4 pages; ADR 0008 deterministic rendering; ADR 0015 replaceable agent/orchestration; existing code MIT license. The duplicate accepted ADR 0012 conflict remains under [#44](https://github.com/interzettel/kushluk/issues/44); licensing discussion [#38](https://github.com/interzettel/kushluk/issues/38). The founder's future variable-length/prompt-driven vision does **not** silently supersede these.
- Permanent ChatGPT restart prompt: [`coordination/restarts/chatgpt-work.md`](https://github.com/interzettel/kushluk/blob/main/coordination/restarts/chatgpt-work.md); shared handovers/collective assumptions/decisions/dissent under `coordination/`. **Some merged docs still have stale PROPOSED text**: draft [PR #180](https://github.com/interzettel/kushluk/pull/180) corrects statuses alongside a neutral discussion packet. Avoid independent edits that conflict with that PR.

## 2. Main ongoing project — Phase II / read-only GitHub Pages Decision Atlas

**Active branch** `site/decision-atlas-pages-v1` → **draft [PR #181](https://github.com/interzettel/kushluk/pull/181)**.  
**PRE-HANDOVER PR HEAD** `e3b71545e5791e68200c1516316810cd81ad4dc3`. Creating this temporary file moves the branch HEAD; **the next agent MUST query the new head and its own checks**, not reuse `e3b71545` for merge.  
**PR status at latest check:** open, draft, NOT merged. Base main `fe25c90fa14e6875845074247a8a2b75e19e249c`.  
**Project/site:** static public, read-only and visibly dated 19 October 2026, **56 decision nodes and 87 valid cross-links** copied from **separate draft strategy PR #177** without approving that draft's roadmap or architecture changes.

PR #181's permanent deliverables (5 files **before** this temporary handover file):
1. `site/decision-atlas/index.html` — standalone HTML/JS/CSS, frozen embedded JSON; branch fixes ADR hyperlinks and mobile detail navigation; prominent **PUBLIC PREVIEW** state; optional **on-demand human click** to fetch public issue comments with GitHub REST.
2. `site/decision-atlas/decision-atlas.json` — snapshot matching the embedded data.
3. `tools/check_decision_atlas_site.py` — source equality, graph and links, JS parse through Node if available, public-only behavior/CSP and no automatic issue polling; latest source adds checks for valid ADR links and mobile inspector visibility.
4. `.github/workflows/decision-atlas-pages.yml` — PR validation; **real deploy on merged main only**, using official configure/upload/deploy Pages Actions, `pages:write`/`id-token:write` in deploy job, `github-pages` environment. A PR success of workflow `Publish Decision Atlas (GitHub Pages)` means **only its verify job** passed: its deploy job is intentionally **skipped** for pull requests.
5. `site/README.md` — release requirements, public-data boundary, privacy policy and optional read-only future Agent Council integration contract. Read this in full before implementing.

**Live verification at checkpoint:** for PR HEAD `e3b71545...`:
- `Publish Decision Atlas (GitHub Pages)` run [#39285916007](https://github.com/interzettel/kushluk/actions/runs/39285916007): overall **SUCCESS**; verify job passed; deployment **SKIPPED** (because PR).
- `Project health` [#39285915813](https://github.com/interzettel/kushluk/actions/runs/39285915813): Python 3.12 passed, 3.11 running at last check.
- `CI` [#39285916103](https://github.com/interzettel/kushluk/actions/runs/39285916103): test + Linux 3.11 packaging + Intel macOS passed; other Linux/macOS packaging jobs still in progress/queued. **NOT all-green at checkpoint**.
- Earlier PR #181 base iteration's validation and full CI/project health reportedly passed; new code commit `e3b71545` **restarted** checks. Do NOT merge based on previous head successes.
- **No verified public GitHub Pages URL or HTTP page load** yet. Candidate default GitHub Pages URL is `https://interzettel.github.io/kushluk/` but this is **not confirmed live**; the actual deploy job's `page_url` and HTTP result are decisive.
- GitHub connector **does not expose Pages admin settings writes** (nor permitted Pages settings status URL). Founder may need [Settings → Pages](https://github.com/interzettel/kushluk/settings/pages) → Build and deployment → **Source: GitHub Actions**. Do not pretend this was set. Use standard GitHub Actions credential, not a PAT or local council token.

**Security boundary:** no secret/public private sources, no embedded GitHub auth, no local host requests, no model execution; only optional human-click unauthenticated public `api.github.com` GET, comment bodies rendered using `textContent`, not HTML. The public site is a static **dated proposal**, not an automatically live governance dashboard. Future project/decision status sync requires an authorized source-data review and explicit owner decision. Do not merge strategy [#177](https://github.com/interzettel/kushluk/pull/177) merely to deploy this isolated preview.

**Already posted authoritative progress notes:** central [#157](https://github.com/interzettel/kushluk/issues/157#issuecomment-6271726084) and PR [#181 handoff](https://github.com/interzettel/kushluk/pull/181#issuecomment-6271796817). A later #157 note reported ADR/mobile improvements and current CI restart; inspect latest issue comments for exact link. Do not spam GitHub with routine status comments unless new evidence exists.

## 3. Immediate next steps for resumed ChatGPT session (in order)

1. **Fetch this exact file** on `site/decision-atlas-pages-v1` and read it fully; inspect root `AGENTS.md`, approved constitution, `coordination/README.md`, permanent ChatGPT handover and the relevant PRs/issues.
2. **Recheck live state** of [#181](https://github.com/interzettel/kushluk/pull/181): fresh HEAD, open/draft/mergeability, check runs **for that exact SHA** (note: the temporary handover commit itself can restart PR checks). Inspect CI job failures, especially `tools/check_decision_atlas_site.py`, before any merge.
3. Once PR #181's actual code HEAD is clean, **remove THIS TEMPORARY FILE** with an exact branch `delete_file` call and fresh blob SHA from `fetch_file`; this produces a new HEAD, thus **recheck final CI once more**. This is a requirement from the owner: **do not leave temporary handovers in merged main**. If the new session needs context before deleting, capture it in that conversation or **append only nonredundant verified state to permanent `coordination/agents/chatgpt/HANDOVER.md` on a separate reviewed update**, not inside this deployment PR.
4. Validate Pages site on desktop/mobile, keyboard navigation, focus visibility and safe public issue comment rendering. Automated checks passed on one PR code head, but a genuine browser visual/a11y inspection **has not been completed**; don't claim otherwise.
5. After **all checks are green** and any needed founder review/approval for public deployment is satisfied, **ready/merge** PR #181. The user's request to start Phase II and publish the public atlas authorizes working toward deployment but earlier messages didn't explicitly authorize bypassing design/safety review; prioritize conservative assessment. Deploy job should then run on `main`. Check actual deployment logs, Pages setting and URL; **do not announce a live site until HTTP/browser check succeeds**. If Pages source setting still needed, give precise one-click path and ask owner.
6. After live deployment, propose a scoped Phase II continuation: accessible mobile refinement; deliberate public GitHub issue status freshness without misrepresenting dynamic truth; consider a **future read-only bridge** to the agent council after actual model runtime adapter is validated. No automated polling or exposure of the user's local Agent Council via public Pages.
7. [PR #180](https://github.com/interzettel/kushluk/pull/180) remains a separate **draft** neutral first-round packet (head at snapshot `e7a6f7084fc89466e3277a3132b4365bc452b39c`); verify its status independently, keep separate from Pages. PR #177 remains a separate design/strategy **draft**. Phase III future: audit/install 4 canonical Stiprā skills (`.agents/skills` not just Claude shims) for each actual compatible runtime, license/sandbox first; Phase IV future: content→semantic model→editable vector/photo styles→safe deterministic composer → bounded editions, subject to accepted decisions.

## 4. Parallel Agent Council work (do NOT take over)

Other repo [`interzettel/agent-council`](https://github.com/interzettel/agent-council): [draft PR #1](https://github.com/interzettel/agent-council/pull/1) (was open, HEAD `41baa58c19e22228101c682e2cc42b86d8c2dc7c`), [issue #2](https://github.com/interzettel/agent-council/issues/2) open and owned by **another agent + founder's local testing**. Reported local foundation: **9/9 pytest, 21/21 HTTP checks**, real model adapters **0** at that report. Windows Low-integrity pip/temp workaround used by local DeepSeek operator; no application code/Git history change from that fix was reported.

Issue #2 goal: standalone **opt-in DeepSeek main-agent adapter**, targeted `@deepseek` inbox only, no autonomous code/repo changes, no Claude/Codex wakeups, no paid inference without owner authorization, fake-runner first then **one genuine read-only** model response if actual unattended CLI exists and is authorized. Board is localhost `127.0.0.1:8130`; reported browser UI includes notifications, advisory exclusive claims and self-reported quota; this is **not** proof of validated provider quota data or genuine model execution. A2A subset simulator is a different layer from real model adapter. Don't edit Agent Council code/claims/database or touch the user's workstation; no cross-repo merges.

Founder already asked to **wait** for real model adapters before restarting three-way AI discussions. The Kuşluk GitHub discussion rooms and restart prompts are ready but cannot be claimed to operate autonomously. **Public Decision Atlas must NEVER directly fetch localhost Agent Council (inaccessible from GitHub Pages and a privacy boundary).** If later connection desired, define an explicit, redacted, secure, opted-in export/public bridge and deliberate authorization.

## 5. Cleanup instructions (essential!)

Before merging #181, obtain fresh content blob SHA:

```text
GitHub fetch_file:
  repository_full_name = "interzettel/kushluk"
  ref = "site/decision-atlas-pages-v1"
  path = "coordination/agents/chatgpt/TEMP_PHASE2_HANDOVER_2026-10-19.md"
```

Then invoke GitHub `delete_file` on **this exact path and branch** with its `sha`, message `chore: remove consumed temporary Phase II session handover`. Confirm the deleted file returns 404 on the branch and check #181's changed files **no longer includes this path**. Recheck CI for the last head. Never remove `main`'s permanent `HANDOVER.md`, accepted constitution or collective memory folders. If deletion cannot be performed, **do not merge PR #181 with this temporary file**; explain the blocker to the owner.

**New-session work begins only when a real user starts it. This handover does not constitute a scheduled task, Agent Council message, GitHub Pages deployment or communication to Claude/DeepSeek.**
