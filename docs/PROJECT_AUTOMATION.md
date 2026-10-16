# Operating native GitHub Project metadata

**Project:** [Kushluk #3](https://github.com/orgs/interzettel/projects/3) · **Implementation:** [#65](https://github.com/interzettel/kushluk/issues/65).

**Agent workflow:** [tools/issue-intake/SKILL.md](../tools/issue-intake/SKILL.md) and `python -m tools.create_issue`. The owner's Actions secret is now authorized for organization Project #3. The first successful run created **Workstream, Maturity, and Evidence**. GitHub's existing reserved **Priority** field had no options and rejected API mutation ([attempt](https://github.com/interzettel/kushluk/actions/runs/38967689905)). This integration therefore provisions a distinct editable **Triage Priority** field; it does **not** delete, modify, or claim to populate the reserved Priority field. Run bootstrap/backfill/audit and verify issue values before declaring completion.

## What the fields do

| Native Project field | Values | Practical purpose |
| --- | --- | --- |
| **Status** (already exists) | Backlog, Ready, In progress, In review, Done | Who should work next; do **not** create duplicate Stage |
| **Triage Priority** (custom) | P0, P1, P2, P3 | Maintainer order of work; separate from GitHub's reserved, unconfigurable Priority |
| **Workstream** | A–H, Untriaged | Group backlog into the eight master-ledger areas |
| **Maturity** | Idea, Research, Accepted, Implemented, Verified | Separate unapproved thoughts from accepted or coded work |
| **Evidence** | Missing, Partial, Verified | Identify what is still unproven, independent of GitHub issue closure |

**Labels** (`kind:*`, `priority:*`, `workstream:*`) support repository issue search and filtering. **Native issue type** (Bug/Feature/Task) is set where the organization enables it. **Assignee** is the real maintainer, `@yigit-denktas`. Project fields are actual GitHub native values, **not text in the issue body**.

Defaults for newly opened issues: **Backlog, Triage Priority P2, Untriaged, Idea, Missing**, adjusted to Research for RFCs. If a maintainer has already assigned a field, the bot preserves it. A new issue's body can suggest Priority/Workstream only when its author is the designated steward. **No issue author can claim Verified automatically.**

## One-time setup by the Project owner

1. Create a **fine-grained personal access token**, scoped to the `interzettel` organization and `interzettel/kushluk` repository, with **Organization Projects: read/write** and **Repository Issues: read/write** (and normal Metadata read). Choose an expiry and rotate it. A GitHub App with equivalent permissions can replace the token in future.
2. In this repository, open **Settings → Secrets and variables → Actions → New repository secret**. Name it exactly **`KUSHLUK_PROJECT_TOKEN`**; paste the token **there only**, not in an issue, PR, screenshot or chat. If organization policy blocks a personal token, use an approved GitHub App identity instead.
3. Go to **[Actions → Native Project metadata](https://github.com/interzettel/kushluk/actions/workflows/native-project-metadata.yml) → Run workflow** and choose **`bootstrap`**. That creates missing native fields and supporting label vocabulary only once. It reuses the already existing `Status`.
4. Run **`audit`** to inspect coverage. For an immediate, rate-budget-safe manual backfill use **`backfill`** with batch size **5** (never more than 20). The same workflow now resumes **up to five incomplete issues every two hours**, but skips writes while GraphQL quota is low. Re-run **`audit`** to check the remaining count and verify issue values on the [Project](https://github.com/orgs/interzettel/projects/3). This is an intentionally paced reconciliation, not a single unbounded bulk import.
5. From then on, an issue opened/reopened/edited/labeled/closed triggers the sync workflow. Errors are visible in Actions; it is **not operational until the secret and bootstrap actually succeed**.

GitHub-hosted Actions runners already include `gh`, so you do not need to install GitHub CLI on your Windows PC for this workflow. Local developers with `gh` authenticated can also run:

```bash
python tools/project_sync.py bootstrap
python tools/project_sync.py audit
python tools/project_sync.py sync --issue 65
python tools/project_sync.py backfill
```

Use `GH_TOKEN` via your secret environment and do **not** copy it into an ordinary shell transcript.

## How issues and development remain traceable

An issue created by a contributor will be assigned to the steward, placed into Project #3, and initialized with safe metadata. The correct milestone is an **existing verified outcome milestone**, otherwise `TBD` in the issue until roadmap milestones are created. Do not fabricate milestone numbers. Native parent/subissue/blocked-by relations are added when concrete dependencies are reviewed; fallback links remain in the issue body. A research-only issue need not have a code branch. Any implemented task needs an issue-linked branch and PR, `Refs #N` or `Closes #N`, CI and accepted evidence before closure.

**Safety:** the workflow never issues an automatic PR merge, gives an L5 autonomy grade, edits the MIT license, triggers paid services, or treats issue Done as an evidence-verified feature. Status on the Project and product delivery G1–G8 are separate dimensions.

## Local verification

```bash
python -m unittest discover -s tests -p test_project_sync.py -v
ruff check tools/project_sync.py tests/test_project_sync.py
```

These tests simulate GitHub CLI responses. **Passing them does not prove the Project token is configured or that field writes occurred on GitHub.** For actual operational verification use the bootstrap/sync Action run links and Project field values, and record outcomes in issue #65 and master ledger #43.

## Rate-limit recovery (16 October 2026)

The authorized token created the custom **Triage Priority** single-select field. The original unbounded bulk write partially populated existing issues but then failed with GitHub's GraphQL API rate-limit error ([run](https://github.com/interzettel/kushluk/actions/runs/38968661458)). Replaying the old full backfill would immediately spend more API calls and risk duplicate work. The implementation now caches Project field metadata per batch, checks existing values, limits each batch to at most 20 issues, and runs **five issues** per scheduled attempt only when the token has a safe GraphQL budget. **Do not interpret a scheduled workflow succeeding because it skipped a low-quota run as proof that field coverage is complete**; use the `audit` missing-values report and inspect actual Project records.
