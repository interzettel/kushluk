# Native unattended scheduling — reviewable Linux and macOS recipes

**Owner:** [#47](https://github.com/interzettel/kushluk/issues/47) · **Status:** reproducible templates and synthetic tests, **not a deployed service or accepted host**. No scheduler, print job, SMTP delivery or third-party orchestrator is enabled by Kushluk's template export.

## 1. Prerequisites (local owner action)

Install Kushluk into a local Python environment (including the optional PDF dependencies and their native requirements on macOS), choose a writable **persistent working directory** and run an interactive `kushluk doctor`. Configure your private profile and source permissions separately. Preserve the `archive` and `output` directories across restarts. Ensure the host's **system clock, OS timezone and Kushluk IANA timezone** match for morning scheduling: systemd/launchd trigger at the OS clock, while `--latest-start` is checked against Kushluk's configured timezone.

Test manually with `kushluk run --latest-start 07:45` **without `--print` or `--email`**. Note that even digital-only runs may fetch deliberately approved remote news/weather sources. The separate [offline CI smoke](../tools/offline_smoke.py) never does.

The full edition readiness goal remains **08:00 local time**. A default 07:30 trigger and 07:45 cutoff are adjustable **examples, not measured production latency**. A cutoff rejects only a new start after its clock time; there is no kill-switch when rendering crosses 08:00.

## 2. Generate, inspect and install native units yourself

Create *disabled* files (absolute paths are intentional, and user-supplied output files are never overwritten):

```bash
kushluk schedule-export --platform systemd \
  --executable /home/reader/kushluk/.venv/bin/kushluk \
  --working-dir /home/reader/kushluk \
  --output-dir /home/reader/kushluk/scheduler-review \
  --start 07:30 --latest-start 07:45
```

This creates `kushluk.service` and `kushluk.timer`. Both are mode 0600 and **do not** install into systemd. For Linux user units, review them, then *only after deciding to activate a schedule*:

```bash
mkdir -p ~/.config/systemd/user
cp /home/reader/kushluk/scheduler-review/kushluk.{service,timer} ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now kushluk.timer
systemctl --user list-timers kushluk.timer
```

Use `systemctl --user status kushluk.service` and `kushluk run-status` to inspect a run. To stop it, `systemctl --user disable --now kushluk.timer`. `Persistent=true` catches up after a missed timer on supported hosts, **but the local latest-start cutoff blocks late publication**. A normal user session does not necessarily start before login; unattended boot operation may require an owner-configured always-on host and user lingering. **Do not enable lingering without reviewing host security.** No root/system service is generated.

For macOS, generate a LaunchAgent:

```bash
kushluk schedule-export --platform launchd \
  --executable /Users/reader/kushluk/.venv/bin/kushluk \
  --working-dir /Users/reader/kushluk \
  --output-dir /Users/reader/kushluk/scheduler-review \
  --start 07:30 --latest-start 07:45
```

The output is a plist named `org.interzettel.kushluk.morning.plist`. After reviewing the command, permissions and working directory, the **local user** can copy the file to `~/Library/LaunchAgents/` and explicitly run:

```bash
mkdir -p ~/Library/LaunchAgents
cp /Users/reader/kushluk/scheduler-review/org.interzettel.kushluk.morning.plist ~/Library/LaunchAgents/
launchctl bootstrap "gui/$(id -u)" ~/Library/LaunchAgents/org.interzettel.kushluk.morning.plist
launchctl print "gui/$(id -u)/org.interzettel.kushluk.morning"
```

To disable: `launchctl bootout "gui/$(id -u)/org.interzettel.kushluk.morning"`. This is a **logged-in-user LaunchAgent**, **not a headless LaunchDaemon**; do not assume it survives logout, a sleeping Mac or a reboot without user login. If the PDF renderer requires an inherited environment/loaded Pango libraries, resolve those in the host session before enabling. No shell, secret, provider URL or printer flag is inserted into the generated plist.

## Timing and evidence reports (read-only)

After a locally initiated run, inspect `kushluk run-report --date YYYY-MM-DD`. To measure the software deadline, use `kushluk run --ready-by 08:00`. Once **three or more** valid completed local edition receipts exist, `kushluk timing-plan --date YYYY-MM-DD --ready-by 08:00 --margin-minutes 10` suggests a start clock from a conservative p90 software archive latency. This is only a suggestion for manual review; **it does not modify the exported unit files**. An OS's trigger/wake/login delay and actual CUPS/SMTP delivery are **not** included. Full semantics: [TIMING_REPORTS.md](TIMING_REPORTS.md).

## 3. Run-state semantics after restart

- `kushluk run-status --date YYYY-MM-DD` uses the same persisted `scheduled.json` receipt as `operate` `status`.
- The bounded `stages` list is built from actual pipeline events: `started`, `sources_complete`, `editorial_complete`, `rendering`, `rendered`, `validated`, `archive_ready`, optional `print_submission_unknown`, `print_submitted`/`print_failed`, `email_submission_unknown`, `email_sent`/`email_failed`, `complete` or `interrupted`. Not every stage is present on a degraded run.
- On Linux/macOS, a private per-edition advisory file lock distinguishes an **actively held** run (`in_progress`) from a nonterminal receipt left by a dead process (`needs_review`). A dead/ambiguous print/SMTP attempt is **never automatically retried**. On Windows and nonlocal/network filesystems, active-run detection is not verified and nonterminal states fail closed.
- `print_submitted` means accepted by the CUPS submission API, **not paper exited successfully**. `email_sent` means SMTP accepted submission, **not recipient delivery/read**. The `complete` stage means Kushluk returned from pipeline, not an independently verified morning paper.
- `pause-day` only blocks **future starts**; it cannot cancel an already active run. Explicit `deliver-archived` with a new authorized request ID remains the only supported reprint path after review of the real printer queue.

## 4. Human acceptance checklist (G3 remains unverified)

On a **real selected host**, conduct at least five scheduled morning runs, including one cold reboot, one deliberate interrupted source/provider outage, an unexpected process termination, one blocked late start, and one paused morning. Compare scheduler trigger timestamps, local timezone, archive receipts, validated PDFs, printable artifacts and actual delivery/queue state. Measure readiness relative to 08:00 and record whether manual intervention was necessary. Validate log ownership and file permissions after restart, and test crash/recovery without duplicate print/email. A live print acceptance requires a real printer and independent verification, not just a CUPS job ID. Do not upload personal calendar/feeds, credentials, address or unredacted local logs into public issues.

**Remaining risks:** OS wake/session/lingering configuration, clock drift, network filesystem locking, pause/start atomicity across processes, uncertain device/SMTP delivery, real 08:00 readiness and notification/alert mechanisms. Existing systemd and launchd templates deliberately require manual owner review/installation; an exported file is not a working deployment.
