# Provider-specific source rights evidence checklist (F-011)

**Engineering policy:** the current RSS connector is **reference-only**. A user's saved intention `derivative` or `private-direct` is not permission to copy an article; those modes remain disabled. This file defines **what a future implementation must prove**, not legal advice or authorization to execute full-text extraction. Owner [#4](https://github.com/interzettel/kushluk/issues/4), trust [#16](https://github.com/interzettel/kushluk/issues/16).

## Evidence required per provider / adapter

Maintain one **private, dated** review record per named provider, source type, account category and intended output mode. Check:

| Field | Required proof / decision |
|---|---|
| Provider and source type | Exact publisher, delivery/API mechanism, subscription tier and geographic or account restrictions |
| Authorized principal | Who controls the account/license; proof they can access this material (without recording secrets) |
| Intended transformation | Reference/link, personal factual summary, derivative excerpt, local private direct copy, or wider redistribution; specify limits per mode |
| Source rules | Terms/license URL and **retrieval date**; publisher-supplied explicit license or written authorization when needed |
| Reuse constraints | Attribution, quotation limits, caching/deletion, rate limits, personal-use-only, AI processing restrictions, download/export restrictions |
| Rights of third parties | Wire photos, syndicated articles, fonts and illustrations require separate permissions; do not assume publisher ownership |
| Evidence integrity | Local saved copy/hashes or decision receipt; redact account details and source tokens; reviewer code and date |
| Expiration / revocation | Check cadence, how consent/reuse stops, how previously created archives are treated |
| Outcome | `reference-only`, `approved-for-separately-scoped-implementation`, `blocked`, or `unknown`; where uncertain, stay **reference-only** |

**Provider terms can change**, and a license to read privately is not necessarily a license to send the full story to an AI provider, publish a derivative, or distribute a PDF. Personal device access, paid subscription or login alone is not sufficient proof. Consider legal review for uncertain commercial use.

## Execution gates for future work

1. The record identifies the **specific adapter + operation + account license + target output**. Generic “all magazines” or “I pay for it” does not qualify.
2. A reviewer approves the evidence and logs the interpretation with date, scope, and revocation conditions. For provider-specific arrangements, obtain explicit authorization when required.
3. The implementation isolates the provider's scopes (access, allowed transformations, storage, export) with separate tests for denied, expired, no consent and revoked rights. The storage model must not silently conflate URL access with full-text rights.
4. A public share/export must have its **own** permission gate even if a private local use was allowed. Third-party embedded assets remain independently gated.
5. Include a rights receipt with the edition where appropriate, avoid leaking licenses/subscription URLs, and make bad/unknown permission status fail closed. Test on synthetic or permission-cleared samples first.
6. **Only after the above** may an issue propose making `derivative` or `private-direct` operational. Current CLI/source registry purposely prevents execution.

## Minimal evidence record (complete privately)

```yaml
provider: "REPLACE — exact provider"
adapter: "REPLACE — RSS/API/mailbox/local reader"
account_or_license_tier: "REPLACE — never store secrets"
usage_mode_requested: "reference-only | derivative | private-direct"
allowed_input: "REPLACE"
allowed_transformations: "REPLACE"
allowed_local_storage: "REPLACE"
allowed_redistribution: "REPLACE"
ai_processor_authorization: "unknown"
attribution_obligation: "REPLACE"
third_party_asset_exclusions: "REPLACE"
terms_or_license_reference: "REPLACE"
terms_review_date: "YYYY-MM-DD"
evidence_hash_or_private_reference: "REPLACE"
reviewer_code: "REPLACE"
review_state: "unknown"
expiry_or_recheck_date: "YYYY-MM-DD"
revocation_plan: "REPLACE"
implemented_and_tested: false
```

Do **not** commit populated evidence records, source subscriptions, passwords or private legal documents. This checklist is the missing proof specification; it does not itself settle contested interpretations or advance the F-011 acceptance percentage.
