# Kushluk optional Windows A4 print handoff. Runs in Windows PowerShell 5.1+.
# Default is inspection only. Physical submission requires explicit switches.
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$PdfPath,
    [Parameter(Mandatory=$true)][string]$ExpectedSha256,
    [Parameter(Mandatory=$true)][string]$PrinterName,
    [string]$SumatraExe,
    [string]$RequestId,
    [string]$ReceiptDirectory,
    [switch]$Submit,
    [switch]$AcknowledgePossibleDuplicate
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if ($ExpectedSha256 -cnotmatch '^[a-fA-F0-9]{64}$') {
    throw 'ExpectedSha256 must contain exactly 64 hex characters.'
}
if (-not [System.IO.Path]::IsPathRooted($PdfPath) -or
    -not (Test-Path -LiteralPath $PdfPath -PathType Leaf) -or
    [System.IO.Path]::GetExtension($PdfPath).ToLowerInvariant() -ne '.pdf') {
    throw 'An existing absolute PDF path is required.'
}
$source = Get-Item -LiteralPath $PdfPath
if (($source.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
    throw 'PDF reparse points are not accepted.'
}
if ($source.Length -lt 64 -or $source.Length -gt 52428800) {
    throw 'PDF size must be between 64 bytes and 50 MiB.'
}
$actual = (Get-FileHash -LiteralPath $PdfPath -Algorithm SHA256).Hash
if ($actual -ine $ExpectedSha256) {
    throw 'PDF SHA-256 mismatch. No printer contacted.'
}
$matched = @(Get-Printer | Where-Object { $_.Name -ceq $PrinterName })
if ($matched.Count -ne 1) {
    throw 'Specified Windows printer queue was not found.'
}
$printer = $matched[0]
if ($printer.PrinterStatus.ToString() -ne 'Normal') {
    throw 'Printer does not report Normal status. No submission attempted.'
}
if (-not $Submit) {
    [pscustomobject]@{
        status = 'ready_for_operator_review'
        sha256_verified = $true
        submission_attempted = $false
        physical_print_verified = $false
        print_profile = 'a4_simplex'
    } | ConvertTo-Json -Compress
    return
}
if (-not $AcknowledgePossibleDuplicate) {
    throw 'Submission requires -AcknowledgePossibleDuplicate.'
}
if ([string]::IsNullOrWhiteSpace($RequestId) -or
    $RequestId -cnotmatch '^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$') {
    throw 'Submission requires a safe unique request ID.'
}
if ([string]::IsNullOrWhiteSpace($ReceiptDirectory) -or
    -not [IO.Path]::IsPathRooted($ReceiptDirectory) -or
    -not (Test-Path -LiteralPath $ReceiptDirectory -PathType Container)) {
    throw 'Submission requires an existing absolute owner-controlled receipt directory.'
}
$receiptRoot = Get-Item -LiteralPath $ReceiptDirectory
if (($receiptRoot.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
    throw 'Receipt directory must not be a reparse point.'
}
if ([string]::IsNullOrWhiteSpace($SumatraExe) -or
    -not [IO.Path]::IsPathRooted($SumatraExe) -or
    -not (Test-Path -LiteralPath $SumatraExe -PathType Leaf) -or
    [IO.Path]::GetFileName($SumatraExe) -ine 'SumatraPDF.exe') {
    throw 'Submission requires an explicit trusted SumatraPDF.exe path.'
}
$receiptFile = Join-Path $receiptRoot.FullName ($RequestId + '.json')
$stagedPdf = Join-Path $receiptRoot.FullName ($RequestId + '.pdf')
if ((Test-Path -LiteralPath $receiptFile) -or (Test-Path -LiteralPath $stagedPdf)) {
    throw 'Request ID already has artifacts. No resubmission.'
}
# Stage exact bytes in a private Windows directory before invoking the printer.
[IO.File]::Copy($source.FullName, $stagedPdf, $false)
$stagedHash = (Get-FileHash -LiteralPath $stagedPdf -Algorithm SHA256).Hash
if ($stagedHash -ine $ExpectedSha256) {
    Remove-Item -LiteralPath $stagedPdf -Force
    throw 'Staged PDF hash mismatch. No submission.'
}
# An exclusive receipt is written BEFORE an external print attempt.
# Any ambiguous error or process interruption remains non-retryable.
$receipt = @{
    format = 'kushluk-windows-print-attempt-v1'
    request_id = $RequestId
    sha256 = $stagedHash.ToLowerInvariant()
    state = 'submission_outcome_uncertain'
    print_profile = 'a4_simplex'
    physical_print_verified = $false
    attempted_at_utc = [DateTime]::UtcNow.ToString('o')
}
try {
    $handle = [IO.File]::Open($receiptFile, [IO.FileMode]::CreateNew,
                            [IO.FileAccess]::Write, [IO.FileShare]::None)
    try {
        $payload = [Text.Encoding]::UTF8.GetBytes(($receipt | ConvertTo-Json -Compress) + [Environment]::NewLine)
        $handle.Write($payload, 0, $payload.Length)
        $handle.Flush()
    } finally {
        $handle.Dispose()
    }
} catch {
    throw 'Could not create exclusive receipt. No printing attempted.'
}
$settings = 'simplex,portrait,paper=A4,noscale,ignore-pdf-print-settings'
try {
    & $SumatraExe '-print-to' $PrinterName '-print-settings' $settings $stagedPdf
    $code = $LASTEXITCODE
} catch {
    throw 'Print process exception. Outcome uncertain; inspect Windows queue before a new request.'
}
if ($code -ne 0) {
    throw ('Print process exit code ' + $code + '; outcome may be uncertain. Inspect queue before any reprint.')
}
[pscustomobject]@{
    status = 'print_process_exit_zero_not_physically_verified'
    request_id = $RequestId
    sha256_verified = $true
    submission_attempted = $true
    physical_print_verified = $false
    receipt = $receiptFile
} | ConvertTo-Json -Compress
