# Experimental Windows print handoff — A4 simplex only

**Owners:** [#46](https://github.com/interzettel/kushluk/issues/46), [#13](https://github.com/interzettel/kushluk/issues/13). This is an **operator-triggered experiment**, not part of the automatic `kushluk run` pipeline and not a physical device acceptance. Do not schedule it over the active 20–24 October 2026 digital-only WSL2 trial.

## Why a bridge?

The real HP DeskJet 2800 is configured as a **Windows** printer. The existing Python printer backend in Kuşluk relies on Linux/macOS **CUPS** commands. A Windows `Get-Printer` queue is **not** automatically a WSL2 CUPS queue. The correct path is an explicit transport adapter, rather than assuming `lp` works inside Ubuntu.

The experimental script at `tools/windows_print_handoff.ps1` uses the separately installed [SumatraPDF command-line printing interface](https://www.sumatrapdfreader.org/docs/Command-line-arguments). SumatraPDF is **optional software**, not installed, downloaded, or bundled by Kuşluk. Verify the official binary, licenses and system requirements yourself. Its exit code cannot report post-submission failures inside the Windows spooler.

## Read-only inspection first

In **Windows PowerShell**, provide an *absolute Windows-accessible* path to the approved A4 PDF, its exact SHA-256 digest, and the exact configured Windows printer name:

```powershell
# Illustrative placeholders; no printer is contacted WITHOUT -Submit
.\tools\windows_print_handoff.ps1 `
  -PdfPath "C:\private\edition.pdf" `
  -ExpectedSha256 "REPLACE_WITH_REAL_64_CHARACTER_SHA256" `
  -PrinterName "REPLACE_WITH_EXACT_WINDOWS_PRINTER_NAME"
```

The default mode checks file existence and SHA-256, and requires one exact `Get-Printer` queue whose reported status is `Normal`. The script returns `submission_attempted=false` and `physical_print_verified=false`. The synthetic print-proof hash is NOT interchangeable with a real archived edition's digest.

## Explicit one-attempt submission (later, separate approval)

The physical experiment requires an owner-reviewed original PDF and all of: `-Submit`, `-AcknowledgePossibleDuplicate`, a unique `-RequestId`, an existing private `-ReceiptDirectory`, and the absolute path to a trusted `SumatraPDF.exe`. The script copies verified PDF bytes into the operator's Windows directory, rechecks their SHA-256, and writes a create-only receipt **before** invoking the process. It supplies `simplex,portrait,paper=A4,noscale,ignore-pdf-print-settings` and the **explicit named** queue. There is no fallback to another printer and no silent retry.

```powershell
# Replace ALL illustrative values only after inspecting actual printer and file.
.\tools\windows_print_handoff.ps1 `
  -PdfPath "C:\private\edition.pdf" `
  -ExpectedSha256 "REPLACE_WITH_REAL_64_CHARACTER_SHA256" `
  -PrinterName "REPLACE_WITH_EXACT_WINDOWS_PRINTER_NAME" `
  -SumatraExe "C:\Program Files\SumatraPDF\SumatraPDF.exe" `
  -ReceiptDirectory "C:\private\kushluk-print-receipts" `
  -RequestId "approved-proof-001" -Submit -AcknowledgePossibleDuplicate
```

Create the private receipt directory in advance and restrict its Windows ACLs; the staged PDF **contains potentially private newspaper content**. An uncertain process state leaves a receipt and blocks reuse of that request ID. Check the real Windows print queue and physical sheets before any separately authorized reprint.

## Acceptance still open

Neither GitHub CI nor the PowerShell script verifies native Windows execution, printer-driver reliability, actual paper, queue completion, A4 margins, ink coverage, sleep/reboot, cancellation or real duplicates. The repository test is a source-level guardrail only; a Windows PowerShell 5.1 parser/run, Sumatra installation/licensing check, controlled dry-run and explicit printer trial are still needed. Process exit code 0 is **not** physical delivery. No release gates G1–G8 or work-ledger checkboxes change from this experiment.

A later production transport should expose a stable platform-independent archive-only print operation and explicitly reconcile uncertain queue outcomes without refetching news or regenerating an edition.
