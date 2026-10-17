# Measured morning production: software-readiness reports and start planning

**Issue:** [#47](https://github.com/interzettel/kushluk/issues/47) · **Work:** AUT-09 / AUT-12 software slice · **Evidence:** local machine receipts only, **not** verified unattended hardware operation.

## Three distinct results

1. **Validated and archived**: Kushluk has emitted both `validated` and `archive_ready` for an edition, in order. The timing reported for this milestone measures time since the local run receipt was created. This means a validated PDF has reached the archive path in the software pipeline, not that any person has seen a newspaper.
2. **Transport submission accepted**: CUPS or SMTP reported acceptance of the job/message. `submission_accepted` does **not** establish physical paper output, recipient delivery or a readable edition.
3. **Physically delivered / human-verified**: requires independent device evidence and a real unattended-host session. This tool always reports `physical_print_verified: false` and `recipient_delivery_verified: false`.

## Inspect one day

```bash
kushluk run --date 2026-10-17 --latest-start 07:45 --expected-start 07:30 --ready-by 08:00
kushluk run-report --date 2026-10-17
```

`--ready-by` is an **observation target**, not a promise or a kill switch. It compares the archived-PDF software readiness timestamp with the local wall-clock target of 08:00 in the configured IANA timezone. The report carries machine-allowlisted stage events, UTC timestamps, duration to archived PDF, and `ready_by_met` (true/false or null when the required validated archive evidence is missing). When `--expected-start HH:MM` is supplied (native generated scheduler templates now include it), the report separately measures **OS trigger-to-process-start delay** and **scheduled-trigger-to-PDF-archive duration**. An expected clock is an operator expectation, not proof the OS actually fired on time. It contains no headlines, feed URLs, credentials, address or external provider errors. Old receipts without timestamps are not inventively backfilled; timing values remain null.

`kushluk operate --request PRIVATE.json` also supports v1 `{"schema_version":1,"action":"report","date":"2026-10-17"}`. The command is local, read-only and does not contact a feed, printer or email service.

## Suggest a start time from measured local history

```bash
kushluk timing-plan --date 2026-10-18 \
  --ready-by 08:00 --margin-minutes 10 --history-days 30
```

This walks **at most 30 previous date-scoped local receipts**, bounded to a maximum of 90 days if requested. Only `completed` editions with ordered, timestamped `validated` and `archive_ready` milestones count. Stale, interrupted, degraded-before-validation and tampered receipts are excluded. When at least three receipts record the expected trigger clock, the method preferentially uses **trigger-to-archive elapsed time** (including observed scheduler launch delay). Otherwise it uses a separate, clearly labelled process-start-to-archive series without mixing the two samples. It applies the **nearest-rank 90th-percentile recorded elapsed time** plus a user-specified 0–120 minute safety margin to suggest a local wall-clock start time. At least three valid prior samples are necessary; otherwise the output says `insufficient_history` and never guesses.

A returned `suggested_not_installed` result can include, for example, a recommended start of 07:42 for three synthetic durations of 3, 5 and 8 minutes, with a ten-minute margin and an 08:00 target. The tool **does not edit, install or enable** any systemd/launchd timer; one can review the plan and then use `kushluk schedule-export --start HH:MM --latest-start HH:MM` manually.

```json
{"schema_version":1,"action":"timing_plan","date":"2026-10-18","ready_by":"08:00","margin_minutes":10,"history_days":30}
```

This alternative uses the stable v1 operation boundary. `margin_minutes` and `history_days` are bounded integers. The output is explicitly `local_receipts_not_independent_host_proof` and `schedule_enabled: false`. It is not a measurement of OS wake latency, login readiness, network stability or guaranteed paper delivery. Do not mistake fixture sample data for five real morning sessions.

## Readiness limitations and open acceptance

The start-to-archive duration includes source fetch and rendering in a single process, but **not** OS timer launch delay, host wake/login, a physical spooler's print completion or actual arrival of email. In addition, configuration/sources can change, so historical latency is only a planning input, not an SLA. If the estimated start would fall before the target date's midnight, the tool refuses that recommendation rather than silently scheduling on a different day.

A real G3 acceptance requires: selected always-on host, owner-installed and enabled schedule, five independently observed morning runs (including cold reboot, deliberate source outage, interruption, paused morning, deadline miss, duplicate/reprint review), and observed ready-by deadline plus actual delivery. [NATIVE_SCHEDULERS.md](NATIVE_SCHEDULERS.md) describes the manual installation and evidence rubric. AUT-09 and AUT-12 remain **open** pending complete operational delivery observability and measured real-host scheduling evidence; the G1–G8 gates remain **0/8**.
