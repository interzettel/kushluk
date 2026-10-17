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

**Permissions:** `--acknowledge-feed-access` is a personal statement that the reader is entitled to retrieve the selected RSS feed. It is **not a copyright or republication grant**, and the only active mode today is `reference-only` (headlines and feed-provided snippets with attribution). Derivative summaries and private direct inclusion still require their own rights checks and source-mode UI under #4/#48. Approved endpoints can access the network **only during a run**; do not approve feeds pointing at sensitive local/admin addresses or URLs containing secrets. As of the guarded RSS transport, each feed DNS lookup must resolve only to global/public IP addresses and its connection is pinned to an approved numeric IP; private redirects, HTTPS downgrades, nonstandard ports, credentials and oversized responses are blocked. Proxy environment variables are not honored. This is defense-in-depth for RSS, not a comprehensive sandbox for every other connector or a guarantee against DNS attacks outside the fetch path; #49 remains open.

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

Do not confuse saved `derivative` or `private-direct` preferences with actual support for those workflows. Neither is currently allowed to fetch article bodies, save them in an edition, or be distributed. This is not a legal rights-verification service. All RSS inputs—including explicitly configured legacy `KUSHLUK_RSS_URLS` and the historical default sample feed—now use the **same reference-only and guarded network policy**. Existing custom RSS article-body/description copies into editions are intentionally no longer supported. Feed endpoint URLs with subscription tokens are not archived as story provenance; only validated article links and headline references are retained. The source-mode control is a protective increment, not the complete permissions acceptance gate.


### Safe article links

RSS story links from providers are never used to fetch full article bodies. Before placing links in a PDF/HTML/EPUB edition, the system accepts only public HTTP(S) article references that lack embedded credentials and known authentication/session query parameters; nonpublic or unsafe links are omitted. Legacy archived EPUBs are checked again during export. Removing a suspicious link does not invent a replacement or remove the truthful headline/source name.

### Per-source degradation

A blocked, offline or malformed feed reports `rss_feed_unavailable` with only its 1-based position and a safe category. The connector preserves candidates from the other healthy RSS feeds and never logs feed URL tokens. If no source provides a valid article headline, the existing `no_editorial_stories` degradation remains visible. No article is invented to cover missing data.

## Reader-approved feed preflight (F-007 / F-008 slice)

Inspect which local RSS sources are enabled **without contacting any website** by default:

```bash
kushluk sources-preflight
# Optional private create-only diagnostics (no URL or feed articles in output)
kushluk sources-preflight --output ~/kushluk-private/audit-001.json

# Explicit network check, bounded to five active approved feeds by default:
kushluk sources-preflight --network --limit 5
```

An opt-in network preflight uses the same guarded public-only RSS transport as publication. It only fetches the approved reference-only feed metadata required to tell whether headlines are available; it **does not approve new sources, create a four-page edition, write to the archive, contact disabled sources, or store article bodies**. Each result refers to a stable hashed source ID and one of `reachable`, `empty`, `unsafe_or_unavailable`, `invalid_feed_xml`, `not_checked`, or `disabled`, never its private subscription URL, raw HTTP errors or headline text.

The CLI exits 2 when any **checked** source fails, useful for optional manual troubleshooting. It does not call the network unless you pass `--network`; you can check at most ten approved feeds in one invocation to avoid surprise provider traffic. A good result verifies **reachability**, not source licensing, content accuracy, PDF print quality, or unattended scheduling. No remote telemetry is sent by the diagnostic beyond each explicitly requested feed access.

### New readers: sources are opt-in

Once you create a **local home profile** with `kushluk setup` or `kushluk setup-web`, Kuşluk will no longer insert the historical Hacker News example RSS feed as an implicit source. Your source list starts **empty** until you explicitly approve one, and pausing the last feed leaves it empty. Importing an OPML file *for review* alone never activates a feed.

Compatibility: older installations that have **neither a local profile nor a source registry** retain the legacy example feed, so this increment does not silently break existing scripted demonstrations. An explicit `KUSHLUK_RSS_URLS` setting remains authoritative and follows the same reference-only content restrictions. Anyone configuring that setting is independently directing the program to retrieve those feed URLs.

This is a source-selection safety default, not a confirmation of publisher reuse rights or remote service hardening beyond the RSS transport.
