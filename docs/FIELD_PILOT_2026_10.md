# October 2026 local field pilot — operator evidence register

**Evidence date:** 2026-10-19. **Owners:** [#13](https://github.com/interzettel/kushluk/issues/13) (physical pilot and reader ritual), [#47](https://github.com/interzettel/kushluk/issues/47) (scheduler and recovery). **Task source:** [WORK_LEDGER.md](WORK_LEDGER.md); [host trial rubric](HOST_TRIAL_REVIEW.md). This is a dated record of **operator-provided output and observations**. It is not an independent host audit, print certification, or release-gate approval.

## Observed

| Date | Experiment | Operator-supplied result | Evidence boundary |
| --- | --- | --- | --- |
| 2026-10-18 | Four-page offline A4 synthetic print proof, HP DeskJet 2800 series via Windows | Four individual, single-sided sheets produced. Operator reports no text extending beyond the pale/beige background region. | Actual paper was produced, but no quantitative margins, ink/stock measurements, duplex, CUPS or unattended print acceptance. [#13](https://github.com/interzettel/kushluk/issues/13) |
| 2026-10-18 | Manually invoked `kushluk run` under Ubuntu 24.04 on Windows WSL2 | Edition `20261018-001` completed, validated and archived. Elapsed to archive 6.47 s, no failure codes; print/email not requested. | Manual digital-only software receipt. [#13](https://github.com/interzettel/kushluk/issues/13) |
| 2026-10-19 | One-time Windows Task Scheduler → WSL2 → local `kushluk run`, expected 07:30, latest start 07:45, software-ready target 08:00 | Windows `LastRunTime=07:30:00`, `LastTaskResult=0`, missed runs 0. Edition `20261019-001` completed; `archive_ready=2026-10-19T05:30:08.238684Z` (07:30:08 CEST), `elapsed_to_archive_seconds=7.19`, `trigger_delay_seconds=1.05`, `trigger_to_archive_seconds=8.24`, `ready_by_met=true`, no failure codes. | **One** successful operator-reported unattended **digital-only** host launch. No printer/email delivery requested or verified. [#47](https://github.com/interzettel/kushluk/issues/47) |

## Scheduled, not yet observed

On 2026-10-19, the operator registered and inspected **five separate one-time Windows Task Scheduler tasks** for 2026-10-20 through 2026-10-24 at **07:30 local time**. Each invokes the Ubuntu 24.04 WSL2 checkout's `kushluk run` for that date with `--expected-start 07:30 --latest-start 07:45 --ready-by 08:00`; **neither `--print` nor `--email` is set**. The operator supplied the five task names, next-run timestamps and initial `267011` (task not yet run) codes. All **0/5** of these future runs remain unobserved as of this evidence date. The previously completed 2026-10-19 run is separate from this planned five-day window.

The jobs use Windows interactive logon and do not independently ensure host wake-up, cold-boot readiness, unlocked credential access, native CUPS printing or automatic fallback. Review system task results **alongside** each local `kushluk run-report`; a created task is not evidence of completed execution.

## Next observations, no automatic acceptance

1. Inspect each 20–24 October task's actual `LastRunTime`, exit code, missed-run count, edition ID, ordered stages, validated archive, timing against the target and any human intervention.
2. Perform a controlled cold-restart/wake and delayed-start test *separately*; document laptop power/sign-in prerequisites and fail-closed behavior. Include a safe outage, pause and interrupted-run/idempotency review before claiming reliability.
3. Test a printer transport deliberately after validating Windows-to-printer and WSL2/CUPS boundaries, without automatic reruns or unattended ink consumption until explicitly enabled.
4. Conduct first-reader/usability and meaningful editorial-density/layout review separately. The synthetic four-page fixture was **not** accepted as a finished newspaper design.

**Acceptance accounting:** no existing WORK_LEDGER task checkbox is changed by this log; AUT-09/AUT-12, TRIAL-01..07 and #13/#47's full acceptance remain open where already open. G1–G8 independently verified gates remain **0/8**. No private photos, configuration files, raw archives, credentials, task-host identity or local logs are committed.
