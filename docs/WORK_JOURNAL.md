# Kushluk work journal

A concise, dated evidence/history record for one maintainer with AI helpers. **This is not an activity-time tracker or a substitute for GitHub commits and discussions.**

## 2026-10-17 — User-owned Google grants and narrow DOI evidence checks

**PR #119** adds a desktop local OAuth flow with separate least-privilege `gmail.metadata`/`tasks.readonly` grants; limited Gmail header-only source review, optional real Google Tasks candidate generation, token-mode validation and explicit local disconnect. No remote credential or mail contents are stored in the repo.

Crossref `crossref-check` tests exact DOI title/year metadata, disputes mismatches and abstains when missing/unavailable; does not claim independent verification of research conclusions. Hermetic security tests include malformed scopes, private token files, limited provider request fields, denied redirects, malicious private data and safe error codes. **No live Google OAuth token/user mailbox was accessed**; real acceptance remains evidence-gated.

**Ledger 26/90 (28.89%) unchanged** until real authorized-provider and independent claim reviews. G1–G8 0/8, package v0.1.0.

## 2026-10-17 — Local tasks, public research pointers, bounded newsletter source review

**Issues:** #49 task/public research; #48 newsletter discovery; #16 provenance and trust. **Stage:** PR #118 awaiting final cross-platform merge CI; no private inbox, paywalled provider or verified-claim entitlement claimed.

- Add owner-exported replaceable local task connector for dated incomplete tasks, bounded file size/schema and source-safe errors.
- Add explicit opt-in Crossref DOI/title/date public metadata adapter, using hostname-pinned HTTPS fetch, URL redaction, and reference-only mode; scholarly titles are not accepted as verified claims.
- Persist original candidate source IDs, safe URLs, originating and retrieval time, transform and rights mode through clustering and published story metadata. Titles that differ remain flagged for human verification.
- Add local header-only discovery and explicit mode-review CLI; proposals are owner-local/private and never activate copying or synthesis. All four modes remain disabled for live ingestion.
- Software task evidence SRC-03/04/07 checked **26/90 (28.89%)**, SRC **3/10**. No hardware/evidence gate advanced (G1–G8 0/8); #16 cost and real provider verification remain outstanding.

## 2026-10-17 — Permission-gated print images and offline original artwork proof

**Issues:** #50 media pipeline, #21 print, #4/#16 source rights/security. **State:** PR #117 implementation under final CI review; no physical/legal acceptance.

- Add v1 normalized SHA-256 local media asset records with owner-granted scope, source provenance, credit/caption/alt and bounded focal/contain policy; never infer RSS rights or automatically download photographs.
- Implement explicit local `media-import`/`media-info`/`media-assign`/`media-remove` and `KUSHLUK_MEDIA_DIR` opt-in; private local bindings to selected story IDs, no automated third-party acquisition.
- Add deterministic 66×33 mm print lead slots with >=180 effective DPI preflight; inline approved PNG data URI and attribution. Failing records/under-resolution fall back to the story's text. Archive approved normalized crop and immutable placement metadata for repeatability.
- CI/test portfolio generates original synthetic portrait/landscape/square media fixture PDFs and checks bad/tiny/missing/invalid license, duplicate, symlink, altered content, contain and focal behavior; **no real printer/provider/legal claims**.
- Check IMG-01,04,05,06,07,08 on software evidence only: **23/90 · 25.56%**; IMG-02/03/09 and RES-IMG-01 remain open; G1–G8 remain 0/8, release version unchanged.

## 2026-10-17 — Typed editorial composition and three fixed-edition PDF variants

**Issues:** #51 semantic composer and #21 print engine. **State:** PR #116 implementation under cross-platform acceptance review; **not** a hardware or visual design approval.

- Implement finite archetype choice and typed semantic slot capacities; preserve source IDs and EPUB-compatible default publication structure while enabling auto-choice from the live pipeline.
- Implement reason-coded shorten, move, demote, replace, omit and unapproved-image removal; mandatory calendar/task overcapacity is a hard failure, not a hidden deletion.
- Implement practical half-width WeasyPrint-safe grid, six-column news layout, Unicode-safe copy limits and automated per-page text boundary/footer/font-size checks.
- Generate three offline comparison PDFs from one immutable synthetic edition on both macOS CI architectures, with source/slot decision manifest. A4/A3 imposition, rights and physical printer assertions are **not** automatically advanced.
- Software-only reconciliation: LAY-02/04/05/07 checked (4), ledger **17/90 = 18.89%**, eight release evidence gates **0/8**. LAY-01/03/06/08/09 and FMT-03 explicitly remain incomplete.

## 2026-10-17 — Observed stage metrics and readiness-planning software

**Issue:** #47 · AUT-09/AUT-12 partial work · **Status:** implementation in review pending CI, not a real-host trial.

- Add bounded timestamped stage events and UTC/local cutoff comparison for validated-and-archived PDF readiness; CUPS/SMTP submission remains distinct from physical/recipient delivery.
- Add read-only `run-report`, `timing-plan` and matching v1 `report`/`timing_plan` operations. Require >=3 valid historical completed, archived receipts for p90 latency + explicit margin; insufficient history returns no proposed start. No native scheduler is changed or enabled.
- Synthetic multi-date fixture tests for interrupted/paused/deadline/replay behavior; prevent stale/unvalidated/tampered receipt data from contributing to schedule advice.
- AUT-09/AUT-12 and real five-morning G3 acceptance remain open; **13/90 = 14.44%** ledger, 0/8 evidence gates and 0.1.0 unchanged.

## 2026-10-17 — Native host recipes and safe recovery-status test slice

**Scope:** #47 AUT-05 software slice; AUT-09/12 follow-up. **State:** implementation in review until CI is green; no physical deployment.

- Generate disabled, create-only, private systemd user timer/service and macOS LaunchAgent from explicit local binary/workdir and configurable schedule times; no paid/orchestrator dependency, no service install or print autoactivation.
- Add source/render/PDF lifecycle milestones to typed `scheduled.json` stage history; Linux/macOS file-lock distinguishes a live run from a stale after-crash receipt, with continued at-most-once semantics.
- Test synthetic repeated/abandoned/in-progress runs, tampered diagnostic fields and scheduler file safety; preserve separate human host/reboot/08:00-ready proof.
- Add execution acceptance matrix to #47, WORK_LEDGER.md and NATIVE_SCHEDULERS.md. Software task reconciliation: AUT-05 checked, **13/90 = 14.44%**; G1–G8 unchanged (0/8).

## 2026-10-17 — Versioned local run controls, deadline and pause contract

**Issue:** #47. **Scope:** first stable local JSON operations boundary, consent safety and local-date controls. **State:** implementation in PR under CI review, no host acceptance.

- Implement schema-v1 run/status/pause/resume/archived-delivery operation adapter; reject unknown JSON fields, malformed dates/clocks, wrong booleans or missing explicit print/email/reprint consent.
- Add `--latest-start HH:MM` to scheduled CLI as last permissible start, and owner-private date-scoped pause marker/fail-closed resume. Pre-existing receipts cannot be bypassed by revised dates, pauses or accidental reprints; active jobs are not cancelled.
- Reconcile AUT-01 and AUT-03 only as software evidence (12/90, 13.33%); leave AUT-05/09/12 and all eight real-world gates open. Document repeat-safe native scheduler usage and remaining pause/start concurrency limitation.
- No device/host deployment, automatic print activation, external paid orchestration, version or release change.

## 2026-10-17 — Privacy-safe failures, hermetic CI and evidence reconciliation

**Issues:** #54 (CI/security), #44 (documentation), #45/#46 (FMT software), #47 (AUT software); implementation in PR under review.

- Replace raw connector/renderer exception text and CUPS/SMTP subprocess/provider diagnostics with bounded safe status messages. Add fake-token regression tests for persisted edition/run/CLI output and transport receipts.
- Replace live weather/RSS CI smoke generation with deterministic source fixtures, socket deny, disabled printer/SMTP and a real CLI path; macOS still verifies four-page PDF.
- Reconcile exactly six previously unchecked FMT/AUT tasks based on software evidence: FMT-01/02/06/07 and AUT-02/10. Regenerate ledger, progress report and SVG to **10/90 (11.11%)**; leave G1–G8 at **0/8 (00.00%)**. Correct obsolete AGENTS, roadmap and status descriptions and real issue priority labels (#44 P0, #45–#51/#54 P1).
- Remaining: real host/printer, visual overflow/fold preflight, deadline controls and independent reader/device proof. No release/version change.

## 2026-10-17 — First-reader synthetic path and observer preflight

**Kind:** onboarding QA + privacy-safe evidence tooling. **Issue:** #5 (F-008 / UX-01). **State:** implementation in PR awaiting CI; no independent reader claim.

- Added an end-to-end **synthetic** U1–U6 loopback journey regression with fake CUPS, fictional sources, explicit consent, pause/resume and printer preference persistence.
- Added local-only observer-record completeness preflight, private handoff instructions and consistent ASCII Kushluk setup mastheads.
- Actual first-reader observation, keyboard/assistive-technology study, physical printer/e-reader and unattended host acceptance remain unperformed. No acceptance gate/percentage or released version changes.

## 2026-10-17 — Opt-in printer preference after local preflight

**Kind:** onboarding engineering. **Issue:** #5 (UX-01). **State:** proposed implementation, awaiting CI and review in the linked PR.

- Connects a deliberately checked local CUPS queue to an existing private profile via an explicitly confirmed, printer-only update. The initial home profile remains create-only.
- Negative tests cover missing prior scan/check, stale selection, CSRF/Origin/Host, missing profile, symlinks, non-private files, and preference preservation.
- No printing, driver installation, automatic delivery or release-gate claim. Actual reader observation, paper, e-reader and unattended-host trials remain outstanding; progress percentages and hardware gates unchanged.

## 2026-10-16 — Solo project operations and editorial entrypoint

**Kind:** project-system design + documentation proposal.  
**State:** historical proposal at time of writing. **Later on 2026-10-16 all four reviewed PRs #53, #55, #27 and #61 were merged into `main`; see consolidation receipt below.**

- [#54](https://github.com/interzettel/kushluk/issues/54) and [PR #55](https://github.com/interzettel/kushluk/pull/55): introduced initial offline task inventory, eight evidence gates, generated Markdown, tracker CI, PR/issue templates and contributor guidance. The PR head's CI was verified green before the later stacked work began.
- [#59](https://github.com/interzettel/kushluk/issues/59): proposed a simplified solo-maintainer intake and Kushluk-branded progress visualization, adapting parts of the owner's [website ledger](https://github.com/interzettel/yigitdenktasdotcom/blob/main/progress/progress.json).
- [#60](https://github.com/interzettel/kushluk/issues/60): started a revised README that distinguishes one-page working skeleton, accepted four-page design, and future research; official user-facing name **Kushluk**.
- [#56](https://github.com/interzettel/kushluk/issues/56): research queued for L0–L5 + R0–R4 readiness from [personal-agent-stack](https://github.com/interzettel/personal-agent-stack/tree/main/docs/agent-readiness), not yet assessed.
- [#57](https://github.com/interzettel/kushluk/issues/57): Dependabot/dependency maintenance research queued; no configuration enabled yet.
- [#58](https://github.com/interzettel/kushluk/issues/58): Grok/Hermes/Claude/OpenCog adapter compatibility investigation queued; no runtime certified.
- [#43](https://github.com/interzettel/kushluk/issues/43) remains the issue index; #53 remains the independent ADR/task crosswalk review.

**Proof boundary:** a generated dashboard reflects current ledger checkboxes, not product maturity. Actual real-printer acceptance, private subscriber content use and legal/commercial licensing remain unverified or undecided.

## 2026-10-16 — Merge and issue governance consolidation

**Kind:** verified repository merge and stewardship-policy change.  
**State:** merged and verified on `main`.

- Merged [PR #53](https://github.com/interzettel/kushluk/pull/53) (90-task crosswalk and ADR index), [PR #55](https://github.com/interzettel/kushluk/pull/55) (CI/evidence foundation), [PR #27](https://github.com/interzettel/kushluk/pull/27) (paper research), and [PR #61](https://github.com/interzettel/kushluk/pull/61) (ASCII brand, welcoming README, per-task progress and governance policy).
- Official public name **Kushluk**. The original Turkish spelling is retained only as a word-origin note in the README. Source/runtime displays and tests were updated.
- [Main CI run](https://github.com/interzettel/kushluk/actions/runs/38955479295) and [Project health run](https://github.com/interzettel/kushluk/actions/runs/38955479313) both passed on commit `1193a21301205ce91a688a603bf953c237eb6265`.
- All 56 open issues assigned to `@yigit-denktas`; [#60](https://github.com/interzettel/kushluk/issues/60) closed **completed** after README merge. Issue registry [#43](https://github.com/interzettel/kushluk/issues/43) now contains **58 issues (56 open, 2 closed)** exactly once.
- GitHub Project native fields, labels, milestone assignments and relationship backfill remain **unconfigured/unverified** until the owner creates the Kushluk Project: [#62](https://github.com/interzettel/kushluk/issues/62). No false linkage claimed; native issue metadata and future automation require a separate verification.
- Unresolved accepted-ADR 0012 conflict remains in #44. No OSS relicensing, hosted product or autonomous merging approved.

## 2026-10-16 — Owner-created GitHub Project linked

**Kind:** project management integration · **Status:** Project verified, native field configuration in progress.

The owner shared [Kushluk Project #3](https://github.com/orgs/interzettel/projects/3). Its inspected Backlog view contained **56 items**, with Ready, In progress, In review and Done empty. Other available views are Priority board, Team items, Roadmap and My items; the UI reports seven enabled workflows. This is an observation, **not** a proof that every issue has every required custom field or that automations have been inspected. [#62](https://github.com/interzettel/kushluk/issues/62) now tracks remaining metadata, native relationship and workflow verification, while [#43](https://github.com/interzettel/kushluk/issues/43) records the Project URL.

## Journal entry template

```md
## YYYY-MM-DD — One meaningful outcome
Kind: idea | bug | decision | engineering | incident | research
Status: proposed | investigating | accepted | verified | parked | rejected
Issue and task IDs:
Change / decision:
Evidence: commit, passing tests, print sample, ADR, user acceptance
Remaining uncertainty / next action:
```

For minor progress, update the existing issue/PR instead of expanding this file.
