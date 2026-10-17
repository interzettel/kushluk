# A4/US Letter/A3 physical print verification

Kushluk can verify print geometry and imposition in software. **Physical
paper handling has not been verified by CI.** A CUPS job marked "submitted"
is not evidence that the printer delivered a legible page.

## Generate offline fixtures

From a macOS or Linux setup with `pip install -e '.[pdf]'` and native
WeasyPrint dependencies:

```bash
kushluk print-proof --output-dir output/print-proof
```

The generator neither fetches RSS/calendar/weather nor contacts CUPS/SMTP.
It writes:

- `kushluk-proof-a4.pdf` — four logical, portrait A4 pages.
- `kushluk-proof-a3.pdf` — two imposed A3 landscape sides; outside `4 | 1`,
  inside `2 | 3`.
- `kushluk-proof.html` — the synthetic editorial template source.
- `kushluk-proof.json` — file names, SHA-256 digests, logical page counts and
  `physical_verified: false`.
- `PRINT-CHECKLIST.md` — checkboxes for the actual printing operator.

Keep these artifacts together and attach the checksum/filled checklist to
[#13](https://github.com/interzettel/kushluk/issues/13). Never change the
machine-readable `physical_verified` field to true from CI alone.

## A4 acceptance

Use actual A4 paper, **100% size**, no "fit to printable area", 2-sided
long-edge when the device supports it. Confirm page pairs 1/2 and 3/4 are
on the expected physical sheets, correct up/down orientation, right page
reading order, and that the footer/rules have safe margins. Test simplex
separately if the printer lacks duplex support.

## A3 folded acceptance

Use A3 landscape paper, actual size, and start with duplex short-edge.
Check that the *outside* shows 4 on the left and 1 on the right, and the
*inside* shows 2 on the left and 3 on the right. Fold at the centre. The
reading order must be cover > page 2 > page 3 > back cover. If the reverse
side is upside down, document the printer, driver, feed orientation and
correction before choosing the production duplex mode; different devices
may differ.

## Record the hardware evidence

For each printer/profile include model, firmware, CUPS queue name, macOS
or Linux and version, driverless IPP/AirPrint vs vendor driver, duplex option,
paper stock/weight, margins, actual-size setting, photographs of both sides,
whether fold/binding works and any clipped text. Compare at least one A4
and one A3 sample if hardware permits. If no A3 printer is available,
record the test as **blocked**, not passed.

Do not enable a daily auto-print schedule before physical output, queue
behaviour, a sleep/reboot test and an interruption/replay test have been
observed locally. These are separate from the deterministic CI fixture tests.
