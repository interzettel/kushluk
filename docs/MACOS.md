# Run Kushluk on macOS

Kushluk's local Python engine is intended to run on a Mac without Docker or a hosted service. The executable **Stage 1 software** produces four ordered logical A4 pages. Native A4/A3 physical imposition and real-printer testing are separate delivery work.

This guide covers **native Apple Silicon and Intel Macs**. macOS software compatibility is checked in CI. Successful printer submission does **not** establish that a physical sheet emerged correctly.

## Install (macOS + Homebrew)

You need [Homebrew](https://brew.sh/), Python 3.11+ and Pango for the optional WeasyPrint PDF renderer.

```zsh
brew install python@3.12 pango

git clone https://github.com/interzettel/kushluk.git
cd kushluk
python3.12 -m venv .venv
source .venv/bin/activate

# WeasyPrint needs native Pango libraries; use Homebrew's actual prefix,
# /opt/homebrew on most Apple Silicon Macs and /usr/local on most Intel Macs.
export DYLD_FALLBACK_LIBRARY_PATH="$(brew --prefix)/lib${DYLD_FALLBACK_LIBRARY_PATH:+:$DYLD_FALLBACK_LIBRARY_PATH}"

python -m pip install -e '.[dev,pdf]'
python -m weasyprint --info
kushluk doctor
```

The Python PDF extra is optional. For a local HTML-only run, you can skip Pango and install `python -m pip install -e '.[dev]'`, then use `--no-pdf`. On a Mac with Pango installed but hidden from Python, `kushluk doctor` should now report an optional/unusable PDF runtime instead of declaring it ready. If you see a missing `libpango` / `libgobject` error, confirm `brew --prefix` and set `DYLD_FALLBACK_LIBRARY_PATH` in **the process launching Python**. Restart a shell after installing native libraries if necessary.

Homebrew-installed Python and Pango should match your Mac's architecture. Avoid mixing Intel/Rosetta Homebrew (`/usr/local`) with an arm64 Python environment (typically `/opt/homebrew`) or vice versa.

## Make and inspect an edition

```zsh
kushluk generate --date 2026-09-23 --no-pdf
kushluk generate --date 2026-09-23
kushluk archive-list
```

`output/` contains local HTML/Markdown and, when rendering succeeds, a validated PDF. Personal edition files are local; do not upload a private archive to troubleshoot. Weather/RSS require a connection but should degrade when a source is unavailable. The Stage 1 calendar fixture is provided for the first run.

These commands **generate**, not automatically print or schedule a morning delivery.

## Print through the Mac's existing printer queue

Add and test a printer in **System Settings → Printers & Scanners**. A compatible printer registered via AirPrint can also appear as a macOS/CUPS destination; the Kushluk process still submits through the Mac's local queue, **not** an unattended iPhone/iPad AirPrint dialog.

```zsh
lpstat -p -d              # available printers and default
lpoptions -p "YOUR_PRINTER_NAME" -l   # supported options, if exposed by driver
export KUSHLUK_PRINTER="YOUR_PRINTER_NAME"
kushluk doctor
kushluk generate --print  # submits a newly generated, validated PDF
```

Do not use `--print` until you've verified the printer and paper settings. The current print profile is **A4**, with automatic two-sided long-edge printing only if CUPS advertises duplex support; otherwise the request is explicitly single-sided. An explicit `KUSHLUK_PRINTER` wins; if unset, the CUPS `LPDEST`, `PRINTER`, and system/default destination are considered in that order. Missing/unknown printer capabilities must not be described as proven support.

`lp` returning successfully means **the job was submitted**, not that the job printed. Check the actual queue, duplex orientation, media, margins, and the resulting paper. Physical A4/A3 profile trials remain open under [#46](https://github.com/interzettel/kushluk/issues/46) and [#13](https://github.com/interzettel/kushluk/issues/13).

Each explicit `kushluk generate --print` call can submit another job. **Do not install a repeating scheduler yet**; idempotent unattended execution and duplicate-print guards are still tracked in [#47](https://github.com/interzettel/kushluk/issues/47).

## Scheduling and Apple controls — not shipped yet

A future native **launchd** agent and optional **Apple Shortcuts** trigger should invoke the same Kushluk CLI/run contract without placing editorial/layout logic into Shortcuts. launchd does not automatically inherit environment variables exported by your interactive zsh session. It needs explicit paths to the venv executable, a defined working directory, timezone/location and only the necessary credentials/variables. Do not place private ICS URLs or SMTP passwords in a committed plist or public issue.

The current prototype does **not** yet provide the stable, idempotent daily-run command, pause/reprint state, or a verified unattended AirPrint route. These belong to AUT-02/03/05/07/08 under [#47](https://github.com/interzettel/kushluk/issues/47); real hardware acceptance is separate.

## What automated testing covers

[CI](https://github.com/interzettel/kushluk/actions/workflows/ci.yml) runs the Python unit suite on Linux and macOS (Apple Silicon and Intel); the macOS jobs install native Pango, load WeasyPrint, run the CLI and validate the current four-page A4 PDF. Printer command behavior is covered by mocked CUPS tests. GitHub-hosted CI has **no real printer**, so it cannot prove printed sheets, waking a sleeping Mac, printer reachability, launchd reliability, or hardware duplex handling.

References: [WeasyPrint native library setup](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html) and [CUPS command-line print options](https://apple.github.io/cups/doc/options.html).
