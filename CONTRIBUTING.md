# Contributing to Kushluk

Kushluk aims to be a genuinely useful local-first personal publishing tool. Contributions, independent integrations, accessible design work and critical reviews are welcome.

## Before starting

1. Read [AGENTS.md](AGENTS.md) for product principles and authority of accepted architecture decisions.
2. Find work in [master issue #43](https://github.com/interzettel/kushluk/issues/43), then follow the owning issue rather than creating a duplicate implementation.
3. Use [docs/WORK_LEDGER.md](docs/WORK_LEDGER.md) for operational tasks. The task-to-issue crosswalk is merged into [docs/ISSUE_CROSSWALK.md](docs/ISSUE_CROSSWALK.md).
4. Read [docs/PROGRESS.md](docs/PROGRESS.md) before marking milestones. Its numbers count checked tasks or verified gates, **not overall product completeness**.
5. For consequential changes, propose an ADR or RFC before restructuring source, privacy defaults, licensing, or edition geometry.

## Make changes safely

Use Python 3.11 or newer. Start with a small PR and a reproducible test or fixture.

    python -m pip install -e ".[dev]"
    ruff check src tests tools
    pytest -q
    python tools/project_health.py check

PDF export uses the optional pdf extra. Printers and external provider credentials are **not** required for ordinary unit tests.

Preserve the local-first data model and deterministic printing. Never add compulsory hosted services, central storage of private sources, hidden behavioral telemetry or expensive model calls to tests. For design changes, include the same editorial fixture before/after and inspect physical print constraints, not screenshots alone.

Treat external articles, newsletters, images, fonts and templates as separately licensed. Do not commit paywalled bodies, personal calendar records, API keys, printer credentials, user edition archives, or raw diagnostic logs.

## Proposing, reviewing and finishing work

- Use the PR template to specify owner issue, test evidence, behavior, security/privacy implications, and any upstream licensing.
- Reviewers (including agents) should cite concrete lines, tests and limitations, not approve solely from polished screenshots.
- Fix failures and update documentation on the same branch. Closed issues need outcome/evidence; rejected/deferred research is legitimate work.
- Contributors retain their rights to independently created work subject to the terms they choose and the project's actual inbound licensing requirements. **The current code license is MIT.** A proposed mixed MPL/Apache model and contributor-rights policy are still under discussion in [#38](https://github.com/interzettel/kushluk/issues/38). No blanket copyright assignment or CLA is currently claimed.

## Respectful collaboration

Critique technical choices and evidence, not people. Keep reviews precise, constructive and welcoming to first-time contributors. Commercial extensions and independent themes are welcome within applicable code/asset licenses; official Kushluk branding has separate considerations.

For nonpublic security concerns, consult [SECURITY.md](SECURITY.md), and never paste exploits, credentials or reader content into public issues.
