# Open Decisions

Only decisions that materially change product direction belong here.
Implementation should continue around them when possible.

## 1. Final production typefaces

Playfair Display + Inter remain safe prototype choices for layout development.

The final production typefaces should be chosen after:
- four-page template prototypes exist;
- A4 stapled and A3 folded physical tests have been printed;
- inexpensive home-printer reproduction has been checked;
- licensing/embedding requirements have been reviewed.

This does not block the four-page renderer or automation work.

## Open proposals tracked on GitHub (not accepted architecture decisions)

These issues currently require evidence, maintainer review and/or founder decisions. Their existence **does not override accepted ADRs** or authorize new hosting, advertising, publisher content sharing, or license changes:

- [#38](https://github.com/interzettel/kushluk/issues/38) — licensing: MIT (currently shipped) vs MPL core / Apache interoperability boundaries and contributor IP/DCO/governance; hold changes pending ownership and dependency audit.
- [#37](https://github.com/interzettel/kushluk/issues/37) — local vault format and whether/when optional E2EE sync/browser access should be offered.
- [#35](https://github.com/interzettel/kushluk/issues/35), [#36](https://github.com/interzettel/kushluk/issues/36), [#39](https://github.com/interzettel/kushluk/issues/39) — Studio economics, optional creative merchandise and reader-invited sponsorships; experimental, not current business commitments.
- [#40](https://github.com/interzettel/kushluk/issues/40), [#41](https://github.com/interzettel/kushluk/issues/41) — personal magazines vs public editorial products and separate printing/storage service feasibility; copyright/privacy review required before any commercial rights claim.
- [#26](https://github.com/interzettel/kushluk/issues/26), [#30](https://github.com/interzettel/kushluk/issues/30), [#31](https://github.com/interzettel/kushluk/issues/31), [#52](https://github.com/interzettel/kushluk/issues/52) — optional implementation research, **not** reasons to block the deterministic native renderer.
- [#44](https://github.com/interzettel/kushluk/issues/44) — resolve the two accepted ADR 0012 files' identifier/wording conflict and maintain accepted ADR 0015 index.

Track portfolio state in [master ledger #43](https://github.com/interzettel/kushluk/issues/43) and implementable tasks in [ISSUE_CROSSWALK.md](ISSUE_CROSSWALK.md) / [WORK_LEDGER.md](WORK_LEDGER.md).

## Reopened owner-level strategic questions (19 October 2026)

The founder's [affirmed product direction #170](https://github.com/interzettel/kushluk/issues/170) calls for beautiful user-selected physical publishing, personal/private/authorized mailbox content, possible finite supplements and longer magazines, and provider-independent prompt-guided creative production. **This direction is not a silent amendment of accepted ADRs or an implemented feature.** The [reconciliation audit](coordination/RECONCILIATION_AUDIT_2026-10-19.md) preserves the exact current contract and records which issues own the changes.

- [#171](https://github.com/interzettel/kushluk/issues/171) — **ADR 0013** four-page canonical format versus bounded variable-length editions and sports supplements. **OPEN; accepted four-page contract remains.**
- [#172](https://github.com/interzettel/kushluk/issues/172) — prompt-to-style creative control versus **ADR 0008/0015** deterministic, provider-neutral production. **OPEN; safe executable recipe format unapproved.**
- [#173](https://github.com/interzettel/kushluk/issues/173) — authorized mailbox, Substack and timeline content assembly versus per-source privacy/rights requirements and the **ADR 0012 duplicate**. **OPEN; source rights not assumed.**
- [#174](https://github.com/interzettel/kushluk/issues/174) — agent-neutral CLI/HTTP/MCP and optional A2A orchestration. **OPEN; no three-provider transport certified.**
- [#175](https://github.com/interzettel/kushluk/issues/175) with [#38](https://github.com/interzettel/kushluk/issues/38) — original paper/art business versus current MIT core, source/brand rights. **OPEN; no relicensing.**
- [#176](https://github.com/interzettel/kushluk/issues/176) — one founder and three **generalist reasoning peers**, handovers, governance and independent review process. **OPEN; proposed collaboration constitution under review.**
- [#162](https://github.com/interzettel/kushluk/issues/162) and [#87](https://github.com/interzettel/kushluk/issues/87) — rebaseline milestone order against the owner's quality and reader-value criteria. **OPEN; planning PRs #169/#177 remain proposals.**

Do not confuse **discussion OPEN/CLOSED** with Project implementation stage or the separately checked `WORK_LEDGER.md` tasks and `PROGRESS.md` evidence gates.

## Resolved since the previous register

The canonical physical-format decision is no longer open. ADR 0013 supersedes ADR 0002: Kushluk uses four logical A4 pages with A4 Home Printer and A3 Folded Newspaper print profiles.
