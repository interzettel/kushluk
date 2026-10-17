# Local incident reports for reader-owned agents

**Owner:** issue [#20](https://github.com/interzettel/kushluk/issues/20). **Status:** an inspectable local protocol, **not** a background notifier, remote reporting endpoint or autonomous repair engine.

## Read a report on your own computer

```bash
kushluk incident-report --date 2026-10-17
kushluk incident-report --date 2026-10-17 --output ~/private-kushluk-reviews/incident.json
```

Both forms read only the existing bounded `run-report`/scheduled-run receipts. The optional output writes a **new**, owner-only JSON file (mode 0600 on POSIX), never overwrites an earlier receipt, and does not put private article text, URLs, home details, tokens or raw provider errors into the result. It does not inspect arbitrary logs.

An existing agent can make an explicit **read-only** invocation using the local `kushluk operate --request /private/request.json` interface:

```json
{"schema_version":1,"action":"incident_report","date":"2026-10-17"}
```

The operation schema rejects additional destination/recipient keys; this action **cannot** print, email, re-run an edition or make remote diagnostics requests. There is no automatic agent invocation or outgoing telemetry.

The [local morning status page](MORNING_STATUS_WEB.md) presents the same bounded, read-only incident facts to ordinary readers through `setup-web` (GET `/status`); it does not perform agent actions or send any information to a remote server.

## Machine-readable contract, v1

`kind=local_run_incident`, `schema_version=1` and `report_template_version=1` identify the format. Fields include:

- A **local**, deterministically derived short `incident_id` and date-only `edition_id`, not a user or cloud identifier.
- `status`, `component`, `severity` (`info`, `degraded`, `failed`), a fixed `error_code` and **allowlisted** `failure_codes`; unrecognized codes become `unclassified_failure`.
- Separate printer and email **submission** states, with `paper_verified=false` and `recipient_verified=false`. Queue acceptance is not physical delivery.
- `edition_usable=validated_archive_reported` only if validated+archive-ready software receipt evidence exists; it is not an end-user reading/quality verification.
- `suggested_actions` with a fixed ID, permission level, `automatic_retry_allowed=false`, and whether a person must decide. These are **advice**, not callable commands.
- A fixed, plain-language `human_notice`; `user_notification_required` flags serious incidents but does **not** send a notification.
- `report_prepared=true`, `remote_report_authorized=false`, `remote_report_sent=false`, `sources_contacted=false`, `delivery_attempted_by_report=false`.

A typical interrupted printer submission is classified as `failed` with action `inspect_local_receipt_and_external_queues` and `human_review_required`. An existing successful archive with unverified paper is `info`, not a green physical acceptance signal. Missing run receipts are `degraded` because a missing log is not proof of a failed print attempt. Any unknown status falls back to `status_requires_review`.

The v1 report intentionally does **not** include environment/platform identifiers, source titles, paid articles, local paths, mailbox IDs, article counts, raw failure messages or personal calendar entries. No automated retry budget is enabled, because an uncertain printer or SMTP submission must not be replayed silently. Agent prompts are untrusted input and cannot change this execution boundary.

## Separate permissions and unfinished work

Owner review may use the private JSON file to troubleshoot locally. **Sharing with a maintainer, external agent, support channel or diagnostic receiver needs separate preview and explicit consent**, governed by #18. A static `safe_diagnostic_fields` list does not make a disclosure automatically lawful or approved.

Still open under #20: independently tested accessible notice language, actual opt-in native local notifications, broader deterministic remedial actions with authority/budgets, external diagnostics consent workflow, and physical queue/hardware observations. A passing test is not evidence of a real host or physical printer.
