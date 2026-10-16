# Local scheduled runs (Stage 1)

Kushluk's Python engine owns content selection, layout and its local archive. A native OS scheduler may invoke `kushluk run`; it does **not** own editorial rules or page geometry.

## Stable command boundary

```bash
kushluk run --date 2026-09-23
kushluk run-status --date 2026-09-23
```

Omit `--date` for today's date in `KUSHLUK_TIMEZONE` (not the computer's possibly different timezone). `run` produces the canonical four-page edition; `--print`, `--email`, and `--email-on-print-failure` are explicit delivery options, and `--print-profile a3-folded` uses the existing A3 validation/preflight path. By default **no printer or SMTP job is triggered**.

The CLI emits a small JSON object with `schema_version`, `edition_id`, `status`, `print_submitted`, `email_sent`, and `failure_codes`. No source article bodies, subscribed content, ICS URLs or SMTP credentials are intentionally emitted in this status contract.

The **daily at-most-once guard** writes a durable `archive/YYYYMMDD-001/scheduled.json` receipt *before* work starts. Concurrent runs are refused. A completed edition is reused rather than regenerated or redelivered. A crash, corrupt receipt, or failed/ambiguous delivery becomes `needs_review` and blocks subsequent scheduled attempts. Printing is recorded as *submitted to the queue*, not physically printed. The guard is deliberately conservative: it may require manual intervention after an interruption even if no paper was printed.

For a manual reprint, inspect the archived PDF and the print queue before using the explicitly non-idempotent `kushluk generate --print`. Do not automatically delete receipts to make failed jobs retry. Preserving uncertain states prevents duplicate paper/mail during a race or power outage.

## Crash-safe checkpoints and recovery (software)

The edition is archived **before** CUPS or SMTP is contacted. Its four-page PDF,
HTML and original metadata survive a crash during print/email submission, so the
next action does not require editorial regeneration, more network requests, or
paid inference. The local scheduled receipt records `sources_complete`,
`editorial_complete`, `validated`, `archive_ready`, and the submission
outcome where available. The JSON output's `stage` reflects the latest
recorded checkpoint, not a physical print confirmation.

A scheduled run is still **at most once**, not automatically retry forever.
If a job was interrupted or its print/email result is uncertain, inspect
`kushluk run-status --date YYYY-MM-DD`, the CUPS queue and the existing
archive. A later `kushluk run` with different delivery options returns
`needs_review` / `request_mismatch` instead of silently claiming the newly
requested channel already ran. Rendering without a validated PDF also reports a
failed scheduled run; no job should be sent.

For a deliberate recovery *from the archived edition* without re-generating
content, choose a unique operator request ID and explicitly acknowledge the
possibility of duplicate delivery:

```bash
kushluk deliver-archived --date 2026-09-23 --channel print \
  --request-id operator-check-001 --acknowledge-possible-duplicate

kushluk deliver-archived --date 2026-09-23 --channel email \
  --request-id operator-email-001 --acknowledge-possible-duplicate
```

For an archived A3 booklet, also specify `--print-profile a3-folded`.
The command validates the **archived** publication identity and four-page PDF
(and archived A3 sheet PDF where appropriate), then exclusively reserves that
request ID *before* contacting CUPS or SMTP. Calling it again with the same
request ID never submits a second job. The resulting `manual-*.json` receipt
stores the chosen channel, content checksum and a limited status, not source
contents or private credentials. A fresh request ID is allowed only as a
**new deliberate operator action** after reviewing print/mail status; this is
not a hidden automatic retry mechanism.

For software print tests **without sending any paper**, run:

```bash
kushluk print-proof --output-dir output/print-proof
```

It builds an offline synthetic A4 four-page PDF, an A3 two-side booklet,
SHA-256 checksums, and a physical-verification checklist; see
[PRINT_PROOF.md](PRINT_PROOF.md). CI validation is not physical printer
acceptance.

## Linux systemd user-timer example (non-printing)

Place the two units under `~/.config/systemd/user/` and substitute a real
absolute path to your own Kushluk Python virtual environment and working
directory. The default example generates an archive only:

```ini
# kushluk.service
[Unit]
Description=Generate one local Kushluk morning edition

[Service]
Type=oneshot
WorkingDirectory=/ABSOLUTE/PATH/TO/kushluk
ExecStart=/ABSOLUTE/PATH/TO/kushluk/.venv/bin/kushluk run
```

```ini
# kushluk.timer
[Unit]
Description=Generate Kushluk at the configured local morning time

[Timer]
OnCalendar=*-*-* 07:30:00
Persistent=true
Unit=kushluk.service

[Install]
WantedBy=timers.target
```

Enable only after correcting paths, `systemctl --user daemon-reload`
and `systemctl --user enable --now kushluk.timer`. The host timezone and
its DST behaviour must be checked against `KUSHLUK_TIMEZONE`. A user timer
runs only if the user manager is active; lingering and wake from suspend
depend on local OS settings and must be tested. Put secrets in a protected
local environment mechanism, not in committed unit files.

## Native macOS launchd example (non-printing first)

Use an absolute path to your project, Python venv and archive; do not depend on interactive zsh `PATH` or activated virtual environments. Place this example at `~/Library/LaunchAgents/org.kushluk.daily.plist` after replacing **every** `/ABSOLUTE/PATH/TO/kushluk` placeholder.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>org.kushluk.daily</string>
  <key>ProgramArguments</key>
  <array>
    <string>/ABSOLUTE/PATH/TO/kushluk/.venv/bin/kushluk</string>
    <string>run</string>
  </array>
  <key>WorkingDirectory</key><string>/ABSOLUTE/PATH/TO/kushluk</string>
  <key>StartCalendarInterval</key>
  <dict><key>Hour</key><integer>7</integer><key>Minute</key><integer>30</integer></dict>
  <key>EnvironmentVariables</key>
  <dict>
    <key>KUSHLUK_TIMEZONE</key><string>Europe/Berlin</string>
    <key>DYLD_FALLBACK_LIBRARY_PATH</key><string>/opt/homebrew/lib</string>
  </dict>
  <key>StandardOutPath</key><string>/ABSOLUTE/PATH/TO/kushluk/output/scheduled.stdout.log</string>
  <key>StandardErrorPath</key><string>/ABSOLUTE/PATH/TO/kushluk/output/scheduled.stderr.log</string>
</dict>
</plist>
```

On Intel Macs, change the native library prefix where appropriate (often `/usr/local/lib`) and verify with `brew --prefix`. Make sure the output directory exists and log files are private. `launchd` cannot inherit your normal shell's `export` statements. Keep sensitive connector configuration/SMTP passwords **out of plists, public repositories and plain-text launch logs**; use a user-owned protected environment/secret-helper strategy before enabling such integrations.

Once the plist is valid, the user may run:

```zsh
plutil -lint ~/Library/LaunchAgents/org.kushluk.daily.plist
launchctl bootstrap "gui/$(id -u)" ~/Library/LaunchAgents/org.kushluk.daily.plist
launchctl kickstart -k "gui/$(id -u)/org.kushluk.daily"
kushluk run-status
```

This example is **not installed automatically**. It generates a local edition only; edit ProgramArguments to include `--print` **only after real printer testing**, and make sure `--email` has a privately configured SMTP transport. A sleeping Mac, user-login session, network outage, permissions and actual printer queue must still be tested in that deployment. A launchd timer is a trigger, not a guarantee of an 08:00 physical newspaper.

## Error and retry contract

| State | Meaning | Safe next action |
| --- | --- | --- |
| `not_run` | No receipt | Invoke `run` |
| `completed` | Run finished; delivery submission accounted for | Do not resubmit |
| `already_completed` | Repeated `run` found completed receipt | No operation |
| `needs_review` | Crash, incomplete state, ambiguous/failed delivery, corrupt receipt | Inspect local archive, queue and logs; human decides |

The receipt is local/private and does not guarantee OS-level printer completion. The complete run-state API, pause/intent/reprint controls, automatic preflight recovery, Apple Shortcuts trigger and real unattended morning proof remain open under [#47](https://github.com/interzettel/kushluk/issues/47) and [#13](https://github.com/interzettel/kushluk/issues/13).

See [macOS setup](MACOS.md), [print profiles](../README.md#make-an-edition), and [full automation design](FULL_AUTOMATION.md).
