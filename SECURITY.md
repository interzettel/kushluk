# Kushluk security reporting and boundaries

**Status:** early-stage, locally run prototype; no published security-response SLA. See [engineering foundation #54](https://github.com/interzettel/kushluk/issues/54) and [provenance/security #16](https://github.com/interzettel/kushluk/issues/16).

## Sensitive findings

Do **not** post proof-of-concept exploits with user secrets, access tokens, subscribed articles, private calendar URLs, real mailbox content or personal newspaper editions in public issues.

If GitHub offers **Security → Advisories → Report a vulnerability** on this repository, use that private route. If private reporting is not enabled, open a **minimal public issue requesting a private contact method** without including technical exploit details or user data. This document does not imply a monitored security email address or private reporting feature already exists.

## Areas that deserve special care

- External article/newsletter text is **untrusted input**, not authorization for agent commands or local file operations.
- ICS URLs and mailbox/API/SMTP credentials may contain secrets; errors, logs and generated reports must not preserve raw tokens.
- Local archives, preference models and subscription-derived editions are private by default.
- Optional remote AI, storage, printing and voice providers must be authorized individually; no new default outbound telemetry.
- Imported recipes/templates must not execute arbitrary code or silently connect accounts.
- Dependency and copyright provenance are also release requirements.

Security fixes should have regression tests using fictional fixtures, and sensitive test traces should remain out of PR descriptions.
