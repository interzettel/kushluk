# Kuşluk collaboration constitution — three generalist AI peers and one accountable founder

**Status:** FOUNDER-APPROVED collaboration procedure, merged via [PR #178](https://github.com/interzettel/kushluk/pull/178) on 2026-10-19. This document is a **collaboration procedure**, not an accepted architecture ADR, a release authorization, a model integration or an Agent2Agent transport implementation.  
**Founder mandate:** [#170](https://github.com/interzettel/kushluk/issues/170) · **Operating-model debate:** [#176](https://github.com/interzettel/kushluk/issues/176) · **Discussion index:** [#157](https://github.com/interzettel/kushluk/issues/157).

## 1. Purpose and permitted debate

Three proposed participants—**ChatGPT Work**, **Claude Code**, and **user-operated local DeepSeek**—act as **broad reasoning peers**. Every participant may critically assess the product vision, art direction, architecture, user research, privacy, copyright, licensing, finance, testing, project management and sequencing. There are **no permanent Designer/Architect/PM/Tester AI silos**. Different tool access is a capability disclosure, not a rank or authority grant.

The founder is the accountable product steward and final editor of strategic decisions. The founder may overturn a past product decision **by explicitly approving a new decision and the required migration**, not by pretending the historical decision never existed. An AI proposing alternatives is not acceptance, and three AI opinions are **not a binding vote**.

## 2. Authority and truth hierarchy

Read the existing root [AGENTS.md](../../AGENTS.md) and its **Documentation precedence** section first. Do not establish a competing order here.

| Question | Authoritative location | Important status distinction |
| --- | --- | --- |
| Enduring owner intent and new proposals | [#170](https://github.com/interzettel/kushluk/issues/170) and founder verdicts on owning decision issues | Vision affirmed; conflicting code constraints still require formal change |
| Current implementation contracts | Accepted [ADRs](../adr/README.md), then [REQUIREMENTS.md](../REQUIREMENTS.md), PRODUCT/ARCHITECTURE/EDITORIAL docs in root AGENTS order | Accepted ≠ merely proposed |
| Why/where a question is debated | [#157](https://github.com/interzettel/kushluk/issues/157) and discussion rooms [#158–#162](https://github.com/interzettel/kushluk/issues/158), [#171–#176](https://github.com/interzettel/kushluk/issues/171) | Opinions/dissent ≠ decision |
| All GitHub issue records | [Master catalogue #43](https://github.com/interzettel/kushluk/issues/43) | Dated snapshots; verify current records |
| Approved feature/version plan | [#87](https://github.com/interzettel/kushluk/issues/87), [FEATURE_CATALOG.md](../FEATURE_CATALOG.md), [RELEASE_PLAN.md](../RELEASE_PLAN.md) | PR #169 remains a draft proposal |
| Executable tasks and independent acceptance | [WORK_LEDGER.md](../WORK_LEDGER.md), ISSUE_CROSSWALK, [PROGRESS.md](../PROGRESS.md) and real CI/device evidence | An opened/closed issue is not a checked task or G1–G8 acceptance |
| Proposed strategic map and impact paths | [Draft PR #177](https://github.com/interzettel/kushluk/pull/177), decision atlas data and visual tree | A snapshot; no live sync or accepted authority implied |
| Existing code licensing and original creative rights | Current repository LICENSE, [#38](https://github.com/interzettel/kushluk/issues/38), per-source/asset permissions | Licence discussion does not relicense MIT code |

**Known normative conflicts:** the two **accepted ADR 0012** documents require the explicit [#44](https://github.com/interzettel/kushluk/issues/44) resolution. Accepted **ADR 0013** and REQUIREMENTS currently prescribe **four logical A4 pages**; a finite, variable-length edition is founder intent and an open [R6 #171](https://github.com/interzettel/kushluk/issues/171) proposal, *not* shipped behavior. **ADR 0008** and **ADR 0015** preserve deterministic Kuşluk-owned production and agent/orchestrator replaceability; prompt-driven themes [R7 #172](https://github.com/interzettel/kushluk/issues/172) must respect that until an explicit approved amendment.

## 3. Human, peer, and tool permissions

- **Founder:** sets priority and product quality bar; rules ACCEPT / AMEND / EXPERIMENT / DEFER / REJECT on consequential decisions; authorizes credentials, costs, external publishing, hardware actions, policy/architecture/licensing changes and releases.
- **Any AI peer:** reads allowed sources, independently challenges all options, writes attributed opinions, conducts reproducible non-sensitive experiments within authorized scope, prepares draft branches/PRs, and corrects its own errors.
- **Temporary task owner/integrator:** coordinates conflicting **files and actions**, not knowledge domains or who may argue. A Claude coding checkout does not make Claude the exclusive engineering reviewer; a ChatGPT Work browser does not make ChatGPT the exclusive product strategist.
- **Independent verification:** a model cannot self-award human aesthetic approval, legal permission, third-party agreement, production print success or independent delivery gates from a passing CI job.

**Explicit approval required** before reading private mailbox content, sharing user content with a provider, spending money, accessing third-party private accounts, enabling recurring monitoring, posting on behalf of another AI, installing executable skills/plugins, changing root licences, deploying a production service, auto-merging, or sending print/email jobs. Read-only GitHub inspection does not imply permission to do those things.

No agent may say it contacted another participant, synchronized their memory, invoked a connected tool, ran a local harness, or installed an integration unless it actually did and can link evidence.

## 4. Review exchange and provenance

One consequential decision = one **owning GitHub issue thread**, not a new parallel chat thread or a new issue per observation.

The standard review lifecycle is:

1. **Intake:** name the decision ID and issue; classify observed contradiction vs implementation gap vs proposal; supply current source commit, accepted ADR, affected F-IDs/task IDs/release.
2. **Independent round:** each participating AI reads the **same frozen source packet**, forms a position *before seeing the others' recommendations where practicable*, and posts its own attributable first-pass comment. Disclose exact model/runner and actual access; never fabricate attribution or claim a review was independent when it borrowed another's position.
3. **Cross-examination:** read the other attributable reviews, quote their strongest valid arguments, expose conflicting assumptions and modify recommendations openly. Preserve dissent instead of synthesizing false consensus.
4. **Founder ruling:** founder records a specific outcome, reason, boundaries, rejected alternatives, and evidence still required.
5. **Execution:** for a reversible experiment, isolate a branch and measure; for accepted durable behavior, prepare an ADR or documented contract migration before changing production semantics.
6. **Closure:** update the owning issue, linked authority documents, feature and original task mappings only where actually warranted. A review cycle is *not* a completed implementation.

Suggested fields for each comment: `reviewer`, `model/runner`, `phase`, `timestamp`, `source_commit`, `observed_facts`, `assumptions`, `options`, `preferred_option`, `strongest_objection`, `falsifying_test`, `affected_authorities`, `requested_founder_decision`. Use [REVIEW_TEMPLATE.md](REVIEW_TEMPLATE.md).

**Anti-loop:** do not have models repeatedly ask one another for permission or trigger reciprocal mentions indefinitely. A response must introduce a *new source, concrete objection, test result, changed position or owner question*. Otherwise mark `NO NEW EVIDENCE` and pause. No claim of universal “three-AI consensus” from an incomplete round.

## 5. Agent2Agent transport versus durable discussion

The proposed Agent2Agent (A2A) interoperability layer is a **future, separately verified integration**. A shared Markdown file or GitHub comment is not A2A protocol compliance. When implemented, transport must be evaluated for identity/discovery, task identifiers, state transitions, messages/artifacts, authenticated authorization, replay/idempotency, cancellation, bounded timeouts, and traceable source/issue IDs. Verify actual compatibility with each chosen ChatGPT Work/Claude Code/local DeepSeek environment; none is assumed.

**Current usable fallback:** the public GitHub issue is the canonical asynchronous discussion thread. Human or explicitly authorized agent transfers prepared messages between environments. A model can create a handover artifact without implying the other runtimes received it.

## 6. Memory, handovers and shared assumptions

Individual agent session memory is **not** collective evidence. The durable Step 2 workspace at [coordination/README.md](../../coordination/README.md) (merged via [PR #179](https://github.com/interzettel/kushluk/pull/179)) has these distinct storage surfaces:

- `coordination/agents/<runtime>/HANDOVER.md`: what that runtime actually did, environment/commit, limitations, own unresolved hypotheses and next safe action;
- `coordination/collective/ASSUMPTIONS.md`: attributed hypotheses with provenance, confidence and invalidation condition; **not accepted facts**;
- `coordination/collective/DECISIONS.md`: index of **actual** founder rulings and accepted ADR links, not reconstructed votes;
- `coordination/collective/DISSENT.md`: unresolved objections and their status;
- `coordination/sessions/<date-id>/`: optional bounded snapshots and artifact links.

These paths are now **versioned repository files**, not synchronized cross-model memory or a transport service. The actual Claude and DeepSeek runner handovers remain uninitialized until they write attributed evidence. Never put API keys, private email/article bodies, personal home details, proprietary subscriptions, or raw unlicensed images into public repo memory. Use GitHub issue links and private artifact destinations with explicit access controls. Google Drive can hold authorized large visual evidence if real access is confirmed for **each** runtime; do not assume three-way connectivity merely because a human has a Drive.

A session handover must specify **observed vs inferred**, source commit, known blockers, pending founder verdicts, active PRs, status of relevant tests and *what it did not do*. Restarting a conversation must not turn a preliminary opinion into an accepted decision.

## 7. Design quality, evidence and skills

Physical art direction is a product requirement, not a consequence of successful PDF geometry. Same-content art studies, readable/credited photographic/diagrammatic assets, inexpensive real-paper tests, and explicit owner desirability review precede visual acceptance. Deterministic geometry and factual/source/rights validation remain necessary.

Future design skills (including imports from Stiprā) must be installed **separately** per runtime with full canonical references and scripts, licensing/provenance checks, and sandbox testing. No attached zip, external binary, or plugin is executed or installed by adopting this constitution. Skills provide critique methods; they cannot override an accepted ADR or fabricate editorial material.

## 8. Evidence ladder and bounded delivery

Use exact verbs:

| State | Meaning | Example evidence |
| --- | --- | --- |
| `PROPOSED` | An option is open to discussion | Issue, draft PR |
| `REVIEWED` | Attributed review exists | Dated comment, source commit |
| `DECIDED` | Human outcome recorded | Founder verdict, ADR approval if required |
| `IMPLEMENTED` | Code/asset/contract delivered | Commit, merged PR, test output |
| `VERIFIED` | The claimed effect was actually observed | Reproducible CI, permitted hardware/reader evidence |

`REVIEWED` and `IMPLEMENTED` do not imply `VERIFIED`; `DECIDED` is not necessarily `IMPLEMENTED`. Repo Project Status (`Backlog → Ready → In progress → In review → Done`) is a different field from these evidence meanings and must not be duplicated.

Reversible art experiments may proceed on isolated branches during ongoing hardware trials. Shared schema, license, privacy, source-inclusion and external delivery changes require decisions first. Maintain the current pilot's frozen checkout and do not alter running Windows tasks or printers without explicit approval.

## 9. Immediate next stages (not installed here)

**Step 1 (completed, PR #178):** founder approved and merged the shared constitution and source-authority reconciliation.

**Step 2 (workspace merged, PR #179):** handover files, collective assumptions and restart briefs exist; genuine Claude/DeepSeek introductions and independent peer reviews have NOT been verified. Use the first-round facts-only packet under `coordination/rounds/`.

**Step 3:** test actual Agent2Agent messaging against each runtime and live atlas/Pages deployment; prove end-to-end identity and resilience before recurring monitoring.

**Step 4:** independently install/audit each design skill and locally test Adaptive UI in disposable environments; only then begin approved prompt→recipe/image/vector transformation experiments.

**No automated peer meetings, A2A bridge, GitHub Pages deployment, Drive sync, monitoring or skills installation is claimed by Step 1.**
