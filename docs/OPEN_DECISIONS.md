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

## Open proposals tracked on GitHub (not accepted architecture decisions)\n\nThese issues currently require evidence, maintainer review and/or founder decisions. Their existence **does not override accepted ADRs** or authorize new hosting, advertising, publisher content sharing, or license changes:\n\n- [#38](https://github.com/interzettel/kushluk/issues/38) — licensing: MIT (currently shipped) vs MPL core / Apache interoperability boundaries and contributor IP/DCO/governance; hold changes pending ownership and dependency audit.\n- [#37](https://github.com/interzettel/kushluk/issues/37) — local vault format and whether/when optional E2EE sync/browser access should be offered.\n- [#35](https://github.com/interzettel/kushluk/issues/35), [#36](https://github.com/interzettel/kushluk/issues/36), [#39](https://github.com/interzettel/kushluk/issues/39) — Studio economics, optional creative merchandise and reader-invited sponsorships; experimental, not current business commitments.\n- [#40](https://github.com/interzettel/kushluk/issues/40), [#41](https://github.com/interzettel/kushluk/issues/41) — personal magazines vs public editorial products and separate printing/storage service feasibility; copyright/privacy review required before any commercial rights claim.\n- [#26](https://github.com/interzettel/kushluk/issues/26), [#30](https://github.com/interzettel/kushluk/issues/30), [#31](https://github.com/interzettel/kushluk/issues/31), [#52](https://github.com/interzettel/kushluk/issues/52) — optional implementation research, **not** reasons to block the deterministic native renderer.\n- [#44](https://github.com/interzettel/kushluk/issues/44) — resolve the two accepted ADR 0012 files' identifier/wording conflict and maintain accepted ADR 0015 index.\n\nTrack portfolio state in [master ledger #43](https://github.com/interzettel/kushluk/issues/43) and implementable tasks in [ISSUE_CROSSWALK.md](ISSUE_CROSSWALK.md) / [WORK_LEDGER.md](WORK_LEDGER.md).\n\n## Resolved since the previous register

The canonical physical-format decision is no longer open. ADR 0013 supersedes ADR 0002: Kuşluk uses four logical A4 pages with A4 Home Printer and A3 Folded Newspaper print profiles.
