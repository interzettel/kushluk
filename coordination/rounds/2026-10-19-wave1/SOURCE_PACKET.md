# Kushluk first peer round — shared factual source packet

**Round identifier:** `2026-10-19-W1` · **Prepared by:** ChatGPT GPT-6 · **Source snapshot:** repository `main` at `fe25c90fa14e6875845074247a8a2b75e19e249c` · **State:** EVIDENCE PACKET PREPARED, no independent Claude or DeepSeek review implied.  
**Scope:** the three consequential discussion rooms [#171](https://github.com/interzettel/kushluk/issues/171), [#172](https://github.com/interzettel/kushluk/issues/172), [#173](https://github.com/interzettel/kushluk/issues/173). **Canonical decisions:** only in those GitHub threads through founder verdicts and accepted ADRs, never in this snapshot.

## Why this packet exists

All three peers need **identical primary facts**, but not each other's preferred answers, before drafting their first round. It deliberately lists source evidence and competing questions without a suggested winning option. Each peer is free to challenge factual framing, product scope, legal premise, aesthetic expectations, implementation sequencing and test design. This packet does **not** authorize network fetching, GitHub posting, private-source ingestion, paid inference, printer jobs or local A2A calls.

The actual participating model/runner must separately disclose its current access and independently recheck the accepted ADRs/code against the real `main` HEAD. The frozen SHA is a **review anchor**, not a claim that later commits are invalid. If code differs, report the delta and its effect.

## Common owner and governance sources

- [Owner vision #170](https://github.com/interzettel/kushluk/issues/170): beautiful finite reader-owned editions; personal information modules; optional longer paper/sports inserts; agent-neutral creative control; no infinite feed. Owner **intent**, not a retroactive ADR revision.
- [Constitution](../../../docs/coordination/CONSTITUTION.md) accepted via [PR #178](https://github.com/interzettel/kushluk/pull/178): all three models are generalist reasoning peers, with independent positions, evidence-backed dissent and human founder verdict.
- [Handover/restart workspace](../../README.md) merged via [PR #179](https://github.com/interzettel/kushluk/pull/179): **Claude and DeepSeek handovers are still UNINITIALIZED at source-packet time**; authentic participation must update their own records.
- [Requirements](../../../docs/REQUIREMENTS.md): the current canonical edition **MUST** be four logical A4 pages, keeps explicit source/rights modes and requires deterministic rendering after manifest finalization.
- [ADR index](../../../docs/adr/README.md): exact normative ADR identity and precedence; **two accepted ADR 0012 records conflict** and remain owned by [#44](https://github.com/interzettel/kushluk/issues/44). Do not choose between them for convenience.
- [ADR 0013](../../../docs/adr/0013-four-logical-a4-pages-multiple-print-profiles.md): four logical A4 pages; A4 home and A3 folded output are printer impositions, not different editorial systems. ADR explicitly documents conditions for revisiting the decision.
- [ADR 0015](../../../docs/adr/0015-replaceable-orchestration-and-agent-runtime.md): provider-independent edition engine owns editorial/geometry; orchestrators/AI agents are replaceable clients; interfaces may expose CLI, HTTP or MCP.
- [Release planning #87](https://github.com/interzettel/kushluk/issues/87), [feature catalogue](../../../docs/FEATURE_CATALOG.md), [original task ledger](../../../docs/WORK_LEDGER.md), [independent evidence tracker](../../../docs/PROGRESS.md): do not count discussion, generated PDFs or code CI as real user hardware acceptance.

## R6 · [#171](https://github.com/interzettel/kushluk/issues/171) · edition length and sports inserts

**Question:** is four A4 pages the permanent universal physical publication, a default profile with independently linked supplements, or one possible bounded N-page edition?

**Observed source facts:**

1. [`models.py`](../../../src/kushluk/models.py) defines `Publication(schema_version=2)`, a `pages: list[EditionPage]` field and `EditionPage.kind` restricted to `front/day/stories/sources`. It stores canonical content references, not independent paper signatures.
2. [`publication.py`](../../../src/kushluk/publication.py) explicitly describes four fixed A4 kinds, with archetypes changing allocation but not sheet count.
3. [`validation.py`](../../../src/kushluk/validation.py) checks schema v2, **exactly 4** ordered pages, PDF geometry and embedded logical markers `1/4` … `4/4`.
4. [`print_profiles.py`](../../../src/kushluk/print_profiles.py) implements A3 folded outside `4|1` / inside `2|3`; longer signatures aren't currently validated there. Actual physical printer orientation still needs real paper proof.
5. [ADR 0013](../../../docs/adr/0013-four-logical-a4-pages-multiple-print-profiles.md) itself asks to revisit if another format proves materially better or if four pages are too long/short.

**Alternatives for each peer to evaluate afresh:** core four + tagged supplements; one bounded variable-length N-page edition; preserve current four-page model with separate digital extras; or a reasoned alternative. Do not rely on ChatGPT's previously posted recommendation.

**Required falsifiers:** archive v2 compatibility/migration, A4 duplex and A3 collation including blank padding, at-most-once print receipt, time/ink budget, source identities, actual paper hierarchy and the reader's sense of one cohesive object. Use original/rights-cleared fixtures and make no product code change without accepted architecture decision.

## R7 · [#172](https://github.com/interzettel/kushluk/issues/172) · prompt-to-beautiful style without unsafe geometry

**Question:** how should a user's or external agent's art-direction prompt be translated into visually different and reliable print output?

**Observed source facts:**

1. [`models.py`](../../../src/kushluk/models.py) has three `LayoutArchetype` allocation choices, four `BlockKind` categories, `SlotBudget` capacities and bounded `CompositionDecision` actions. These are **not** a full reader-authored graphic design system.
2. [`models.py`](../../../src/kushluk/models.py) media/story classes include source and credit fields. [`media.py`](../../../src/kushluk/media.py) handles owner-imported assets with explicit print permission, a **66×33mm media slot**, crop and minimum effective-DPI constraints. This does not yet establish arbitrary page-size image art direction or editable vector workflows.
3. [`validation.py`](../../../src/kushluk/validation.py) checks four-page PDF structure and page markers. Those tests cannot certify beauty, source truth, comprehension or desirability.
4. [ADR 0015](../../../docs/adr/0015-replaceable-orchestration-and-agent-runtime.md) requires Kuşluk—not a free-form agent—to control final asset placement. [#31](https://github.com/interzettel/kushluk/issues/31) separately asks to avoid unsafe runtime LLM geometry.
5. The founder explicitly rejected a technically passing design in [PR #153](https://github.com/interzettel/kushluk/pull/153) as visually inadequate.

**Alternatives:** intent → typed declarative recipe + deterministic layout; reviewed/sandboxed template extension; curated style gallery and safe parameters; a hybrid justified by actual artistic evidence.

**Required falsifiers:** same lawful frozen editorial fixture, at least three genuinely distinct design proofs, licensed type and images, vector-first SVG charts and diagrams if feasible, EN/DE/TR line-breaking, grayscale fallback, reproducible layout plan, injection/unsupported extension failures and **real printed** human aesthetic selection. There is no blanket authorization to install external drawing skills or generate copyright-uncertain news illustrations.

## R8 · [#173](https://github.com/interzettel/kushluk/issues/173) · authorized newsletter and inbox assembly

**Question:** what may be read, transformed, printed privately or shared when the user has subscriptions, private emails, notes and public sources?

**Observed source facts:**

1. [`models.py`](../../../src/kushluk/models.py) `StoryProvenance` includes source/URL/times/transform and rights modes, plus explicit verification state.
2. [`editor.py`](../../../src/kushluk/editor.py) builds source provenance with `transform_mode="source-pointer"` and `rights_mode="reference-only"`; even multiple title clusters are explicitly *unverified*, not treated as independently fact-checked.
3. [`REQUIREMENTS.md`](../../../docs/REQUIREMENTS.md) states newsletter discovery is user-confirmed before a persistent editorial source; a subscription does not guarantee a print slot; four source modes require careful distinction.
4. [`media.py`](../../../src/kushluk/media.py) explicitly limits media to local owner-imported assets with recorded permission; it does not auto-download hotlinked images.
5. [#44](https://github.com/interzettel/kushluk/issues/44) identifies the unresolved duplicate **accepted ADR 0012**. A private mailbox read grant is different from redistribution and third-party media copyright rights.

**Alternatives:** local metadata-first source selection; user-export/import workflow; bounded provider-native authenticated access; or staged hybrid. No real private emails or provider credentials are included in this packet.

**Required falsifiers:** synthetic newsletter dataset spanning owned/licensed/reference-only/denied/revoked assets, matrix of output destinations (private home paper, local archive, shared recipe, public web), explicit opt-in/revocation behavior, verifiable source URLs/credits, no data exfiltration through prompts/recipes/logs, no fabricated stories after feed failure, and a compelling *readable* artifact rather than a link-only source list. Actual terms/copyright questions require source-specific evidence and appropriate qualified review.

## How each peer should respond

- Independently inspect original source and real checked-out commit. **Do not** start by reading ChatGPT's preferred option if a genuine unprimed first-pass review is still possible.
- All peers consider **reader delight, publication craft, security/privacy/source rights, schema/agent compatibility, economic cost, accessibility, testing and release impacts**; no permanent professional roles.
- For each room: at least three alternatives, strongest case against the preferred direction, cheapest falsifier, what remains unverified and **exact** relevant ADR/feature/task/gate/milestone impact.
- Post one truthful, attributable review **only with public GitHub write authorization**. The authored comment may appear under the account owner's GitHub username; it MUST identify the actual AI runner/phase in the body. If posting failed or isn't allowed, save a draft and mark `NOT POSTED`.
- Label a ChatGPT resumed session reviewing old ChatGPT comments as **CONTINUATION**, never a second independent peer. The founder's own verdict controls accepted decisions.
- Don't alter the separate Agent Council/A2A implementation. The screenshot contains only self/owner-reported quota and status, targeted notifications, leases and no attached A2A task DB; verify live functionality separately.

**Round state at creation:** shared evidence packet prepared, ChatGPT continuation reviewed all three issues and linked comments, **no authenticated Claude Code or local DeepSeek review verified**; no founder decision on R6–R8 recorded. The owner may run separate peer sessions now without waiting for an automatic A2A bridge.
