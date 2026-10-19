# Kushluk Windows first-run helper. Windows PowerShell 5.1+, no background services.
# Default is read-only diagnosis. Explicit modes never print, email or schedule.
[CmdletBinding(DefaultParameterSetName='Check')]
param(
    [Parameter(ParameterSetName='Install')][switch]$Install,
    [Parameter(ParameterSetName='Launch')][switch]$LaunchSetup,
    [ValidatePattern('^[A-Za-z0-9_.-]+$')][string]$Distro = 'Ubuntu-24.04'
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$wsl = Join-Path $env:WINDIR 'System32\wsl.exe'
if (-not (Test-Path -LiteralPath $wsl -PathType Leaf)) {
    throw 'WSL is unavailable. Install Ubuntu 24.04 first.'
}
# Diagnosis uses requested distro; never default into docker-desktop.
$distros = ((& $wsl --list --quiet) -join [Environment]::NewLine) -replace [char]0, ''
if ($distros -notmatch [regex]::Escape($Distro)) {
    throw 'Requested Ubuntu WSL2 distribution missing. Install Ubuntu 24.04 before Kushluk.'
}
if ($Install) {
    Write-Host 'Explicit install selected: download Ubuntu packages and clone Kushluk.'
    Write-Host 'Existing checkouts are never updated or overwritten.'
    $command = 'set -eu; if [ -e "$HOME/kushluk" ]; then echo "Kushluk directory exists; refusing changes"; exit 3; fi; sudo apt-get update; sudo apt-get install -y git python3-venv python3-pip libpango-1.0-0 libpangocairo-1.0-0 libpangoft2-1.0-0 libcairo2 libgdk-pixbuf-2.0-0 shared-mime-info fonts-dejavu-core; cd "$HOME"; git clone https://github.com/interzettel/kushluk.git; cd kushluk; python3 -m venv .venv; .venv/bin/python -m pip install -e ".[pdf]"; .venv/bin/kushluk doctor'
    & $wsl -d $Distro -- bash -lc $command
    if ($LASTEXITCODE -ne 0) { throw 'Install did not finish. Check local messages and partial checkout before retry.' }
    Write-Host 'Install complete. Use -LaunchSetup to open the private browser setup.'
    return
}
if ($LaunchSetup) {
    $command = 'set -eu; cd "$HOME/kushluk"; test -x ".venv/bin/kushluk" || { echo "Kushluk is not installed"; exit 3; }; exec .venv/bin/kushluk setup-web --no-open'
    Write-Host 'Private local setup. Open the printed 127.0.0.1 URL in Windows browser.'
    Write-Host 'Keep this window open during setup; press Ctrl+C to stop.'
    & $wsl -d $Distro -- bash -lc $command
    if ($LASTEXITCODE -ne 0) { throw 'Local setup browser exited with an error.' }
    return
}
Write-Host 'Read-only diagnosis: no install, print, schedule or profile change.'
$probe = 'python3 --version; git --version; if [ -x "$HOME/kushluk/.venv/bin/kushluk" ]; then echo "KUSHLUK_PRESENT"; else echo "KUSHLUK_MISSING"; fi'
& $wsl -d $Distro -- bash -lc $probe
if ($LASTEXITCODE -ne 0) { throw 'Ubuntu diagnosis failed. Inspect your WSL installation.' }
Write-Host 'Use -Install only for fresh checkout; -LaunchSetup for private browser.'
