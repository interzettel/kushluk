---
name: kushluk-issue-intake
description: Create traceable Kushluk issues and keep Project #3 metadata in sync.
---

# Issue intake (agents)

1. Search existing issues and [master ledger #43](https://github.com/interzettel/kushluk/issues/43); **reuse** a matching issue rather than duplicating it.
2. For a new issue, write a concise problem, outcome and verifiable acceptance criteria in a Markdown body file. Run:
   `python -m tools.create_issue --title "[Task] Short outcome" --body-file /path/to/body.md --kind task --priority P2 --workstream A`
3. This creates the real issue with assignee, kind/priority/workstream labels, optional parent/dependencies/milestone, attaches it to [Project #3](https://github.com/orgs/interzettel/projects/3), and sets **actual native fields** through `project_sync.py`. Requires authorized `gh` / `GH_TOKEN`; fail clearly if unavailable. Never fake a Project write.
4. When development starts, use an issue-linked branch and PR (`Refs #N` or `Closes #N`), add CI/evidence, then update the issue and #43 once. Never self-award Verified, close duplicates as delivered, or invent milestones.
5. For bot/connector-created issues, use the same metadata and let the [native Project workflow](../../.github/workflows/native-project-metadata.yml) fill real fields; check the Actions run.

See [AGENTS.md](../../AGENTS.md) for the full authority and safety policy.
