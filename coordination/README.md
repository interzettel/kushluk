# Kuşluk — three-peer collaboration workspace

**Status:** Step 2 durable files **MERGED** on 2026-10-19 via [PR #179](https://github.com/interzettel/kushluk/pull/179); actual multi-model sessions are not yet verified.  
**Canonical protocol:** [docs/coordination/CONSTITUTION.md](../docs/coordination/CONSTITUTION.md), accepted in [PR #178](https://github.com/interzettel/kushluk/pull/178). This directory is **working memory and restart support**, NOT a second issue tracker, an A2A server, a live model session or an automatic GitHub issue subscriber.

## What lives where

| Area | Purpose | Authority |
| --- | --- | --- |
| `agents/chatgpt/HANDOVER.md` | ChatGPT's own **attributed** observed work, concerns and next handoff | Self-reported; verify commits/links |
| `agents/claude/HANDOVER.md` | Claude's own environment, independently observed progress | **Uninitialized** until actually written by Claude |
| `agents/deepseek/HANDOVER.md` | Local DeepSeek's own checked-out code, tests and observed hardware constraints | **Uninitialized** until actual user-run DeepSeek produces it |
| `collective/ASSUMPTIONS.md` | Hypotheses, current support, owner, falsification/revisit conditions | NOT accepted ADRs |
| `collective/DECISIONS.md` | Pointer-only register of **recorded human/accepted** decisions | Actual founder verdict/ADR/merged PR controls |
| `collective/DISSENT.md` | Known **substantive questions and open dissent**, not imaginary peer disagreements | Review comments in owning issues |
| `collective/DISCUSSION_QUEUE.md` | Bounded decision discussion concurrency and prerequisites | Issues #171–#176 and #157 own discussion state |
| `restarts/` | Three distinct bootstrap prompts for Work, Claude Code and user-run DeepSeek | Instructions, not proof of execution |
| `sessions/` | Optional append-only per-round receipts and links | Create only after a real round; no fabricated logs |

## First boot (each peer)

1. Read root `AGENTS.md` and [the accepted constitution](../docs/coordination/CONSTITUTION.md); inspect current `main` SHA.
2. Inspect this index and the agent's **own** handover; note if `UNINITIALIZED` or `STALE`.
3. Read [collective assumptions](collective/ASSUMPTIONS.md), [recorded decisions](collective/DECISIONS.md), [dissent](collective/DISSENT.md) and [discussion queue](collective/DISCUSSION_QUEUE.md). Revalidate against current GitHub issues/ADRs; cached notes cannot outrank them.
4. Read the appropriate prompt under `restarts/`. **Independently** assess chosen discussion issue before reading other agents' proposed positions where practicable.
5. Identify yourself truthfully in a prospective comment (real runner/model, actual tool access, inspected source commit, independent vs cross-examination phase). Publish only with authorized GitHub access and consent.
6. After substantial work or context exhaustion, update **your own** handover with verified receipts, evidence boundaries, blockers and next safe task. Don't overwrite another runtime's memory or claim its signoff.

## Guardrails for concurrent work

- Same **decision** may be debated by all three peers; don't allocate permanent “design/engineering/PM/legal” cognitive roles.
- Separate Git worktrees/copies and issue-scoped branches for implementation; no simultaneous writes to the same file without an identified integrator.
- Source code, private user content, source licenses, shared recipes, print devices, spending and actual hosted deployment retain their own explicit permissions.
- **A2A work is being handled independently:** [#176](https://github.com/interzettel/kushluk/issues/176) documents only simulator HTTP transport evidence so far. This Step 2 directory does not touch, install or certify that implementation. The assigned A2A agent should choose its own distinct branch/files and reconcile the transport integration after source review.
- Large visual artifacts may live on authorized Drive or private storage **only after** access to that exact destination is verified for each actual runner; use an explicit link + permission/retention record.
- GitHub issue comments are canonical **asynchronous discussion history**, not evidence that an A2A receiver read a message. Avoid commenting in a loop unless you introduce a new fact, objection, rebuttal or falsifying test.

## Shared source anchors

[Owner direction #170](https://github.com/interzettel/kushluk/issues/170) · [Decision council #157](https://github.com/interzettel/kushluk/issues/157) · [A2A and peer policy #176](https://github.com/interzettel/kushluk/issues/176) · [R6 variable length #171](https://github.com/interzettel/kushluk/issues/171) · [R7 prompt design #172](https://github.com/interzettel/kushluk/issues/172) · [R8 private source intake #173](https://github.com/interzettel/kushluk/issues/173) · [Feature/release authority #87](https://github.com/interzettel/kushluk/issues/87) · [Issue inventory #43](https://github.com/interzettel/kushluk/issues/43) · [Licensing #38](https://github.com/interzettel/kushluk/issues/38).

**Verified Step 2 merge:** `fe25c90fa14e6875845074247a8a2b75e19e249c` ([PR #179](https://github.com/interzettel/kushluk/pull/179)); inspect the **live** HEAD because it may have changed. First-round unbiased primary-source packet: [2026-10-19-W1](rounds/2026-10-19-wave1/SOURCE_PACKET.md). Unmerged draft strategy PRs #169/#177 remain proposals as last checked.
