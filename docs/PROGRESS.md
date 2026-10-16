# Kuşluk progress and evidence gates

**Snapshot reviewed:** 2026-10-16 · Sources: [WORK_LEDGER.md](WORK_LEDGER.md), [progress-manifest.json](progress-manifest.json)

> These numbers are NOT an overall percentage of product completion. Checked tasks count operational checklist marks only. Delivery gates are independently verified with linked evidence.

## Delivery evidence gates

**0 of 8 verified with evidence.** Unverified does not mean failed.

| Gate | State | Owner issues |
| --- | --- | --- |
| G1 — Four-page format | unverified | [#45](https://github.com/interzettel/kushluk/issues/45), [#21](https://github.com/interzettel/kushluk/issues/21) |
| G2 — Real A4/A3 delivery | unverified | [#46](https://github.com/interzettel/kushluk/issues/46), [#7](https://github.com/interzettel/kushluk/issues/7), [#13](https://github.com/interzettel/kushluk/issues/13) |
| G3 — Unattended automation | unverified | [#47](https://github.com/interzettel/kushluk/issues/47), [#17](https://github.com/interzettel/kushluk/issues/17), [#13](https://github.com/interzettel/kushluk/issues/13) |
| G4 — Sources and security | unverified | [#4](https://github.com/interzettel/kushluk/issues/4), [#16](https://github.com/interzettel/kushluk/issues/16), [#48](https://github.com/interzettel/kushluk/issues/48), [#49](https://github.com/interzettel/kushluk/issues/49) |
| G5 — User-owned portability | unverified | [#5](https://github.com/interzettel/kushluk/issues/5), [#15](https://github.com/interzettel/kushluk/issues/15), [#37](https://github.com/interzettel/kushluk/issues/37) |
| G6 — Public trust and legal copy | unverified | [#10](https://github.com/interzettel/kushluk/issues/10), [#34](https://github.com/interzettel/kushluk/issues/34) |
| G7 — Licensing and contribution governance | unverified | [#38](https://github.com/interzettel/kushluk/issues/38), [#54](https://github.com/interzettel/kushluk/issues/54) |
| G8 — Real reader trials | unverified | [#6](https://github.com/interzettel/kushluk/issues/6), [#13](https://github.com/interzettel/kushluk/issues/13) |

## Operational work ledger

**4 of 90 task checkboxes checked.** This measures task-record state, not overall readiness.

| Task group | Checked | Total |
| --- | ---: | ---: |
| DOC | 4 | 5 |
| FMT | 0 | 10 |
| AUT | 0 | 13 |
| SRC | 0 | 10 |
| IMG | 0 | 9 |
| LAY | 0 | 11 |
| DES-EXT | 0 | 5 |
| RES-NEWS | 0 | 3 |
| RES-AUTO | 0 | 2 |
| RES-IMG | 0 | 1 |
| ED | 0 | 6 |
| UX | 0 | 8 |
| TRIAL | 0 | 7 |
| **TOTAL** | **4** | **90** |

## Update protocol

1. Complete an owning issue's acceptance tests and attach reproducible evidence.
2. Update the relevant WORK_LEDGER.md checkbox only after evidence review.
3. Mark a gate verified only with HTTPS evidence and a verified_on ISO date in progress-manifest.json.
4. Run: python tools/project_health.py write
5. Run: python tools/project_health.py check (enforced by Project health CI).

The [master ledger #43](https://github.com/interzettel/kushluk/issues/43) holds the GitHub issue inventory. This offline report does not fetch live GitHub issue states. [Engineering foundation #54](https://github.com/interzettel/kushluk/issues/54) owns this reporting system.
