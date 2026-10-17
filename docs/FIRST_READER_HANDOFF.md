# First-reader handoff — U1–U6

**For one consenting, independent participant and an observer.** This is a *research session* using fictional data, not a live print or morning-delivery setup. No participant result has been recorded. Use with [FIRST_READER_PILOT.md](FIRST_READER_PILOT.md), which controls timing, scoring and consent.

## Participant-facing instructions

> Your task: Set up a local morning-newspaper profile and choose *one fictional source*. Nothing should print or automatically run. You may stop whenever you wish. Say aloud what you expect each step to do. The observer should not guide you unless you ask for help; any help will be logged.
>
> Please do not enter real subscriptions, names, addresses, personal coordinates, calendar details, credentials or printer secrets. For the location, use **latitude 50.9 / longitude 6.9**, time zone **Europe/Berlin**, and home name **Test Morning**. These are fictional test values, not your address.
>
> **U1: Start.** On Linux or macOS, open the repository checkout and follow the commands below. Tell the observer where you get stuck.
>
> **U2: Home.** In the browser, save the fictional home settings. Observe the recommended **DIN A4 and US Letter** paper sizes; choose **US Letter** for this controlled trial, even if you normally use A4. Describe what changes and what is *not* activated.
>
> **U3: Sources.** On “Review your sources,” paste the fictional OPML below, preview it, and approve **only Trusted Example**, not Untrusted Example. Explain what you think approval permits.
>
> **U4: Pause.** Pause the approved feed, then resume it. Observe whether fresh confirmation is required.
>
> **U5: Printer.** Open the printer step, confirm that US Letter is still selected, and explain whether the printer itself advertises Letter paper. Only when you choose, discover local printer queues. If a queue is present, check it and optionally save it with the separate confirmation. If none are reported, explain the result. **Do not print anything.**
>
> **U6: Finish.** Open the local **Morning status** page (`/status`). Explain why “Not started” or a queued print would *not* prove physical delivery, and what setup did *not* do: copy paid articles, contact feeds, schedule a newspaper or print on paper.

### Starting commands (Linux/macOS)

The installation itself is being tested; a failure to understand or complete these commands is important evidence. **Do not pre-install or troubleshoot secretly.** Use an actual clean checkout or GitHub source ZIP; if `git` is unavailable, record that as U1 friction.

```sh
git clone https://github.com/interzettel/kushluk.git
cd kushluk
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
PILOT_DIR="$(mktemp -d)"
export KUSHLUK_PROFILE_FILE="$PILOT_DIR/profile.json"
export KUSHLUK_SOURCE_REGISTRY="$PILOT_DIR/sources.json"
kushluk setup-web --no-open
```

Open the displayed `http://127.0.0.1:PORT/` link on the same computer. The two environment overrides keep the fictional home profile and approved-source list out of any pre-existing installation. Stop the temporary server with Ctrl+C. Keep the terminal and test files private.

### Fictional reading list to paste (do not use real accounts)

```xml
<opml version="2.0">
  <body>
    <outline text="Trusted Example" xmlUrl="https://reader.example.org/rss"/>
    <outline text="Untrusted Example" xmlUrl="https://untrusted.example.org/rss?token=FAKE"/>
  </body>
</opml>
```

Those addresses are reserved examples, not working subscriptions. Import/preview/approval does not contact either host; if the participant later deliberately runs a separate live source check, that is **outside this pilot**.

## Observer-facing evidence

Before starting, obtain explicit consent to observation and note any separate consent to share redacted findings. Do not capture audio, video, screen, home address, personal account data or real printed editions without separate permission. Don't answer U6 for the participant. **U1 includes installation difficulty**; installing it on their behalf is assisted, not unassisted. Record whether the reader understands the A4/Letter distinction and the read-only Morning status explanation; confusion or hints belong in the private U2, U5 and U6 notes, not as invented task passes.

Record task outcome, measured time, hints, and observed friction in a **private local copy** of [FIRST_READER_TEMPLATE.json](FIRST_READER_TEMPLATE.json). Replace its example fields with actual anonymous codes, observed OS, local date and **real 40-character source commit**. After an actual session change `status` from `template-not-observation` to `observation`; fill all U1–U6 records and the five comprehension responses, including failures/blocks. Keep `independently_verified: false`, `reviewer_signoff: not_reviewed` and `release_gate_accepted: false`. Do not commit or upload the filled record.

For a local **completeness preflight only**:

```sh
python -m tools.first_reader_evidence /PRIVATE/PATH/first-reader-record.json
```

The command prints only issue *field names* and `ready_for_review` or `incomplete`. It does **not** echo free-text notes, transmit private records, certify an independent participant or accept a release gate. A separate human reviewer must inspect an appropriately redacted report before the owner issue #5 can be advanced.

The synthetic CI journey in `tests/test_first_reader_journey.py` covers HTTP mechanics for U1–U6, but **cannot** measure novice understanding, assistive technology, physical printing, e-reader handling or unattended-host behavior. Keep those items open.
