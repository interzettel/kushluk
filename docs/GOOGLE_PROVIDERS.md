# Local Google OAuth providers and DOI evidence checks

**Issue coverage:** #48, #49, #16. **Status:** code tested with synthetic API mocks; real-user OAuth and live provider acceptance must be performed on an authorized machine. The ChatGPT Gmail connection, if any, is **not** copied or reused by Kushluk.

## Provider credentials and scopes

Google's Gmail API supports `gmail.metadata` for limited metadata reads, but this scope does **not** support Gmail's `q` message search argument. The adapter therefore scans **at most 100 messages over two recent message-list pages**, requests only `From` / `List-ID` and Google internal timestamps, and marks incomplete scans with `partial_scan=true`. It does not claim complete inbox coverage. It never requests message bodies, attachments, subjects, or mailbox modification permissions. The proposal has only sender domain, count/distinct days and hashed identity, and **every ingestion mode stays disabled**.

Google Tasks uses a separate **`tasks.readonly`** grant. It reads at most three task lists and the first 50 tasks per list, sending only incomplete due/overdue tasks into the existing practical layout. Titles are not printed by the preview command. The production edition activates this connector only with `KUSHLUK_GOOGLE_TASKS_VAULT`. The Google API's due-time is generally a date-only field; Kushluk uses its date, not a misleading promise of exact clock time.

Google API official references:
- <https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/list>
- <https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/get>
- <https://developers.google.com/workspace/tasks/reference/rest/v1/tasks/list>

### One-time local setup

Create **your own Google Cloud project and OAuth desktop client**, enable the Gmail API and Google Tasks API, configure its consent screen and users according to Google's current policies, and download the *desktop installed-app* JSON. Some Gmail scopes are restricted or need verification; Google Cloud eligibility and provider approval are not implied by this PR. Do **not** commit, attach or send the OAuth client file or resulting tokens to issues, ChatGPT, CI or the repository.

Install optional dependencies using `pip install -e '.[google]'`. Place the client JSON in an owner-private file, chmod 600, and use a dedicated local vault:

```bash
chmod 600 /private/google-desktop-client.json
kushluk google-connect --provider gmail --oauth-client /private/google-desktop-client.json --vault /private/kushluk-google
kushluk google-connect --provider tasks --oauth-client /private/google-desktop-client.json --vault /private/kushluk-google
```

Each command opens an interactive browser **separately**. No client secret, token, refresh token or account address is included in stdout, diagnostics or the published newspaper. OAuth tokens are written as owner-mode 0600 `gmail-token.json` and `tasks-token.json` inside the local vault. Secrets have no user-configurable publication path. Read-only does not make all contents non-sensitive: these scopes still require conscious consent and locally secure credentials.

### Preview, consent and revocation

```bash
kushluk gmail-discover --vault /private/kushluk-google --output /private/review.json --days 30 --acknowledge-metadata-read
kushluk newsletter-set-mode --proposal /private/review.json --id HASHED_NEWSLETTER_ID --mode reference-only --acknowledge
kushluk google-tasks-preview --vault /private/kushluk-google --date 2026-10-17
export KUSHLUK_GOOGLE_TASKS_VAULT=/private/kushluk-google
```

The first command is an explicit user-initiated **bounded header-only** read; it creates a private inactive review file, not a mailbox sync. The second records intent but does **not** activate newsletters, including reference-only. The third outputs just an eligible task count, no task titles. Only the `KUSHLUK_GOOGLE_TASKS_VAULT` environment setting enables Tasks as an actual source in the newspaper.

To remove a local grant:
```bash
kushluk google-disconnect --provider gmail --vault /private/kushluk-google
kushluk google-disconnect --provider tasks --vault /private/kushluk-google
```

These delete only the selected local token. Separately revoke Kushluk's authorization in Google's account security settings, and remove any previously generated personal editions/exported copies if needed. The tool cannot revoke already delivered printouts or remotely deactivate a Google grant.

## Narrow factual check: Crossref DOI metadata

```bash
kushluk crossref-check --doi 10.1038/s41586-020-2649-2 --title "Array programming with NumPy" --year 2020
```

A single exact DOI metadata read (no abstracts/full text) returns a structured state:
`bibliographic-match-claims-unverified`, `bibliographic-conflict`, or `abstain-*` on unavailable/missing data. A matching title/year is **not an independently verified scientific finding**; Crossref records are largely deposited by publishers. This check verifies a *bibliographic assertion*, not an arbitrary factual claim from RSS, social media or a paid article. The edition never labels general claims independently fact-checked merely because several titles agree.

The public API's limits are not guaranteed; a 429 or outage is an abstention. Live Crossref retrieval was not available in the current execution environment. The CI fixture tests check the code paths, not a production API SLA. Sources:
- <https://www.crossref.org/documentation/retrieve-metadata/rest-api/access-and-authentication/>
- <https://www.crossref.org/documentation/retrieve-metadata/rest-api/>

## Release/acceptance gates still open

**Do not check G4 based solely on this code.** An eligible operator must complete local OAuth with their own Google client, run a live bounded discovery, review false positives, revoke/refresh grants, test rate limits and outages, inspect a real Google Tasks snapshot, and validate a genuine DOI API response. Full fact-level independent corroboration, content-rights verification and paid-content copying remain separate, not implicitly delivered. No credentials or personal email data belong in CI fixtures.
