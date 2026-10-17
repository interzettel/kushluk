# M1 · First installable preview — candidate validation

**Status:** engineering candidate only, under [#54](https://github.com/interzettel/kushluk/issues/54) and [#87](https://github.com/interzettel/kushluk/issues/87). **No tag or release has been created.** The package metadata is still development version `0.1.0`; `v0.2.0-alpha.1` is a **proposed** future release decision, not an installed or published version.

## What is actually installable

A standard Python `py3-none-any` wheel and corresponding source distribution can be built with [Hatchling](https://hatch.pypa.io/) and [build](https://build.pypa.io/). Both should include `kushluk` runtime modules, its HTML template, package metadata, CLI entry point, README and license/notices. The wheel contains portable Python code; **PDF rendering depends on native libraries and platform-specific fonts**, so installability does not imply identical raster output on every computer.

The installed `kushluk preview` command produces one fixed, four-logical-page **fictional** edition. Its date, timestamp, source labels, article copy and story IDs are frozen. It never reads a local profile, contacts any API, discovers accounts, prints to CUPS, or sends email. It can generate HTML without WeasyPrint, with PDF rendering explicitly opt-in.

## Get a preview candidate from CI

Open [GitHub Actions → CI](https://github.com/interzettel/kushluk/actions/workflows/ci.yml), choose the latest successful **M1-enabled** run, and download one of the `kushluk-m1-*` artifact ZIPs. Linux Python 3.11/3.12 and macOS Apple Silicon/Intel variants include:

- `kushluk-0.1.0-py3-none-any.whl` — source-free Python distribution
- `kushluk-0.1.0.tar.gz` — buildable source distribution
- `wheel/kushluk-preview.html`, `.md`, `-edition.json`, `preview-manifest.json` — synthetic sample generated **after clean wheel installation**
- `sdist/...` — equivalent files generated from the **clean sdist installation**
- `release-evidence.json` — platform, Python version, archive SHA-256s and verification state
- `m1-preflight.json` — independent checksum/installed-preview/rights-boundary audit; **not a release approval**
- On macOS: `wheel/kushluk-preview.pdf` and `sdist/kushluk-preview.pdf` — checked as four logical A4 PDF pages

CI artifacts are temporary (14-day retention), **not** signed release assets, release tags or an approval to put the application into unattended production. The artifact ZIP is only for developer review. Verify checksums before installing any copied files.

## Fresh installation without cloning

Unzip a candidate ZIP, then run from a **different directory** in a fresh virtual environment. For Linux/macOS:

```bash
python3 -m venv kushluk-preview-venv
source kushluk-preview-venv/bin/activate
python -m pip install "/absolute/path/to/kushluk-0.1.0-py3-none-any.whl"
kushluk --help
kushluk preview --output-dir ./kushluk-sample
```

For the optional PDF path, install the PDF extra (native Pango/cairo/font dependencies may be needed; see [macOS setup](MACOS.md)) and use a **new output directory**:

```bash
python -m pip install "/absolute/path/to/kushluk-0.1.0-py3-none-any.whl[pdf]"
kushluk preview --output-dir ./kushluk-pdf-sample --pdf
```

Use the absolute wheel path; do **not** attempt `pip install kushluk==0.2.0a1` or assume a PyPI package exists. To check source distribution parity, create a separate virtual environment and use `pip install "/absolute/path/to/kushluk-0.1.0.tar.gz[pdf]"` before invoking the same command.

The preview refuses to overwrite a nonempty output directory. It is *not* a daily-news generator: there are no personal calendar entries, current weather, paid article excerpts, live sources or rights-uncleared photos. `preview-manifest.json` identifies fixture provenance, generated file hashes and zero network/print/mail submissions. HTML/Markdown/JSON bytes are deterministic from one version of the installed code. PDF **structure** (four logical A4 pages, numbering and ordering) is checked; PDF binary hashes can legitimately differ across operating systems/fonts. The build reproducibility gate separately compares SHA-256 **wheel/sdist** outputs from two fixed-epoch builds on the same runner.

## Reproduce the CI build yourself

From a clean repository checkout with Python 3.11+:

```bash
python -m pip install build
python -m tools.release_check --artifact-dir output/m1-candidate
```

With `pip install -e '.[pdf]'` and the native PDF libraries present, use `--pdf` to require an actual four-page PDF from **both** isolated wheel and sdist installs. The verifier builds the distributions twice with a stable `SOURCE_DATE_EPOCH`, checks files/entry points/licenses, compares artifact checksums and creates two **new isolated virtual environments** to test installed entry points from outside the checkout. A failure is a package gate, not a green local fixture substitute.

The [CI workflow](../.github/workflows/ci.yml) checks Linux 3.11/3.12 (portable HTML) plus macOS Apple Silicon/Intel (PDF + native Pango) and uploads the evidence artifacts. It also preserves the existing network-blocked smoke and source-code tests. Windows is **not** part of the validated M1 support matrix.

## Installed dependency inventory and local archive inspection

Every clean installed wheel and source preview includes a machine-readable `installed-environment.json` and a SHA-256 digest linked from `release-evidence.json`. The inventory lists actual installed Python package versions and self-declared license metadata for review. Missing metadata is **not** equivalent to a prohibited license, and a license field does **not** constitute independent permission verification. `pip check` confirms the installed Python dependency graph is not internally inconsistent. No vulnerability advisories or native Pango/Fontconfig/font licenses are independently evaluated. See [DEPENDENCY_AUDIT.md](DEPENDENCY_AUDIT.md).

For an existing private archive, the new **non-mutating** `kushluk archive-check --archive-root /private/archive` reports only version/structure counts. Valid schema-v2 metadata is classed structurally readable; legacy schema-v1 or future unknown archives remain untouched and require a separately specified migration. An archive check never authorizes printing or a repeated delivery. See [ARCHIVE_COMPATIBILITY.md](ARCHIVE_COMPATIBILITY.md).

The [compatibility matrix](COMPATIBILITY_MATRIX.md) records exactly which software/platform paths have CI evidence and which hardware/device claims remain open. A [human alpha approval handoff](RELEASE_APPROVAL.md) keeps all release publication steps separate from this development preview.

The optional `kushluk-m1-isolated-0.2.0a1-trial` CI artifact is a
*disposable proposed-version test* built from a temporary tracked source
snapshot. It is not the development package or an officially supported
alpha. The checked-in package remains `0.1.0`. See the
[M1 alpha evidence and remaining signoff](M1_ALPHA_CANDIDATE.md).

## Known limitations and release decision

- **No device proof:** four PDF pages in CI do not prove A4/A3 duplex, print-stock behavior, CUPS compatibility, folding/binding, or correct user-visible paper.
- **No unattended-host proof:** scheduler/retry protections exist, but five consecutive real mornings, restart and printer recovery remain open.
- **No fully nontechnical setup:** managing Python, virtual environments, native PDF libraries, credentials and CUPS is still a developer-oriented installation.
- **No private/paid-content redistribution license:** local sources and image grants remain subject to provider rights. This sample embeds only original synthetic text.
- **No production cross-platform guarantee:** Linux software and macOS (ARM/Intel) CI are automated checks, not approval of every supported printer, e-reader or OS version.
- **No migrations declared complete:** schema-v2 metadata exists, but older-archive migration and local-vault compatibility require broader acceptance evidence.
- **No artifact signature/SBOM audit yet:** dependencies and optional native libraries need final third-party, vulnerability and licensing review before a public release.
- **No telemetry or paid platform fee:** the fixture itself performs no external calls or deliveries; dependency installs/builds can use package indexes.

**M1 candidate exit:** clean wheel/sdist builds and installs, fixed synthetic sample, package/rights documentation and cross-platform CI. **M1 actual prerelease:** explicitly approved version change, release notes, final dependency/licence and safety review, tag and GitHub Release made as a **separate** deliberate action. Neither this PR nor merging a milestone issue authorizes publication. See [Release Plan](RELEASE_PLAN.md), [Security](../SECURITY.md) and [Work Ledger](WORK_LEDGER.md).
