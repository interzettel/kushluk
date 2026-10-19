# Independent peer review and founder verdict template

**Status:** Proposed Step 1 review format; **not a requirement to run three reviews for every CSS tweak**. Follow [CONSTITUTION.md](CONSTITUTION.md). Post to the **owning GitHub discussion issue**, not the all-issues catalogue.

## Individual peer review (copy into one independently authored comment)

```markdown
## Independent review — <actual human / model and runner> — <date>
Decision issue/atlas node:
Phase: independent | cross-examination
Actual source commit / branch:
Sources inspected (exact URLs and source identifiers):
Environment/tool access actually used:
Not accessed / not tested:

### Observed evidence
- [specific code, ADR, issue, paper or reader evidence]

### Assumptions and uncertainties
- [what was inferred, not verified]

### Decision alternatives
- A:
- B:
- C / keep current accepted baseline:

### Preferred option and strongest opposing argument
- Preference:
- Best reason my recommendation could be wrong:

### How we could falsify it
- Cheapest meaningful experiment:
- Negative/privacy/source-rights tests:
- Real paper / reader proof needed:

### Impact if accepted
- Accepted ADR(s) to amend (if any):
- Stable feature ID(s) / owning issues:
- WORK_LEDGER IDs (only if verified):
- Milestone/release impact:
- G1–G8 effect (never infer actual acceptance):

### Decision requested of founder
ACCEPT / AMEND / EXPERIMENT / DEFER / REJECT (recommended only; founder rules).
```

## Cross-examination reply

```markdown
## Cross-examination — <actual model/runner> — <date>
Earlier independent comment URL:
Other peer's attributable comment URL (not paraphrased as agreement):
Strongest credible contrary argument:
New evidence or corrected assumption:
Position: unchanged | changed (how and why):
What remains contested:
Founder question or next falsifying test:
```

## Founder-only decision record

```markdown
## Founder verdict — <date> (recorded by owner or expressly authorized delegate)
Decision issue:
Verdict: ACCEPT | AMEND | EXPERIMENT | DEFER | REJECT
Selected option and explicit boundaries:
Reasons and alternatives rejected:
Impacted accepted ADR / requirement:
Required migration or rights/privacy review:
Required test/paper/reader evidence:
Existing feature/milestone/task owner links:
Authorization granted (exact scope):
What remains prohibited or undecided:
Review/revisit trigger:
```

## Handover and provenance discipline

This template does not make GitHub comments A2A messages, and does not confirm another agent saw a review. Every participant states their own real runtime and reviewed commit. Don't include secrets, private email bodies, unlicensed assets or fabricated approval. Authoritative accepted changes move through reviewed ADR/contract PRs, and software/physical outcome evidence stays in the owning issue and original evidence ledger.
