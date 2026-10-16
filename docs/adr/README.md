# Architecture Decision Records

ADRs preserve decisions that future maintainers or agents must not silently reinterpret.

Status values:
- Proposed
- Accepted
- Superseded
- Rejected

Each ADR contains:
- Context
- Decision
- Rationale
- Consequences
- Alternatives
- Revisit conditions

## Current accepted set

- 0001 Local-first personal data plane
- 0004 Calendar/tasks outrank live travel detail
- 0005 Reliability before cleverness
- 0006 Lead story is optional
- 0007 Serendipity is protected
- 0008 Rendering is deterministic
- 0009 User model is provider-independent
- 0010 Edition archive is first-class
- 0011 Reuse upstream infrastructure while preserving the product layer
- 0012 Newsletter discovery is explicit and source-specific
- 0013 Four logical A4 pages with multiple print profiles
- 0014 Morning intent is ephemeral editorial input\n- 0015 Orchestration and agent runtime are replaceable

## ADR identifier conflict requiring maintainer resolution\n\n**Two files currently carry accepted ADR number 0012:** `0012-newsletter-discovery-and-source-modes.md` and `0012-newsletter-discovery-and-ingestion-modes.md`. Both have overlapping but not identical source-mode wording. This is a documentation integrity issue tracked in [GitHub #44](https://github.com/interzettel/kushluk/issues/44). Neither file is silently treated as superseded solely by this README update. Resolve via an explicit recorded decision, preserve history and then update this index and all references.\n\n## Superseded

- 0002 One DIN A4 sheet by default — superseded by 0013.
- 0003 Front is Today, back is For You — physical grammar superseded by 0013; the Today-first/For-You-later editorial principle remains in current docs.
