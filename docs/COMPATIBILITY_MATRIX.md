# Preview platform and delivery compatibility matrix

**Status 2026-10-17:** software CI evidence, *not hardware certification*. Owner [#54](https://github.com/interzettel/kushluk/issues/54), [#46](https://github.com/interzettel/kushluk/issues/46), [#47](https://github.com/interzettel/kushluk/issues/47).

| Environment | Installed / exercised path | Proven boundary | Open proof |
|---|---|---|---|
| Linux, Python 3.11 | clean wheel + sdist, installed CLI and offline synthetic HTML | reproducible package bytes and input/manifest checks in CI | PDF/native fonts and actual distro/host device |
| Linux, Python 3.12 | clean wheel + sdist, installed CLI and offline synthetic HTML | same software-only boundaries | PDF/native fonts and printer |
| macOS 15 Apple Silicon, Python 3.12 | native Pango + clean wheel and sdist, synthetic four-page A4 PDF, print imposition fixtures | software PDF structure, page count, output/provenance contract | paper, printer queue, user session/wake and OS upgrades |
| macOS 15 Intel, Python 3.12 | same native PDF and package tests | software PDF, *not* pixel-identical rendering across hardware | paper, native font license/identity and sleep/restart |
| Windows | none claimed by installable-preview acceptance | source may be portable; **no supported binary/print claim** | installer, PDF natives, job scheduling, printer integration |
| Home A4 printer | synthetic A4 profile and human print-proof kit | A4 logical page geometry in software | actual duplex edge, tray, margins, contrast and printing |
| A3 folded | synthetic A3 imposition | two imposed sides, outside 4|1 and inside 2|3 | **real A3 device**, flip/fold and media stock; optional if unavailable |
| SMTP | bounded source code/fixture tests | SMTP submission accepted only | receipt delivery, retries and private credentials |
| EPUB/e-reader | software EPUB/conformance tests tracked elsewhere | format checks only | actual reader layout/navigation and accessibility |
| Unattended Linux/macOS | disabled systemd-user/LaunchAgent templates; status and receipt tools | repeatable software outcomes, at-most-once policy | wake/reboot, OS timer, printer recovery and five real mornings |

Every row is bounded by the actual CI run's platform/version and SHA. For current status use [Actions](https://github.com/interzettel/kushluk/actions/workflows/ci.yml) and **record the exact successful run**; a markdown table is not a replacement for build evidence.

The software artifact is currently a **development 0.1.0 wheel/sdist**, *not* the proposed `v0.2.0-alpha.1` release. All local device and identity evidence is stored privately. Do not copy reader calendar, source URLs, archived editions, printer serial numbers or actual photographs to public Actions artifacts.

For release blockers and signoff, see [release handoff](RELEASE_APPROVAL.md), [physical evidence kit](FIELD_ACCEPTANCE.md) and [native host guidance](NATIVE_SCHEDULERS.md).
