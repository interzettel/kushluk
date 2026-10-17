# Editorial inputs and trust boundaries — #49 / #48 / #16

**Implementation stage:** local-first adapters and reference metadata only. Proprietary/publisher copy and any subscription-based derivative or private direct inclusion remain disabled. No consumer subscription is treated as API access or a redistribution license.

## Local tasks — optional, replaceable source

Export a UTF-8 local `KUSHLUK_TASKS_FILE=/private/tasks.json` containing strictly:

```json
{
  "schema_version": 1,
  "tasks": [
    {"id": "stable-local-id-1", "title": "Submit design review", "due_date": "2026-10-17", "status": "open"},
    {"id": "stable-local-id-2", "title": "Archive completed draft", "due_date": "2026-10-17", "status": "done"}
  ]
}
```

Kushluk reads at most 64 KiB and 150 source tasks from a regular non-symlink file; it lists up to six incomplete tasks due today or earlier and omits completed/future work. It never uploads the task export, stores its credentials or creates tasks. Any service that can make this export can become a replaceable source without modifying Kushluk. This is a **working local task adapter**, not a connected Microsoft To Do, Google Tasks, Todoist or remote OAuth integration. Live provider APIs and renewals need their own explicit entitlement approval.

## Public research metadata — Crossref, opt-in

Set `KUSHLUK_RESEARCH_QUERY="spatial planning"` explicitly to search **only public scholarly metadata** by title through the documented Crossref REST API. The connector requests at most five DOI/title/date records and uses an HTTPS-only, hostname-pinned response-bounded transport. It never requests licensed abstracts, article bodies or paywalled PDFs. It stores a DOI public pointer, retrieval timestamp, original DOI ID and source name; the newspaper labels these as unverified source pointers rather than verified research conclusions.

Crossref documents public access and policies at <https://www.crossref.org/documentation/retrieve-metadata/rest-api/access-and-authentication/>. Its current access rules include rate limits and 429 handling: this edition performs just **one** bounded list request when enabled, with safe degradation if unavailable. There is **no** unauthenticated general web crawler, pooled news corpus or claim synthesis. A future documented provider can implement the same `Candidate` contract; this adapter alone does not establish scientific truth or relevance of a claim.

## Traceable provenance and conservative verification

Each selected `Story` may now contain bounded `StoryProvenance` entries: candidate/origin ID, originating source, source kind, cleaned public URL, publish/retrieval times, `source-pointer` transformation and `reference-only` rights. Sources are clustered with explicit evidence entries; even matching titles do **not** elevate a story into a fact-checked claim. States:

- `unverified-source-pointer`: one candidate; merely an index to original reporting
- `multi-source-unverified`: matching titles or URLs across multiple candidates; repetition is not independent corroboration
- `potential-title-conflict`: differing headlines sharing a canonical URL or near-duplicate cluster; human verification needed

No automatic claim assertion, invented summary or model-generated citation is authorized by these states. Every external title, email subject, snippet and candidate is **untrusted data**. It may be safely rendered as escaped article text, but never evaluated as a CLI instruction, API key, tool call, email destination or permission change. Historical edition and print manifest remain local; do not log private URLs, source bodies or credentials. Test fixtures inject hostile web and mail instructions and assert inert handling.

## Authorized Google provider adapters (optional)

Local **separate** OAuth flows can now connect Gmail `gmail.metadata` for *header-only* newsletter review and Google Tasks `tasks.readonly` for due/overdue items. `gmail-discover` requires `--acknowledge-metadata-read`; it stores no message bodies and never enables newsletter ingestion. `KUSHLUK_GOOGLE_TASKS_VAULT` opts Google Tasks into a real edition. Tokens remain on the owner's machine and can be independently removed. There are no app-owned/pooled credentials. The code has mocked provider tests but no real account OAuth acceptance, so #48's connected-mail acceptance remains open. Follow the exact, scoped instructions and revocation procedure in [GOOGLE_PROVIDERS.md](GOOGLE_PROVIDERS.md).

Exact DOI bibliographic title/year claims may be checked via `crossref-check`, which returns explicit match/conflict/abstain. A positive match still labels scientific conclusions and general news claims **unverified**: publisher-deposited metadata is not independent validation of a research result.

## Newsletter discovery — bounded, local, inert

The local export flow remains an offline alternative to the **new, separately consented Gmail metadata-only OAuth adapter**. The owner may locally export at most 250 **header-only** metadata records from the last 1–60 days (30 default) into a UTF-8 JSON file:

```json
{
  "schema_version": 1,
  "headers": [
    {"sender": "Newsletter <letters@example.org>", "date": "2026-10-16T12:00:00+00:00", "list_id": "<daily.example.org>", "subject": "Issue 2"},
    {"sender": "Newsletter <letters@example.org>", "date": "2026-10-15T12:00:00+00:00", "list_id": "<daily.example.org>", "subject": "Issue 1"}
  ]
}
```

```bash
kushluk newsletter-discover --snapshot /private/headers.json --days 30 --output /private/review.json
kushluk newsletter-set-mode --proposal /private/review.json --id HASHED_ID --mode reference-only --acknowledge
```

The discovery output (private mode 0600) contains only a hashed identity, sender **domain**, frequency/distinct-day counts, rights status and an inactive mode. No full email addresses, newsletter contents, subject lines, original message IDs, provider tokens, or unsubscribe links are stored in the resulting proposal. Two messages on different days with the same sender and `List-ID` are required; repeated transactional notices without `List-ID` are excluded. The user must review the inactive proposal; it cannot activate itself.

All four intent choices `ignore`, `reference-only`, `derivative`, and `private-direct` are persistable only with explicit `--acknowledge`. **No choice activates ingestion** in this tranche. An actual mailbox adapter still requires narrowly scoped provider authentication, pagination, consent/revocation and source-specific copy/derivative permission evidence. No messages are sent to external AI or any model in the discovery flow. Duplicate-ADR-0012 policy decisions stay with #44.

## Security and cost honesty

Untrusted webpage/email/recipe material must never cross the line into executable settings or actions. Tasks and newsletter headers are parsed through bounded typed schemas; malicious metadata, invalid local symlinks, oversized exports, query secrets and raw private content are rejected or degraded through fixed error codes. Crossref public metadata is accessed only via an explicitly configured query and a fixed provider hostname. A source record is not an instruction.

No paid AI/model APIs, mail connections or subscription services are added. **Do not display 'zero cost' as a measured value**: print paper/ink, host electricity and optional external services still carry unknown or estimated costs. Complete #16 cost accounting, budgets and independent fact-checking remain open.

## Acceptance outstanding

The new Gmail and Google Tasks OAuth code has not been exercised with a **real authorized user account** in CI, since the owner must supply and approve a local desktop client. The Crossref single-DOI endpoint is implemented and fixture-tested; a direct live check in this execution environment was blocked by DNS/network access. Treat that as missing acceptance evidence, not as a success.

- #49: real authorized task-provider session, public research source quality and recency review, alternative Reddit/HN adapters, source disagreement/claim-level independent checks and travel signals
- #48: scoped connected-mail provider integration, real inbox discovery consent and false-positive review, practical source permissions for derivatives and direct copy
- #16: per-edition metered spend, end-to-end adversarial recipe tests, source-derived conflicting claims with independent evidence and full trust/cost manifest
- G1–G8 independent delivery evidence remain 0/8; no physical printer/email acceptance

All tests in `tests/test_editorial_inputs.py` are hermetic and perform no real mailbox reads, send/print side effects or live provider requests.
