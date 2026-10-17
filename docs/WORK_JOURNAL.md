## 2026-10-17 — Opt-in printer preference after local preflight

**Kind:** onboarding engineering. **Issue:** #5 (UX-01). **State:** proposed implementation, awaiting CI and review in the linked PR.

- Connects a deliberately checked local CUPS queue to an existing private profile via an explicitly confirmed, printer-only update. The initial home profile remains create-only.
- Negative tests cover missing prior scan/check, stale selection, CSRF/Origin/Host, missing profile, symlinks, non-private files, and preference preservation.
- No printing, driver installation, automatic delivery or release-gate claim. Actual reader observation, paper, e-reader and unattended-host trials remain outstanding; progress percentages and hardware gates unchanged.

# Kushluk work journal

A concise, dated evidence/history record for one maintainer with AI helpers. **This is not an activity-time tracker or a substitute for GitHub commits and discussions.**

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
