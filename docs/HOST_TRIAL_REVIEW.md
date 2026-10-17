# M2a · Review an actual local-host trial without fabricating acceptance

**Owner:** [#47](https://github.com/interzettel/kushluk/issues/47) · integrated test [#13](https://github.com/interzettel/kushluk/issues/13). This is a read-only review of local host evidence, **not** a deployed scheduler, printer action, synthetic five-day acceptance or any G1–G8 gate change.

Use the installed `kushluk` CLI on the **same machine that stores the private archive and your evidence receipts**. Start with the existing [print proof kit](PRINT_PROOF.md), [native scheduler templates](NATIVE_SCHEDULERS.md) and [physical observation instructions](FIELD_ACCEPTANCE.md). Test the PDF on paper *manually*, without automatic daily printing until orientation, queue and recovery are understood.

After each actual day, inspect the local run:

```bash
kushluk run-status --date 2026-10-19
kushluk run-report --date 2026-10-19
```

For a real observed host test, use the existing `record-field-proof` command and point `--artifact` at the **exact final archived** `YYYYMMDD-001/scheduled.json`. Add a genuine operator photo/log with `--evidence`; do not upload private files to GitHub.

```bash
kushluk record-field-proof --kind host-resume \
  --artifact /private/kushluk/archive/20261019-001/scheduled.json \
  --evidence /private/kushluk/evidence/actual-os-run-log.txt \
  --device "Actual OS and host" --operator "Operator initials" \
  --observations "What physically happened, including manual interventions" \
  --result pass --acknowledge-direct-observation \
  --output /private/kushluk/evidence/receipts/day-1.json
```

Do not report `pass` unless you genuinely observed it. Record failures and blocked checks as failures/blocked, including missing power, sleeping laptop, wrong paper side, absent printer, interrupted job and ambiguous submission. Run the **new** cross-check when you have a window to review:

```bash
kushluk host-trial-review --start-date 2026-10-19 --days 5 \
  --archive-root /private/kushluk/archive \
  --receipts-dir /private/kushluk/evidence/receipts
```

The command examines five **consecutive local edition dates**, checks the existing `run-report` software validation and expected OS start metadata, verifies actual byte/hash linkage of each passing `host-resume` receipt, rejects malformed/symlinked receipts and outputs content-free per-date statuses. No document names, personal observations, source URLs, paths or credentials are echoed; no files are modified. The summary explicitly counts **self-reports**, not accepted physical evidence. An expected start clock can be passed manually and does **not** prove that an OS timer fired. A software deadline met does **not** prove paper arrived before 08:00.

Required independent follow-up: examine OS timer execution and timezone, cold boot or sleep/wake, five actual morning editions (including failure cases), duplicate CUPS submission risk, manual intervention, file identity and original paper photos. An operator and reviewer must mark #13/#47 acceptance deliberately. This command always reports `independently_verified=false`, `unattended_host_verified=false`, `physical_print_verified=false` and `release_gate_accepted=false`.
