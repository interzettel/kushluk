# Archive compatibility preflight — structural, read-only

Kushluk development archives can contain private calendar entries, sources and newsletter/media records. A release must not silently rewrite or print an old archive after a schema change. The M1 preflight is deliberately **non-mutating**; it never migrates, loads source providers, validates CUPS/SMTP, or approves resend.

## Run privately

```bash
kushluk archive-check --archive-root /private/your-kushluk-archive --limit 100
```

The command emits **aggregate counts only** and keeps private edition IDs, absolute paths, dates, location names and story text out of stdout. It inspects at most 100 directories by default (up to 1,000 explicitly), and returns a `truncated` marker when more exist; this should not be treated as a complete scan. It refuses a symlink archive root, symlink edition directory, symlink metadata file, JSON over 2 MiB and invalid references.

### Explicit interpretation

| Category | Meaning | Production impact |
| --- | --- | --- |
| `readable_v2_metadata` | Current schema-v2 metadata contains matching ID/date, ordered four page kinds/numbers, valid practical/story references | **Metadata structurally readable only** — does not inspect PDF, permissions or delivery receipt |
| `legacy_v1_requires_migration` | Historic schema 1 was found | **No automatic conversion**, preserve original for explicit review |
| `unsupported_schema` | Different numeric version (including future) | Do not guess or rewrite content |
| `invalid_* / unsafe_* / oversized_*` | Bad identity/reference/JSON, symlink or size issue | Quarantine from import/delivery; review privately |
| `missing_metadata` | An edition directory lacks metadata | Not accepted as a valid archived publication |

A v2 metadata check **does not** prove a compatible PDF, e-reader EPUB, correct print imposition, trustworthy source rights or an authorized resend. The separate `deliver-archived` still performs its own independent preflight and requires explicit possible-duplicate acknowledgment. The compatibility command returns `migration_performed: false` and `delivery_approved: false` in every case.

## Migration remains an explicit engineering decision

The first Stage 1 prototype used different page architecture before the canonical four-page schema-v2 edition. No general trustworthy mapping for the earlier schema's missing canonical pages and references has been approved. Therefore no blind v1→v2 up-conversion is implemented. A future migration must describe source schemas, archive directory/version backups, round-trip/rollback behavior, paper-identity checks, deterministic matching, consent when private media changes, and its own regression tests. Older archives remain readable as **files** for their owners, but are **not** promised equivalent reprintability.

Fixtures in `tests/test_archive_compat.py` cover v1, v2, future, bad/missing/oversized/symlink metadata, truncated scans and no mutation. They contain only original synthetic text, not reader archives. Separate real-user archive acceptance belongs to the release gate.
