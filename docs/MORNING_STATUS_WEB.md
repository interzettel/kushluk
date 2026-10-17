# Morning status in the local setup browser

Kuşluk's manual `kushluk setup-web` session now offers **http://127.0.0.1:PORT/status** next to setup, source review, and printer setup.

This is a **read-only**, accessible single-page status panel with deterministic labels. It reports whether today's validated local edition archive was prepared, whether a print/email **submission** was accepted/failed/uncertain, and what safe action an operator should consider. It does not expose home coordinates, private article titles, source URLs, account information, tokens, filenames, raw provider errors or arbitrary receipt strings.

No external frontend frameworks, cookies, JavaScript, polling, analytics, telemetry or remote connection. The browser server requires numeric IPv4 loopback, exact Host header, restrictive Content Security Policy, and no caching; `/status` accepts GET only. Loading or refreshing it never creates a dated archive, starts a scheduler, retries a job, sends an email, prints paper, or submits a notification. When an archive does not exist, the page says **Not started** rather than fabricating an event.

**Important:** the status panel is software evidence, not independent evidence that a physical printer produced a readable page or that an email arrived. The panel is bounded to **today's** edition in the configured local timezone and does not provide raw history or permission to activate delivery. Use `kushluk run-report --date YYYY-MM-DD` or `kushluk incident-report --date YYYY-MM-DD` for other dates. User testing, assistive-technology acceptance, unattended-host observations and actual printer proof remain open.

See [first-run onboarding](FIRST_READER_PILOT.md), [agent incident protocol](AGENT_INCIDENT_PROTOCOL.md) and [failure matrix](FAILURE_MATRIX.md).
