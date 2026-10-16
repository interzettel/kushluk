# Offline OPML source onboarding (preview only)

**Feature:** F-006 · **Owner:** [#49](https://github.com/interzettel/kushluk/issues/49) · **Release target:** proposed M1 preview, [RELEASE_PLAN.md](RELEASE_PLAN.md).

You can import an existing RSS/Atom subscription list from another reader without opening any articles or connecting the internet:

```bash
kushluk sources-import-opml subscriptions.opml

# Explicitly create a 0600 private, nonactivated draft you can review:
kushluk sources-import-opml subscriptions.opml --output private-sources.json

# Only the draft can be exported back to OPML:
kushluk sources-export-opml private-sources.json --output new-subscriptions.opml
```

The CLI returns JSON with a source count, `activated: 0` and `network_requests: 0`. It intentionally does **not** call the application's existing RSS connector or mutate `KUSHLUK_RSS_URLS`. Importing a list is **not a grant to fetch/republish its content**: all imported sources remain `mode: "reference-only"`, `enabled: false`, and the draft documents `activation: "requires-explicit-user-approval"`.

For safety and reproducibility the parser accepts OPML 1.0, 1.1 or 2.0 in a **local file**, caps input at 1 MiB and 500 distinct feeds, rejects XML DTD/entity declarations and embedded URL credentials, validates HTTP(S) URLs, and removes duplicates while preserving stable appearance order. It does not resolve hosts, follow redirects, fetch feed bodies, contact providers, access a user's mailbox, or register feeds with a scheduler. Export escapes XML, never overwrites an existing file and writes restricted local permissions where the OS supports them. Private feed URLs (which may contain subscription tokens) are **not printed to stdout**; the saved file must be kept off Git.

**Known limitations (intentional):** this is **not a live feed approval UI** and does not provide an installable activated feed registry. A bounded approved-source enable/disable flow, persisted rights modes, content acquisition and per-source telemetry/privacy controls are independently owned by [#48](https://github.com/interzettel/kushluk/issues/48), [#49](https://github.com/interzettel/kushluk/issues/49), and [#4](https://github.com/interzettel/kushluk/issues/4). These limitations must be visible in the first preview release notes.
