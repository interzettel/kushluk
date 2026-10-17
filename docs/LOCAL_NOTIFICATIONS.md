# Opt-in local desktop alerts

**Scope:** bounded native Linux/macOS desktop *submission* of failure incidents; issue [#17](https://github.com/interzettel/kushluk/issues/17), [#20](https://github.com/interzettel/kushluk/issues/20). This is neither a push-notification service nor proof that a user saw a banner.

## Commands

```bash
# Default is a read-only preview: no desktop commands or archive writes.
kushluk notify-local --date 2026-10-17

# Explicitly request one on-device OS notification for a failed incident.
kushluk notify-local --date 2026-10-17 --send

# Opt in to a notification after the edition's scheduled-run receipt is written.
kushluk run --date 2026-10-17 --notify-local
```

Only a **failed, action-required incident** triggers submission. Routine information, paused days, completed archives and missing-receipt states remain quiet. On Linux the command attempts `notify-send` (freedesktop notification service). On macOS it attempts a fixed `osascript` Notification Center message. Unsupported platforms, unavailable executables, and headless/no-session conditions fail gracefully; **neither platform is considered physically tested by CI**.

Messages are fixed, content-free text: no article titles, source URLs, printer names, emails, home information, token fragments, arbitrary status strings or shell interpolation. Execution uses argument arrays, no shell and a five-second bound. Only a deliberate `--send` or `--notify-local` may invoke the OS notification tool. We do not install a scheduler, change delivery settings, retry print/email, send telemetry or contact an external notification service.

## At-most-once submission claim and limits

The dated local archive retains a private `.notification-<incident-id>.json` receipt, with a stable local lock. The receipt is claimed **before** attempting the desktop notification so a crash, unknown OS result or repeat invocation cannot silently re-submit the same incident. A failed or timed-out attempt is recorded as *uncertain*, rather than silently retried. Use OS desktop settings and the stored run receipt to investigate; manually resetting a failed marker requires deliberate local operator action. A different incident ID may be independently notified. On a platform with no POSIX lock, sending fails closed.

A subprocess return code of zero means only that the desktop tool accepted the request, **not** that any active desktop displayed it or a person read it. No remote diagnostics are sent. A real macOS/desktop Linux acceptance test with a logged-in session and interruption recovery is still necessary; G2/G3 remain **unverified**.

For typed safe status, see [agent incident report](AGENT_INCIDENT_PROTOCOL.md). For broader failure behavior, see [Failure Matrix](FAILURE_MATRIX.md).
