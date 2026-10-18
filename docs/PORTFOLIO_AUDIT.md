# Portfolio consistency audit — live, read only

Tracking: [master ledger #43](https://github.com/interzettel/kushluk/issues/43),
[#54](https://github.com/interzettel/kushluk/issues/54) engineering health,
[#59](https://github.com/interzettel/kushluk/issues/59) journal,
[#65](https://github.com/interzettel/kushluk/issues/65) Project backfill and
[#87](https://github.com/interzettel/kushluk/issues/87) release plan.

[Run the portfolio audit manually](https://github.com/interzettel/kushluk/actions/workflows/portfolio-consistency.yml).
It also executes at 07:17 UTC each day. It uses the existing
KUSHLUK_PROJECT_TOKEN secret for **read operations only**. The separate
Project synchronization workflow may use broader rights; this audit does not.

The job reports directly in the GitHub Actions summary and stores a small
JSON artifact for 14 days. No issue is automatically posted, labeled, closed,
assigned, reclassified or moved. No Project value, milestone, task check,
release, manifest evidence or acceptance gate is ever changed by this tool.

Checks:
- Live open/closed repository issues (PRs excluded) against the 64-row
  indexed snapshot in #43, including missing, duplicate and stale-state rows.
- Native Project #3 membership, missing Status/Triage Priority/Workstream/
  Maturity/Evidence fields, and existing sync-tool pending conditions.
- Exact 90 TASK IDs against ISSUE_CROSSWALK primary owner references,
  plus all declared G1–G8 owner issue IDs. Project health still controls the
  authoritative ledger task states; a PR or closed issue awards no progress.
- GitHub published releases against the release plan, journal, status and
  current Python version. A development version ahead of the last tagged
  version is a review finding, not necessarily an error.

**Exit codes:** 0 on a complete audit even when drift exists; 1 with
--strict for a complete audit with drift; 2 for missing auth, truncated
inventory, failed API access, or malformed sources. Incomplete is NOT clean.

For local/offline tests use --fixture path/to/synthetic-snapshot.json.
The script's emitted report contains only public issue IDs, counts and
source/release tags; it does not dump issue bodies, private Project values,
tokens, release artifact bytes or participant observations.

Review findings manually under their existing owner issues. Continue
Project metadata backfill separately under #65. This is intentionally an
**audit, not another tracker or a self-approving release gate**.
