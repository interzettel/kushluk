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

**Known limitations (intentional):** OPML import/export alone does **not** activate feeds; the separate approval registry below now provides explicit per-source enable/revoke. It is not a complete nontechnical setup UI. A bounded approved-source enable/disable flow, persisted rights modes, content acquisition and per-source telemetry/privacy controls are independently owned by [#48](https://github.com/interzettel/kushluk/issues/48), [#49](https://github.com/interzettel/kushluk/issues/49), and [#4](https://github.com/interzettel/kushluk/issues/4). These limitations must be visible in the first preview release notes.

## Explicit, durable feed approvals — F-007 first slice

Imported OPML proposals **remain disabled** until you approve an individual feed by its **1-based index**. The CLI does not expose subscription URL tokens in output.

```bash
# Review your original OPML and its order locally, then grant read access to one feed:
kushluk sources-approve private-sources.json --index 1 --acknowledge-feed-access
# -> {"status":"approved","id":"...","approved_count":1,
#     "mode":"reference-only","article_copying_permitted":false}

kushluk sources-list
kushluk sources-revoke --id <the-source-id>
```

Approved feeds are stored in a **private 0600** JSON registry (default `~/.config/kushluk/approved-sources.json`, or `$XDG_CONFIG_HOME/kushluk/approved-sources.json`). Set `KUSHLUK_SOURCE_REGISTRY=/path/to/local/private.json` to select another location. Approve/revoke uses an exclusive lock and atomic file replacement; a stale `.lock` after a crash fails closed for a human to inspect. No background process is started and approval does **not** immediately fetch an article. The **next explicitly run** edition can read approved RSS endpoints.

If an approved registry exists and `KUSHLUK_RSS_URLS` is not set, only its approved feeds are used—no default sample Hacker News feed sneaks in. Any manually configured `KUSHLUK_RSS_URLS` remains an independent legacy explicit source list, combined with approved entries; clear it to enforce the registry alone. A newly created **empty** registry means no RSS feeds.

**Permissions:** `--acknowledge-feed-access` is a personal statement that the reader is entitled to retrieve the selected RSS feed. It is **not a copyright or republication grant**, and the only active mode today is `reference-only` (headlines and feed-provided snippets with attribution). Derivative summaries and private direct inclusion still require their own rights checks and source-mode UI under #4/#48. Approved endpoints can access the network **only during a run**; do not approve feeds pointing at sensitive local/admin addresses or URLs containing secrets. The CLI does not check all DNS targets or prevent redirects; additional source-network hardening is still tracked under #49 and must precede an exposed/multiuser service.

This workflow is intentionally a developer-friendly first source-approval path, not a full nontechnical setup wizard, mailbox/newsletter discovery, or evidence that all source rights are resolved.

## Four reader-intent modes (staged rights enforcement)

```bash
kushluk sources-set-mode --id SOURCE_ID --mode ignore
kushluk sources-set-mode --id SOURCE_ID --mode reference-only
kushluk sources-set-mode --id SOURCE_ID --mode derivative --acknowledge-rights-boundary
kushluk sources-set-mode --id SOURCE_ID --mode private-direct --acknowledge-rights-boundary
kushluk sources-list
```

The registry preserves the selected mode and durable source ID, but **only `reference-only` is currently active and fetched**. Choosing `ignore` pauses that source. Choosing `derivative` or `private-direct` records an intention and **automatically disables the feed** until future authorisation and generation/copy paths are implemented: a reader's click is not a legal determination. Each active reference-only feed *discards* incoming RSS item descriptions and HTML bodies **before editorial selection** and emits only the headline and a neutral source pointer. Already archived editions remain immutable after revocation; removal affects subsequent runs only.

Do not confuse saved `derivative` or `private-direct` preferences with actual support for those workflows. Neither is currently allowed to fetch article bodies, save them in an edition, or be distributed. This is not a legal rights-verification service. Additionally, explicitly configured legacy `KUSHLUK_RSS_URLS` feeds are **outside the registry policy**; they may still ingest feed-provided summaries and should not be used with private/restricted feeds until isolated by the same policy. The source-mode control is a protective increment, not the complete permissions acceptance gate.
