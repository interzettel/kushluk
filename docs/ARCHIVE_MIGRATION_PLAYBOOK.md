# Historical archive preservation and migration decision playbook

**Owner:** [#54](https://github.com/interzettel/kushluk/issues/54), release gates G1/G5. This is a **non-mutating decision specification**, not a migration implementation or permission to resend legacy editions.

## Why v1 is quarantined

The current four-page edition schema is **v2**. Earlier schema-v1 records may lack canonical per-page ordering, practical/story references and the exact verified PDF that the reprint pipeline requires. Guessing these from another schema would invent content, publication identity or provenance. Therefore `kushluk archive-check` identifies `legacy_v1_requires_migration` and **does not** alter a file. The existing manual `deliver-archived` accepts only structurally validated v2 archives. The correct behavior is an explicit refusal, not an automatically manufactured v2 document.

## Safe local owner procedure

1. On the owner machine, stop the local scheduled service before making any changes. Confirm no `kushluk run`, printing or SMTP work is active, and retain the original data on the original host.
2. Make a separate **private, offline, full archive backup or filesystem snapshot** using a trusted local backup tool. Include the file structure, permissions, edition PDF/HTML, run/delivery receipts and media; verify the backup restores into a **new directory**, never into the live archive. Do not publish or upload the backup.
3. Run `kushluk archive-check --archive-root /private/archive --limit 1000` and record the **aggregate counts only**. If truncated, repeat with owner-approved bounded local inventory rather than assuming no other editions exist.
4. If v1 or invalid categories appear, leave them untouched. Keep a separate copy for review; no automatic reflow or new print request. The existing v1 files are readable by their owner as files, not promised reprintable publications.
5. Before **any future migration implementation**, approve a real v1 sample inventory (private), target schema mapping, content/provenance invariants, migration output suffixes, backup verification and rollback drill, negative security cases, copy/serialization parity and human opt-in. An unmappable legacy page must remain legacy, not be silently rewritten.
6. Test a hypothetical migrator only against **synthetic fixtures in disposable directories**, then separately review rights-cleared historical samples offline. Require fresh receipt IDs and the existing explicit acknowledgement before printing a migrated edition; no automatic resend.

## Invariants for any future converter

- Create-only output under a new versioned location; no in-place mutation, symlink traversal or overwrite.
- Stable original edition ID, date, timestamps, credits, source/provenance and checksums remain traceable; do not silently synthesize missing stories or image rights.
- Validate four logical A4 pages and any imposed A3 PDF separately. A schema-v2 JSON label **does not** itself prove a valid printable PDF.
- Detect duplicates and handle interruption/restart transactionally; tests require unchanged original bytes after failures and after rollback.
- Keep private paths/content out of stdout, support logs and CI artifacts. No cloud sync, remote operator or paid model is part of the migration.
- Independently verify old and new artifacts before a new human-authorized delivery; **v1 can legitimately stay unsupported indefinitely**.

See [archive compatibility inspector](ARCHIVE_COMPATIBILITY.md), [manual recovery contract](OPERATIONS_V1.md), and [release approval](RELEASE_APPROVAL.md). All G1–G8 acceptance states remain unchanged.
