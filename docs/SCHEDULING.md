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
