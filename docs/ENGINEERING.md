# Engineering and progress workflow

**Status:** engineering foundation proposal, October 2026. [Issue #54](https://github.com/interzettel/kushluk/issues/54) coordinates the work. This document does not supersede accepted ADRs.

## One source of truth for each concern

| Question | Authoritative record |
| --- | --- |
| Why Kushluk exists, non-negotiable behavior | AGENTS.md, PRODUCT/REQUIREMENTS, accepted ADRs |
| What code actually does | tests, source, CI evidence and STATUS.md |
| Which operational tasks still need work | WORK_LEDGER.md (task IDs, not GitHub issue count) |
| Which GitHub discussions/issues exist | [Master ledger #43](https://github.com/interzettel/kushluk/issues/43), with dated manual snapshots |
| Where operational IDs belong | [Draft crosswalk PR #53](https://github.com/interzettel/kushluk/pull/53) until merged |
| What counts as demonstrated delivery | [PROGRESS.md](PROGRESS.md) plus [progress-manifest.json](progress-manifest.json) evidence links |
| What was considered/rejected | Individual RFCs, ADRs and issue closure notes |

There are **two deliberately different progress measures**:

1. **Task-checklist state:** how many of the 90 currently inventoried WORK_LEDGER task IDs have checked boxes. Already-shipped Stage 1 legacy functionality is not necessarily captured in these newer checkboxes.
2. **Evidence gates G1–G8:** a gate becomes verified only after an actual proof/test and review. A pending gate is not 0% finished; it is **unverified**.

Never blend task count, issue closure rate and product readiness into one invented project-completion percentage. The GitHub issue ledger is a **manual snapshot**; the offline progress script does not contact GitHub or auto-close issues.

## Refreshing progress

    python tools/project_health.py json
    python tools/project_health.py render
    python tools/project_health.py write
    python tools/project_health.py check

The script uses only Python's standard library, needs no GitHub token and never sends private files over the network. Its manifest lists all expected numbered task IDs by group (so missing, duplicate or unexpectedly new IDs fail until mapped) and the eight verification gates. The generated Markdown in PROGRESS.md is committed and CI checks that it is current. To add a new task group or number, update the manifest and related issue crosswalk in the same PR.

A gate's **verified** state requires an ISO date and at least one HTTPS link to a reproducible commit/PR/test output or documented physical trial. Evidence should be reviewed; the script checks its presence and shape, not the truth of the external link. A manual reviewer remains responsible for judging quality.

## Minimum contributor path

1. Confirm owning GitHub issue and work-ledger IDs. Do not open a duplicate issue merely to create a progress number.
2. Make a narrow code/test/doc change in a branch; include fixtures and negative/security tests where relevant.
3. Run Ruff, pytest and the project health check. Hardware, actual printer output and paid provider access are separate manual gates—never fabricate them.
4. PR template summarizes evidence, changes to network/privacy flows, source rights and compatibility.
5. Human/agent reviewer independently inspects the result; the maintainer merges only after required checks and accepted ADR constraints.
6. Update issue state and task/gate evidence **after** the relevant tests/PRs are actually confirmed.

## CI tiers and known limitations

- Existing CI: Ruff, pytest, an executable CLI walking-skeleton smoke test; Python 3.12.
- New Project health CI: no network/paid APIs, validates 90-item task inventory, G1–G8 evidence metadata and committed progress snapshot on Python 3.11/3.12.
- **Known debt:** the older smoke job uses default network-backed weather and RSS. It is not fully hermetic. Track fixture substitution and isolated optional live integration tests in #54 rather than claiming that CI now guarantees network independence.
- **Not yet gated:** real printer access, PDF physical samples, migrations/backups, supply-chain/release attestation, trained LLM behavior. #13, #45–#51 and #54 own those future checks.

## Branches, discussions and licensing

PR #53 is a separate *docs-only* reconciliation PR. This engineering-foundation PR should remain reviewable independently and must not silently change the current MIT license or both accepted ADR 0012 variants. Contributor copyright/inbound rules remain an open governance decision under #38; no CLAs or DCO sign-offs are imposed by this workflow change.

Use [SECURITY.md](../SECURITY.md) for sensitive reporting guidance. Avoid publishing raw data and credentials even in an error screenshot.
