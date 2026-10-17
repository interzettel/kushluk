# Independent keyboard and screen-reader pilot (A1–A5)

**Separate from** the ordinary U1–U6 novice trial. This is a **human observation protocol**, not a passed accessibility audit. It does not mean WCAG conformance, assistive-technology compatibility, or physical printer success. Tracks issue [#5](https://github.com/interzettel/kushluk/issues/5).

A participant who did not build Kuşluk should use a real Linux/macOS computer and a keyboard-only workflow and, where available, their familiar screen reader (VoiceOver on macOS or Orca on Linux). Record OS/browser/assistive-technology versions privately. If no screen reader or knowledgeable participant is available, record **blocked**, not passed. Obtain observation consent; do not record a screen, voice, personal data or actual paid feeds without separate permission.

Give only the [first-reader handoff](FIRST_READER_HANDOFF.md) with fictional home data, including deliberately choosing **US Letter**, and the fictional OPML list. No administrator should secretly preconfigure accounts or printers. Log observer hints as assisted outcomes.

| Task | What the independent participant attempts | Evidence to observe |
| --- | --- | --- |
| **A1** | Navigate the first-run form with keyboard only (Tab/Shift+Tab and skip link) | Logical focus order, visible focus and access to submit/cancel without mouse |
| **A2** | Use screen-reader labels and instructions for location, time zone, and A4/Letter selector | The selected paper choice, mandatory fields and descriptions are announced intelligibly |
| **A3** | Reach RSS preview, approve exactly one fictional source, pause/resume using keyboard | No surprise source activation, separate consent correctly announced |
| **A4** | Open the **read-only Morning status** route `/status` | State, archive, print-queue vs physical delivery distinction, and next action understood in reading order |
| **A5** | Zoom to 200%, navigate forms/status and optionally enable OS high contrast | No obscured action or offscreen keyboard focus; note clipping, contrast and any inaccessible text |

Observers record actual elapsed seconds, number of hints, pass/assisted/fail/blocked, and specific friction in a **private copy** of [ACCESSIBILITY_TEMPLATE.json](ACCESSIBILITY_TEMPLATE.json). Participants answer the five open comprehension questions after the tasks; answers are not corrected during the session. The source SHA and observed date are mandatory. Use an anonymized participant code; keep `independently_verified` and `release_gate_accepted` **false** until a separate review.

Run this optional private completeness preflight:

```bash
python -m tools.accessibility_evidence /PRIVATE/accessibility-record.json
```

The tool checks schema consistency **only**, never echoes free-text notes, opens a network connection or verifies a human. Even `ready_for_review` cannot advance an acceptance gate. Actual reviewer signoff needs a consent-cleared, redacted summary linked privately to #5, with blocking problems resolved or explicitly documented. Accessibility remains unverified until then.
