# M2a: run an actual private beta acceptance session

**Milestone:** proposed `v0.3.0-beta.1`. **Status:** software tools prepared;
no beta has been tagged or published. The existing [source-only alpha](https://github.com/interzettel/kushluk/releases/tag/v0.2.0-alpha.1)
remains the available release. An operator/self-reported `pass` is **not**
independent printer, host, reader or rights approval. G1–G8 remain
**0/8 independently verified (00.00%)** until genuine outside review.

For reproducibility, record the **actual tested source commit** before
enrolling anyone (`git rev-parse HEAD` in the checkout). The software
preflight runs from that checkout, not from the published alpha wheel alone.
Install dependencies in a fresh virtual environment and keep all evidence
under a private folder outside the checkout.

The minimum private pilot requires **one real A4 print**, an observed
host restart/recovery run, a consenting **independent novice** completing
U1–U6, and a source/rights/secret checklist. Unlike the later stable-release
gate, the beta preflight does not demand *five unattended mornings* and
explicitly cannot claim that a scheduler fired or that a printer delivered.

## 1. Produce and physically inspect a synthetic A4 sample

Use an actual printer that you have permission to operate; no third-party
newsletter articles or images are necessary. Begin with the [print-proof
steps](FIELD_ACCEPTANCE.md). Configure `a4-home`, print at actual size,
inspect all four pages, page order, margins, duplex and readability. Record a
failed/blocked run honestly instead of reprinting without diagnosis.

```bash
kushluk print-proof --output-dir /PRIVATE/proof
kushluk inspect-print --profile a4-home \
  --pdf /PRIVATE/proof/kushluk-proof-a4.pdf \
  --output-dir /PRIVATE/inspect-a4 --rasterize
# Only after personally inspecting actual A4 pages and saving an actual local photo:
kushluk record-field-proof --kind paper-a4 \
  --artifact /PRIVATE/proof/kushluk-proof-a4.pdf \
  --inspection /PRIVATE/inspect-a4/inspection.json \
  --device "Printer and driver actually observed" \
  --operator "Anonymous local initials" \
  --observations "Observed four A4 pages, ink, duplex, clipping and legibility" \
  --result pass --acknowledge-direct-observation \
  --evidence /PRIVATE/photo-of-real-print.jpg \
  --output /PRIVATE/receipts/a4.json
```

The recorder requires a matching `a4-home` PDF inspection, SHA-256
identity and a private receipt directory. Do not place the photo or
receipt in the Git repository.

## 2. Observe real host restart / scheduler behavior

Follow [the host trial instructions](HOST_TRIAL_REVIEW.md); use actual OS
scheduler logs from the same computer and a real `scheduled.json` in your
private archive. Observe a real restart, resume and failure/retry behavior,
including duplicate-submission risk. Store an actual log/evidence file and
record an independent **operator self-report** `host-resume` receipt.

The reviewer correlates a 5-day window, but **the beta preflight only looks
for one matching operator report and a validated archived software run**.
That is not independent evidence that a reboot occurred. The later stable
release requires five *actual*, consecutive unattended mornings.

## 3. Independent first reader U1–U6

Obtain participant consent and follow
[FIRST_READER_PILOT.md](FIRST_READER_PILOT.md) and
[FIRST_READER_HANDOFF.md](FIRST_READER_HANDOFF.md) using fictional feeds.
Do not pre-install or coach without recording assistance. Complete a private
copy of [FIRST_READER_TEMPLATE.json](FIRST_READER_TEMPLATE.json). Review
the printed outcome and note every hint, failed task and misunderstanding.
For the provisional beta target, U2–U6 must be unassisted; an assisted U1
install requires an explicit issue and reviewer decision, not an invisible
pass. A separate [accessibility pilot](ACCESSIBILITY_PILOT.md) remains open.

## 4. Safety/rights boundary and operator checklist

Copy [BETA_PILOT_SAFETY_TEMPLATE.json](BETA_PILOT_SAFETY_TEMPLATE.json)
outside the repository and fill the six Boolean checks from actual
observations/permissions. Change `status` to `operator-checklist`.
Do not change `human_rights_review_completed`,
`independently_verified`, or `release_gate_accepted` to true yourself.
If any permissions or safe recovery steps are missing, leave the matching
check false and do not enroll a pilot.

## 5. Locally cross-check the evidence (zero uploads)

From a local repository checkout (with the alpha or current build installed):

```bash
python -m tools.beta_pilot_preflight \
  --a4-receipt /PRIVATE/receipts/a4.json \
  --pdf /PRIVATE/proof/kushluk-proof-a4.pdf \
  --inspection /PRIVATE/inspect-a4/inspection.json \
  --paper-evidence /PRIVATE/photo-of-real-print.jpg \
  --archive-root /PRIVATE/archive \
  --host-receipts /PRIVATE/receipts \
  --host-start-date 2026-10-19 \
  --reader-record /PRIVATE/first-reader.json \
  --safety-checklist /PRIVATE/safety.json
```

The command is entirely read-only, makes **no network/print/email calls**,
and outputs only fixed field statuses and missing domains. Even if all
four domains match, `status: operator_packet_ready_for_independent_review`
means **an outside reviewer needs to inspect the genuine private evidence**.
It always reports `beta_publication_authorized=false` and
`G1_to_G8_independently_verified=0`. It cannot determine whether an
observer or printer in a photo was real, consent was freely given or
publisher licences allow copying; these require direct human review.

## Review and release decision

The independent reviewer must inspect the real pages/device, OS timer/reboot
evidence, consent, novice task observations and content-rights context.
Create only **redacted, consent-cleared issue summaries** in [#13](https://github.com/interzettel/kushluk/issues/13)
(printer/host) and [#5](https://github.com/interzettel/kushluk/issues/5)
(reader). No raw photos, logs, private reports, email or device identifiers
should be uploaded to GitHub.

Only after that external acceptance should the owner decide which G1–G8
have legitimate evidence, and separately authorize `0.3.0b1`, tag
`v0.3.0-beta.1`, and an explicitly constrained private distribution.
No automatic version bump, invitation or beta publication is implemented
by this pilot tooling.
