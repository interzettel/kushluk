# Three-AI founder operating system: decide first, then build the right thing

**Proposal dated 19 October 2026.** Owner direction is [#170](https://github.com/interzettel/kushluk/issues/170), strategic atlas [here](DECISION_ATLAS.md), live deliberations [#157](https://github.com/interzettel/kushluk/issues/157), [R6–R11](https://github.com/interzettel/kushluk/issues/171). This documents *how to work*, not a new hierarchy of product authority. Existing [#43](https://github.com/interzettel/kushluk/issues/43) is the issue catalogue, [#87](https://github.com/interzettel/kushluk/issues/87) owns feature/release planning, `WORK_LEDGER.md` stable tasks, and accepted ADRs govern architecture.

## Tailor PMI/lean/startup practices to a founder, not a bureaucracy

PMI's PMBOK Eighth Edition (2025) emphasizes connecting project work to value, holistic context, quality and accountability and tailoring the management approach instead of one prescribed process. PMI's *Disciplined Agile* describes a decision toolkit to choose and evolve an appropriate “way of working” for team/context. Sources:
- [PMI — PMBOK Guide, Eighth Edition](https://www.pmi.org/standards/pmbok)
- [PMI — Disciplined Agile](https://www.pmi.org/learning/agile/disciplined-agile)
- [PMI — Context Counts](https://www.pmi.org/disciplined-agile/mindset/mindset-principles/context-counts)

**Our synthesis**, not an official PMI checklist: combine outcome/quality/risk/governance discipline with startup-style test-the-most-consequential-assumption-first, cheap prototypes and short feedback cycles. Skip status bureaucracy and fictitious velocity. The founder's scarce resource is **attention and taste**, not typing code.

| Enterprise term | Solo founder translation | Visible record |
| --- | --- | --- |
| Business case / benefits | Who would actually read/keep/pay for the paper? | #170, success proofs in atlas |
| Stakeholder engagement | Reader/rights owner/printer/maintainer perspectives | #13, #4, #14 and council reviews |
| Scope baseline | Product promise + reversible staged contract | Owner manifesto, accepted ADRs, #87 |
| Integrated change control | Formal review only when a *durable* contract changes | Decision room ruling + ADR PR |
| Risk register | Top product-killing assumptions and failure impact | Decision nodes + tests and issue |
| Work breakdown | Atomic PR-sized experiments owned by existing epics | #163–#168 and later evidence work |
| Quality control | Real-paper desirability **and** software/source reliability | A06 + G1–G8, no false completion |
| Benefits realization | Finished reading and enjoyment, not GitHub stars | small consent-based field tests |
| Tailored delivery | Continuous dual track, not five-day artificial freeze | issue graph + weekly decision review |

## No assigned AI personalities or permanent roles

**ChatGPT, Claude, and user-run DeepSeek V4.1 Flash are three independent generalist reasoning peers.** Every model considers product purpose, visual culture, UX, engineering, privacy/rights, threat model, business, testability and maintenance. The only asymmetry is **tool context and provenance**: local DeepSeek can *if the user configures it* inspect code, run tests and report real machine constraints; cloud models have their own linked repo/docs/search context. No model can claim the other actually agreed without reading its separate posted reply.

The owner can ask all three the **same question**. The point is **different arguments**, not division into architect / designer / PM agents, and not a fake three-vote democracy.

### A single rigorous round (one decision node)

1. **Question framing (human or any AI):** link the exact decision node (e.g. `length`), current accepted ADR and source commit. Is this a real contradiction, speculative gap or reversible aesthetic preference? Record alternative A/B/C including “keep baseline,” affected surfaces and explicit uncertainty.
2. **Independent first pass:** each model independently sees the original source and evidence, ideally before reading peers' recommendations. Each submits a signed/attributed initial analysis **as a separate GitHub comment** with runner name, model/config as disclosed by its operator, timestamp and sources. One model drafting two comments is not two reviewers.
3. **Cross-examination:** all three may read each other's responses, respond to strongest opposing evidence and explicitly revise their positions. Capture meaningful dissent; do **not** force consensus or average positions.
4. **Founder verdict:** **ACCEPT / AMEND / EXPERIMENT / DEFER / REJECT**, short rationale and exit proof. Identify whether it changes an accepted ADR, release target, semantic/public schema, privacy/data flow or licence.
5. **Implementation proof:** reversible experiments can be split immediately into non-conflicting branches. Durable decisions require a reviewed ADR/schema/migration PR first; source-code behavior follows the accepted contract. For paper/reader impact, show artifacts before checking “done.”
6. **Update mapped authorities:** owning issue, all-issues #43, stable F-ID #87, original task IDs in `WORK_LEDGER.md`, G1–G8 independent evidence only after actually verified. Decision-atlas node status is a **snapshot**, not an automatic status change from a GitHub comment.

**No role silo:** one agent may write product objections and typography critique and challenge licensing on the same issue. The three source disclosures make differences attributable; “high reasoning” is configured by the user in each provider, not a capability this repository can switch on remotely.

## Two-way doors and one-way doors

| Kind | Examples | Decision speed and controls |
| --- | --- | --- |
| **Reversible / two-way door** | Compare paper stocks, create a designer experiment, explore art styles, test a different CSS prototype | Timebox 1–3 sessions, sandbox original/legal content; undo without data/contract migration. Founder review of actual printed/comparable output. |
| **Durable / one-way or costly door** | Change four-page canonical manifest, alter data ownership, API/recipe compatibility, source rights policy, licence, hosted data plane | Multiple evidence-based alternatives, explicit founder ruling, ADR and compatibility/migration/rights/security test before merging. |
| **Safety/consent boundary** | Read mail, connect subscriptions, send email or print automatically, publish protected content, spend money | Requires explicit scope and user consent *per action policy*; not automatically authorized by any three-AI vote. |

**Decision priority:** focus first on high-user-impact / high-uncertainty / blocking choices. A simple useful heuristic is `priority = potential reader-value loss × downstream rework exposure × uncertainty / cheapest available falsification cost`. This is a discussion tool, not a published numeric truth score; no invented estimates.

## Product development as two intersecting tracks

**Discovery/design track:** real user pain → mood/artifact benchmark → rights-safe same-content fixture → competing visual/prompt/length prototypes → actual 100% print and comprehension/keep interview → founder decision. Aim to kill weak concepts cheaply. Running an ugly sample through CI is not a product-quality pass.

**Delivery/engineering track:** narrow semantic schemas and privacy contracts → deterministic composition and printer-safe output → automatic local scheduling → failure/retry and source rights → independent novice install and 5-morning device trials. It must remain testable and proceed concurrently with design work when no shared contract is frozen.

**Integration gates:** approved design/content contract, rights checks, semantic migration, archive and print proof, real-human desirability, release claim audit. Decide whether they are release-blocking in R5/#162, not by a developer silently checking tasks.

## Minimum useful weekly founder ritual (suggested, not mandated)

- **At the start of a week — 30–45 min:** Look at the atlas highlighted contested nodes and the top 2 critical path risks. Choose one *irreversible decision* to discuss and one *reversible artifact experiment*. Say what answer would actually change direction.
- **Asynchronous throughout the week:** all three peers add source-grounded arguments/comments; DeepSeek may report laptop reproducibility. Any agent can challenge any topic. Run disjoint experiments in parallel; keep one integration PR per shared subsystem unless ownership boundaries are explicit.
- **Midweek — 15 min:** Review real PDFs/prints with source/rights proof, choose/kill a visual direction. Do not reward number of PRs.
- **End of week — 20 min:** Founder accepts/defer/rules on up to 1–3 major nodes, records what evidence changed and selects next risks. Keep backlog lean; close rejected experiments with a reason and link to accepted successor.

The five-morning host trial is a **reliability experiment**, not a ban on unrelated design/development. Keep its checkout pinned; feed results into G3 when actual evidence is independently accepted.

## Local DeepSeek: real machine feedback without unauthorized automation

**Feasibility:** local DeepSeek can provide current hardware/compiler/renderer feedback **only if you run and configure it on your laptop** with appropriate filesystem/GitHub access. ChatGPT cannot see or activate that process from GitHub comments. A proof should include actual `git rev-parse HEAD`, command, OS/Python/renderer versions, exact results, and sanitized local paths/hostnames; no tokens, private article bodies, full inbox dumps or printer-spool payloads.

Suggested user-run inspection commands (inside the repo):

```bash
git status --short
git rev-parse HEAD
gh issue view 171 -R interzettel/kushluk --json title,body,comments
gh issue view 172 -R interzettel/kushluk --json title,body,comments
```

The local model then receives the same **peer review prompt** as ChatGPT and Claude. It may post a prepared review using `gh issue comment <id> -R interzettel/kushluk --body-file <review.md>` **only when the owner has authorized that GitHub write**. No local agent should automatically merge PRs, rotate licenses, inspect private sources or submit printer jobs merely because it watches a discussion issue.

For near-real-time feedback, an optional **read-only** terminal poll of public decision issue events every ~60 seconds is possible, subject to GitHub API availability and rate limits; **there is no installed monitor or live three-way bridge in this PR**. Keep discussion comment bursts finite to avoid API limits and contributor fatigue.

## Shareable initial prompt for ANY one of the three peers

```text
You are one of three equal, independent high-reasoning product collaborators
(ChatGPT, Claude, local DeepSeek). There are no fixed AI job titles.
Read OWNER_NORTH_STAR.md, DECISION_ATLAS.md, decision-atlas.json, accepted ADRs,
#170, #157, and the specific linked issue and code/fixture.
Independently assess the decision as a reader, creative editor, software
architect, privacy/security reviewer, test engineer and responsible OSS
steward. Separate observed facts from hypotheses and aesthetic preferences.
Present at least 3 viable alternatives including preserving the baseline.
For each, analyze user value, risks, dependencies, constraints, cost,
what evidence would falsify it, and downstream ADR/F-ID/milestone changes.
Expose the strongest argument AGAINST your favored option. Do not copy
another agent's opinion or invent consensus. Do not run irreversible,
financial, privacy-sensitive, or printer actions without explicit approval.
Publish your signed/identified recommendation to the owning GitHub decision
issue (not #43) when authorized. Invite a peer to challenge it.
```

## Metadata contract for reviews and founder rulings

```yaml
decision_id: length
issue: 171
source_commit: <actual hash>
reviewer: <human or model as disclosed>
review_phase: independent | cross_exam | founder_verdict
observed_facts: [linked evidence]
options: [A, B, C]
recommendation: <option or defer>
strongest_counterargument: <reason>
falsifying_test: <reproducible experiment>
impact: {adr: [0013], features: [], task_ids: [], release: [], privacy: []}
owner_verdict: pending | accept | amend | experiment | defer | reject
proof_status: proposed | tested_in_code | observed_on_paper | independently_accepted
```

No automated workflow currently writes this YAML into GitHub fields or changes the 90-task ledger. See [DECISION_ATLAS.md](DECISION_ATLAS.md) and [#157](https://github.com/interzettel/kushluk/issues/157) for owner discussion and follow-up.
