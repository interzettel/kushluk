# Stable local operations contract — v1

**Issue:** [#47](https://github.com/interzettel/kushluk/issues/47) · **Architecture:** [ADR 0015](adr/0015-replaceable-orchestration-and-agent-runtime.md) · **Status:** software implementation; no real unattended host or printer accepted.

Use the local, provider-independent command `kushluk operate --request PRIVATE.json`. The command accepts a small JSON v1 instruction (maximum **4 KiB**, use an owner-local mode-0600 file) and emits one JSON response. Nothing connects to a hosted Kushluk service. Orchestrators (cron/systemd, launchd, Apple Shortcuts, n8n) can write the same file and call the same command without reimplementing the newspaper.

The v1 **operation boundary** supports `run`, `status`, `pause`, `resume`, and `deliver_archived`; it is not a claim that every future ADR 0015 preview/render/health operation is independently implemented as a v1 endpoint. The existing `generate`, `print-proof`, `sources-preflight` and archive commands remain available.

## Contract

Every request is a strict object with `"schema_version": 1`, an `"action"`, and an explicit ISO `"date"`. Unknown fields/versions and invalid booleans are rejected **before side effects**. Errors use stable, content-free reason codes; no arbitrary requested values are printed. Response: `{"schema_version": 1, "action": "...", "status": "...", "outcome": {...}, "physical_verified": false}`. `outcome` contains the existing versioned run receipt or archive-delivery receipt. No content, credentials, source URLs, or private home coordinates are returned.

### Nonprinting preview of whether a day has run

```json
{"schema_version":1,"action":"status","date":"2026-10-17"}
```

Run `kushluk operate --request /private/operations/status.json`. A missing receipt reports `not_run`; a paused future start with no receipt reports `paused`. Existing completed/needs-review receipts remain authoritative.

### Scheduled generation (no physical delivery)

```json
{
  "schema_version": 1,
  "action": "run",
  "date": "2026-10-17",
  "latest_start": "07:45",
  "print": false,
  "email": false
}
```

`latest_start` is an optional **last permissible start time** in the configured **IANA local timezone**, not an end-to-end delivery SLA or a scheduler. If the invocation begins after the cutoff, it returns `deadline_missed` **without generating or delivering**. The normal target remains 08:00 local; run from an OS timer sufficiently early for actual measured source/render latency. The cutoff is checked **before a new receipt**, but an already completed request returns `already_completed` even after the cutoff, and an interrupted/unknown-submission run requires review.

To authorize physical delivery, set `"print": true` or `"email": true` **and** `"acknowledge_delivery": true`. Set `"email_on_print_failure": true` only with printing enabled; it requires the same acknowledgment. All these booleans must be genuine JSON booleans. Invalid print profiles, a changed delivery request for an existing edition, and missing consent fail closed. Merely saving a configuration or running `status` never sends anything. `print_profile` is `a4-home` (default) or `a3-folded`.

The simpler `kushluk run --date 2026-10-17 --latest-start 07:45` path provides the same cutoff behavior without JSON. Existing explicit CLI `--print`/`--email` flags continue to count as operator authorization for that original CLI. For new external orchestrators, prefer v1 JSON and separate explicit consent.

### Pause one edition date

```json
{"schema_version":1,"action":"pause","date":"2026-10-17"}
```

`kushluk pause-day --date 2026-10-17` is the equivalent convenience command. Pause writes a private date-scoped marker in the local archive tree and blocks **future starts for this day**. It never cancels a pipeline that is already executing, retrieves a feed or contacts the printer. Unknown/symlinked/insecure pause markers fail closed with `needs_review`. A repeated pause returns `already_paused`.

### Resume after a pause

```json
{"schema_version":1,"action":"resume","date":"2026-10-17"}
```

Or `kushluk resume-day --date 2026-10-17`. Resume only removes a valid marker; it **does not generate or resend** an edition. If a run was already attempted before a pause, the durable receipt prevents replay. This is deliberately not a self-scheduling background service.

### Explicit reprint/re-email from an existing validated archive

```json
{
  "schema_version": 1,
  "action": "deliver_archived",
  "date": "2026-10-17",
  "channel": "print",
  "request_id": "owner-reviewed-001",
  "print_profile": "a4-home",
  "acknowledge_possible_duplicate": true
}
```

This calls the **existing** `deliver-archived` recovery implementation. The operator must first inspect the actual print queue/status. A unique request ID is required for a separate deliberate retry. Reusing it returns `already_attempted`, never a new delivery. A different ID can submit again *only after fresh operator acknowledgment*—including the risk the earlier print/SMTP request was already accepted. It never regenerates source content.

## Read-only version 1 diagnostics operations

The v1 JSON boundary also accepts `{"schema_version":1,"action":"report","date":"2026-10-17"}` and `{"schema_version":1,"action":"timing_plan","date":"2026-10-18","ready_by":"08:00","margin_minutes":10,"history_days":30}`. The first reports typed software stage/submission state, not paper/recipient verification. The second requires >=3 prior valid archived-PDF duration samples and suggests a start clock for **manual** timer reconfiguration; it never schedules. To retain a software archive target on an actual `run` request, pass `"ready_by":"08:00"`. See [TIMING_REPORTS.md](TIMING_REPORTS.md).

## Native Linux/macOS scheduler templates

Use `kushluk schedule-export` to generate a **disabled**, reviewable systemd user timer/service or launchd LaunchAgent from explicit absolute paths and an owner-configured schedule. The output is create-only and mode-0600; no service is installed or enabled. Example commands, real-host caveats and a five-morning acceptance checklist are in [NATIVE_SCHEDULERS.md](NATIVE_SCHEDULERS.md).

`scheduled.json` carries a bounded, typed `stages` array. Linux/macOS `run-status` distinguishes a running process holding the edition lock from an abandoned nonterminal receipt; a dead process always needs review and does not automatically retry. `print_submitted` is CUPS queue acceptance, **not an observation that pages were printed**.

## Local scheduler examples — not unattended proof

Example POSIX cron on an installed local host (use the *actual* path to the Kushluk environment and its configured `KUSHLUK_*` settings; do **not** blindly copy as a deployed schedule):

```cron
# Every local morning at 07:30, no print until explicitly configured:
30 7 * * * /absolute/path/to/.venv/bin/kushluk run --latest-start 07:45 >> /private/local/kushluk-scheduler.log 2>&1
```

On macOS use a **LaunchAgent** under the signed-in user's account for the same CLI command, scheduled via `StartCalendarInterval`; on Linux prefer a **systemd user timer** if the host stays awake. Neither OS will automatically wake a sleeping laptop reliably without independently configured wake/power rules. The entrypoint inherits only environment variables explicitly supplied by the scheduler; installing the package does **not** install a timer or enable printing.

For deterministic CI evidence, see `tests/test_operations.py` and `tests/test_scheduled.py`. Tests cover pause/resume, malformed markers, local-clock cutoffs, consent checks, interrupted/duplicate runs and bounded request parsing with synthetic data only.

**Not verified:** real unattended host reboot, exact publication-ready-by-08:00 deadlines, physical printer/SMTP acceptance, concurrent pause/run race at the final exclusive-create boundary, and task/agent-specific adapters. Any operator-facing alert system remains future work under #17/#20/#47. Gate G3 and all other evidence gates stay unverified.
