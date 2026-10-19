# Source-of-truth reconciliation — 2026-10-19

**Status:** Evidence-based Step 1 audit. No earlier ADR, feature milestone, license, active printer pilot or git history is superseded here.  
**Inspected:** root `AGENTS.md`; `docs/{REQUIREMENTS,PRODUCT,ARCHITECTURE,EDITORIAL_SYSTEM,OPEN_DECISIONS,CHAT_RECONCILIATION,WORKING_METHOD,PROGRESS,FEATURE_CATALOG,RELEASE_PLAN,ROADMAP}.md`; `docs/adr/README.md`, ADR 0013 and ADR 0015; owner [#170](https://github.com/interzettel/kushluk/issues/170), governance [#157](https://github.com/interzettel/kushluk/issues/157) and [#176](https://github.com/interzettel/kushluk/issues/176), source-conflict [#44](https://github.com/interzettel/kushluk/issues/44), licensing [#38](https://github.com/interzettel/kushluk/issues/38), and proposal PRs [#169](https://github.com/interzettel/kushluk/pull/169)/[#177](https://github.com/interzettel/kushluk/pull/177).

**Read-limit disclaimer:** this audit is a focused comparison of **normative and governance documents**, not a new line-by-line audit of every source module, plugin, 85 GitHub issues, historical comments or private files. A missing link is not proof that a behavior is absent. Exact status of Project #3 issue fields and three-agent access remains unverified.

## A. Evidence-based conflict/ambiguity matrix

| ID | Classification | Source A vs source B | What is currently true | Action / owner |
| --- | --- | --- | --- | --- |
| **S01** | Normative contract vs reopened owner goal | ADR 0013 + `REQUIREMENTS.md` **MUST** exactly four logical A4 pages vs #170 variable-length magazines/sports extras | Four A4 pages **currently binding**; longer finite publication is owner intent, not accepted architecture | [R6 #171](https://github.com/interzettel/kushluk/issues/171), ADR/format/archive migration after founder verdict |
| **S02** | Product-direction tension, not direct contradiction | `AGENTS.md` Principle 3 says four pages **by default** vs requirements **MUST** four and ADR 0013 exact four | “By default” is not a license to publish N pages in today's implementation | Distinguish existing production invariant from proposed future in `AGENTS.md`, keep normative text intact |
| **S03** | Prompt design versus deterministic renderer | `AGENTS.md` Principle 8, ADR 0008 and accepted ADR 0015 retain deterministic geometry vs #170/#172 prompt-directed restyling | Natural-language preference may **propose** a recipe; unrestricted runtime executable templates/geometry are not approved | [R7 #172](https://github.com/interzettel/kushluk/issues/172), source/asset/format security tests |
| **S04** | Real documentation conflict | Two **accepted ADR 0012** documents: `0012-newsletter-discovery-and-source-modes.md` and `0012-newsletter-discovery-and-ingestion-modes.md` | Neither file silently wins; current index discloses conflict | [#44](https://github.com/interzettel/kushluk/issues/44) comparison and explicit accepted resolution |
| **S05** | Governance language mismatch | `docs/WORKING_METHOD.md` labels specialist coordinator/worker responsibilities vs #170/#176 **three unrestricted generalist peers** | Human-accountable integration/file ownership is useful; a peer's **thinking** is not assigned by permanent job title | Separate *task ownership* from *discussion scope* in constitution and working method |
| **S06** | Tool capability versus aspiration | #176 suggests Agent2Agent and three independent high-reasoning models vs repo's actual issue-based coordination | A2A task transport, background monitoring and Claude/local DeepSeek connectivity have **not been verified or installed** in Step 1 | Step 2–3 acceptance test with actual access disclosures and a signed round trip |
| **S07** | Planning proposal versus release authority | Draft [#169](https://github.com/interzettel/kushluk/pull/169) M2a-design slice, draft [#177](https://github.com/interzettel/kushluk/pull/177) broader H0–H6 sequencing vs `FEATURE_CATALOG.md` and `RELEASE_PLAN.md` | Current feature and release targets remain baseline pending owner approval | [#87](https://github.com/interzettel/kushluk/issues/87), [R5 #162](https://github.com/interzettel/kushluk/issues/162), [R11 #176](https://github.com/interzettel/kushluk/issues/176) reconcile in later planning PR |
| **S08** | Product-quality evidence mismatch | CI PDF geometry/min font/page count vs owner rejection of visually poor [PR #153](https://github.com/interzettel/kushluk/pull/153) | Passing machine tests does **not** equal a beautiful finished paper, independent reader acceptance or G1–G8 success | [R2 #159](https://github.com/interzettel/kushluk/issues/159), [#168](https://github.com/interzettel/kushluk/issues/168) actual-paper review rubric |
| **S09** | Licensing proposal versus existing rights | Root MIT `LICENSE` and [#38](https://github.com/interzettel/kushluk/issues/38) alternatives (MIT, MPL/Apache, AGPL etc.) | **MIT remains current**, proposed business model/original packs do not themselves change code license | #38 founder/licensing review and actual contributor/third-party rights audit |
| **S10** | Private input vs publishable content | `REQUIREMENTS.md` per-newsletter Ignore/Reference/Derivative/Personal Copy, no silent trust; #170 richer Substack/inbox assemblies | Access to user mail/newsletter **is not public redistribution permission**; ordinary source consent does not authorize private retrieval by an AI | [R8 #173](https://github.com/interzettel/kushluk/issues/173), rights/consent matrix and #44 |
| **S11** | Multiple catalogues with different responsibilities | Full issue [#43](https://github.com/interzettel/kushluk/issues/43); decision council [#157](https://github.com/interzettel/kushluk/issues/157); feature/release #87; `WORK_LEDGER.md` and `PROGRESS.md` | These overlap in references but **are not competing completion ledgers** when responsibilities are maintained | Preserve division and explicit cross-links; don't derive completion from issue count |
| **S12** | Naming/brand ambiguity | Root `AGENTS.md` explicitly declares official ASCII display **Kushluk**, while founder routinely says **Kuşluk** and the owner issue uses the Turkish spelling | Existing naming decision remains accepted until a new founder naming verdict; no styling rename in Step 1 | Optional branding issue / founder decision; keep repo/CLI `kushluk` |
| **S13** | Status semantics drift | GitHub Project Status `Backlog/Ready/In progress/In review/Done`; discussion labels `PROPOSED/REVIEWED/DECIDED`; G1–G8 evidence | They're different dimensions; Issue CLOSED or green CI **does not** imply product verification | Constitution evidence ladder and original task/gate authorities |
| **S14** | Agent-memory versus trusted record | Per-model conversation/scratchpad and proposed `docs/strategy` atlas, handover folders and Drive artifacts | Attributed assumptions and real source commit required; files/comments don't prove cross-model receipt | Step 2 shared memory plan; private inputs only in authorized private storage |
| **S15** | Design skill discovery versus installation | Stiprā `.claude/skills/*/SKILL.md` are **shims** pointing to `.agents/skills/*` canonical content | A copy of the visible shims alone is incomplete; adaptive-ui upload has not been executed or verified in Kuşluk | Step 4 provenance/license/script audit and per-runtime installations only with approval |

## B. Authorities to preserve (no rewritten history)

1. **Current runtime contract:** root AGENTS precedence, accepted ADR 0013 four pages and deterministic ADR 0008/0015; requirements and production code.
2. **Owner direction:** #170 clarifies *desired next product*, not an implicit override of existing code, source rights or architecture records.
3. **Unresolved consequential discussions:** #44 for actual accepted ADR 0012 conflict, #38 for code licensing, R1–R11 for page lengths, typography/art direction, prompt recipes, rights, agent adapters and prioritization.
4. **Product planning:** #87, current catalogue and release plan; #169/#177 are unmerged draft proposals as inspected on 19 October.
5. **Portfolio and evidence:** #43 indexes issues; stable original `WORK_LEDGER.md` task IDs and `PROGRESS.md` G1–G8 are separately verified. No checkbox changes in this PR.

## C. Proposed bounded Step 1 resolution

**Resolved as working interpretation (subject to owner PR review):**
- Three models are **generalist peers**; temporary file/PR integration ownership is not an intellectual silo.
- Independent arguments, rebuttals, founder verdicts and actual verified results are different evidence states.
- GitHub issues are the present durable **asynchronous** medium; A2A/monitoring, model-to-model live notifications and Drive sharing are *future testable integrations*.
- Every new constitutional instruction points to an existing authority rather than quietly minting a new issue/feature/milestone/gate.
- Runtime review duties are identical across peers, while actual tool capabilities and permissions must be disclosed.

**Not resolved by this PR (requires owner/ADR/process decision):** S01/S03/S04/S07/S09/S10/S12 architecture, licensing, source-rights, brand and planning changes. We explicitly preserve those conflicts.

## D. Step 1 acceptance / Step 2 handoff

- [ ] Founder reviews the source matrix and constitution; explicitly accepts, amends or rejects its collaboration procedure.
- [ ] CI validates required issue/source links and prevents accidental deletion of root precedence/accepted constraints.
- [ ] Attributable review of this PR states any disagreement with #170 or accepted ADRs.
- [ ] Follow-up Step 2 creates actual three individual handover folders, a shared assumptions/decisions/dissent index, and tested restart prompts. This PR **does not** create fake entries attributed to Claude or DeepSeek.
- [ ] Follow-up Step 3 verifies A2A task/message round trips and GitHub Pages; Step 4 audits skill installations and adaptive-ui zip before executing anything.

**Change-control rule:** Founder may choose a different approach. Record that verdict in [R11 #176](https://github.com/interzettel/kushluk/issues/176), and only then promote this proposed constitution from `PROPOSED` to `ACCEPTED` through a reviewed update. No external account action or unattended scheduling occurs in Step 1.
