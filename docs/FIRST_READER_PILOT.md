# First-reader usability pilot — observer kit (not a passed test)

**Status:** protocol ready for independent observation; **no participant testing is claimed here**. Owner: [#5](https://github.com/interzettel/kushluk/issues/5), evidence ledger [#43](https://github.com/interzettel/kushluk/issues/43). Scope: the local first-run experience on a real home computer, not merely green CI.

## Design and participant safety

Recruit at least **one person who has not helped develop Kuşluk** for the first pilot. Do not use yourself or an automated browser as evidence of novice usability. The participant must control their own system and give informed consent to be observed; no video/audio capture without explicit permission. Record anonymous participant code and OS/build only. Never collect home addresses, true calendar contents, subscription URLs/tokens, secret env vars, personal emails, or private printed editions. Prefer a fresh temporary profile and synthetic OPML list.

**Observer:** independently follow what the participant actually does. Give only the printed one-page handoff, not conversational hints, unless they become stuck. Record every hint and failure. A hint is a sign of friction; do not mark a hinted task unassisted.

## Starting and validating the pilot

Give the participant only [FIRST_READER_HANDOFF.md](FIRST_READER_HANDOFF.md) and the fictional OPML sample within it. This is a reproducible trial instruction, **not** an observed result. The handoff includes a clean installation attempt (U1), temporary local profile/registry paths, explicit opt-in, and a stop condition. Note any help without marking that task unassisted.

A separate synthetic integration regression, `tests/test_first_reader_journey.py`, exercises the U1–U6 **software interaction contract** using loopback HTTP, fake CUPS and fictional feeds. It is not independent reader evidence. Before sharing a redacted observation, the observer may check private record completeness with `python -m tools.first_reader_evidence /PRIVATE/PATH/record.json`; `ready_for_review` is not a gate pass or verification.

## Exact first-run sequence

| ID | Task posed to the reader | Observable acceptance | Maximum allotted |
|---|---|---|---|
| U1 | Install/start the local program using documented instructions | Open the loopback setup page without developer assistance; errors retained | 15 minutes |
| U2 | Set a home label, *approximate* coordinates and timezone | Create a private profile; identify DIN A4 / US Letter choice and explain why street address is unnecessary | 5 minutes |
| U3 | Review a synthetic OPML list, including one untrusted provider | Accurately distinguish preview from approval; activate only one intentionally | 7 minutes |
| U4 | Pause and resume an approved source | Pause leaves it disabled; resume requires distinct permission acknowledgment | 4 minutes |
| U5 | Inspect printer queues without using paper | Confirm chosen Letter paper remains in settings; explicitly start discovery, select/check a queue or understand missing CUPS; distinguish preference from queue media support; no printing | 6 minutes |
| U6 | Explain what has **not** happened | Use read-only `/status`; understand that no unattended edition, private article copying, real printer proof or notification delivery has occurred | 3 minutes |

If the printer is not configured, **U5 may succeed with an appropriate no-printer explanation**; do not pretend capability data was available. Failures of packaging or setup count as U1 problems rather than skipping the task.

## What to observe and record

For each U1–U6, record `unassisted_pass`, `assisted_pass`, `fail`, `blocked` or `not_attempted`; actual seconds; number of hints; anonymized observation and any screenshot/evidence *approved by the participant*. Ask the reader after the sequence:

- Which step seemed to send data outside the computer?
- What does approving RSS access actually permit?
- Did they expect Kuşluk to print now, or every morning automatically?
- What single instruction, label or control was hardest to understand?
- Would they knowingly repeat the setup on their personal computer?

The observer must note mismatches between expected and actual behavior, not “correct” the participant's understanding during testing.

## Proposed acceptance rule (requires owner approval)

A first-reader pilot counts as **evidence collected**, not a completed release gate, only when all six task records contain actual observations; no consent, surprise feed activation, secret leak, source text copying or spontaneous print job occurred; and the participant is independent. **Provisional product target**: U2/U3/U4/U5/U6 unassisted; U1 may be assisted once for packaging if explicitly logged and a follow-up install issue is filed. Any inability to distinguish preview and approval, copy permissions, or paper submission **blocks F-008 acceptance regardless of total task score**. UX/keyboard/screen-reader accessibility must be evaluated in a dedicated second pilot using [ACCESSIBILITY_PILOT.md](ACCESSIBILITY_PILOT.md); a single novice participant does not establish accessibility.

Do **not** mark G1–G8 / F-008 “accepted” or edit task percentages on a self-attested recording. A reviewer must inspect anonymized evidence and the relevant repository issues.

## Where evidence lives

Use [FIRST_READER_TEMPLATE.json](FIRST_READER_TEMPLATE.json) as a **blank local, private form**. Copy it outside the repository, fill only anonymized observations, retain any evidence files with consent, and link to a redacted summary in [#5](https://github.com/interzettel/kushluk/issues/5). Do not upload the raw response sheet or participant data to the public issue. Actual dates, OS details and app commit must be present; demo values or fabricated results are invalid.
