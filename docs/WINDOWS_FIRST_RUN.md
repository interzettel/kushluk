# First Kuşluk run on Windows — guided WSL2 entry

**Issues:** [#5](https://github.com/interzettel/kushluk/issues/5) (onboarding), [#12](https://github.com/interzettel/kushluk/issues/12) (local deployment), [#47](https://github.com/interzettel/kushluk/issues/47) (scheduling). This is an **experimental first-run helper**, not a signed one-click installer, supported Windows application or independent novice acceptance.

## What a new reader needs

Windows 11 or supported Windows 10 with WSL2 and **Ubuntu 24.04** installed separately, a user with the required local install permissions, Python/pip installation permitted in Ubuntu, internet access for the owner-initiated bootstrap, and disk space for local content. The helper does not install or change WSL2 itself, does not make Docker Desktop the runtime, and does not require a GitHub/ChatGPT login.

1. Download the reviewed repository (or a signed/verified future release) and navigate to its `tools` directory in Windows File Explorer.
2. Inspect `windows_first_run.ps1` rather than executing an arbitrary downloaded script. From Windows PowerShell, use `./tools/windows_first_run.ps1` for **read-only** WSL2/Python/Git/installation checks.
3. On a **fresh** Ubuntu installation only, run `./tools/windows_first_run.ps1 -Install` to explicitly authorize Ubuntu package installation, a checkout at your Linux home directory, private Python venv and PDF dependencies. The script requires your Linux sudo password and may use the network. If a checkout already exists, it refuses to touch it or reinstall. Never use `-Install` on the active five-morning pilot checkout.
4. When installed, run `./tools/windows_first_run.ps1 -LaunchSetup`. The tool starts the existing private loopback browser onboarding; copy its displayed `http://127.0.0.1:PORT` address to your Windows browser. Enter only an approximate city location and your IANA timezone, then review source permissions and paper preference in the browser. Keep the terminal window open; Ctrl+C stops the web server.
5. For a synthetic four-page sample with no personal sources, follow [PRINT_PROOF.md](PRINT_PROOF.md); actual printers and unattended tasks are separate explicit opt-ins. Do **not** use `--print` or register a scheduler during your first setup walkthrough.

## Guarantees and limitations

By default the helper **does not** install, fetch sources, submit print/email, configure accounts, write a profile or register a task. Fresh installation is explicitly requested, and the first browser still requires the reader to provide and approve their own configuration.

The browser binds to Linux 127.0.0.1, and WSL2 localhost forwarding must be enabled and tested to reach it from the Windows browser. If that forwarding is not available, **stop and diagnose** WSL2 networking instead of opening an external interface or disabling origin protections. Do not port-forward the local setup browser. The legacy printed terminal output and one-time installed WSL environment are development tools, not a polished installer UX.

The user-owned profile, feeds, archive, and diagnostics remain private. Do not upload real home details, personal news sources, tokens or Windows task logs to public issues. The helper does not modify an existing checkout by design and does not interfere with the current pilot. Independent Windows PowerShell 5.1 testing and a novice reader trial still gate release acceptance. A future distribution may expose a signed desktop shortcut to this same noncloud, stepwise flow.
