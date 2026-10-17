# Rights-aware local image pipeline — first production-safe tranche (#50)

**State:** local-first, explicit owner authorization, typed print-image eligibility and deterministic text-only fallback. No remote image acquisition or inferred redistribution rights. See [#50](https://github.com/interzettel/kushluk/issues/50), [#4](https://github.com/interzettel/kushluk/issues/4) and [#21](https://github.com/interzettel/kushluk/issues/21).

## Legal boundary: a URL is not a grant

An RSS enclosure, publisher image, search result, cached screenshot or publicly accessible URL does **not** give Kushluk permission to download, reproduce, print, modify or distribute it. Image candidates with unknown/disputed terms remain text-only. A private personal edition is **not automatically exempt** from copyright or privacy rules; local private printing and redistribution/publication have different legal and provider-contract risks.

Kushluk does not independently certify ownership, copyright status, territorial restrictions, moral rights, personality releases, watermark-free status, or rights to modify a crop. The owner must review the actual license/permission and grant a **specific local approval**. `private_print` approval never turns into `shareable` automatically, and it must not be bundled in any public demo, test fixture, sample issue or redistributed PDF. For a public sample, use creator-owned synthetic imagery with written permission (or otherwise independently rights-cleared source) and a separately reviewed `shareable` grant. A `CC0-1.0`, `CC-BY-4.0`, `own-work` or `explicit-permission` label is an assertion to review, **not** a legal verification service. Explicit-permission grants cannot be marked shareable by the first tranche; that needs separately recorded redistribution evidence. Provider-level derivative and attribution conditions still require source-specific review.

## Import an approved local image

The system never requests an image over HTTP. The operator must first lawfully obtain a **local** PNG or JPEG (or create original artwork). All commands operate locally with no email, printer or third-party API:

```bash
kushluk media-import \
  --file /private/owner-cleared/photo.png \
  --store /private/kushluk-media \
  --license-id own-work --scope private_print --approve-print \
  --credit "Original author" \
  --alt "Clear description of the image" \
  --caption "A specific factual caption" \
  --focal-x 0.65 --focal-y 0.48 --crop-policy focal-crop
```

The response includes a 64-hex content-derived asset ID. `media-info --store ... --asset-id HEX` reads the local record. **No `--approve-print`, no import**. Use `--scope shareable` only when actual rights cover redistribution; never make a public proof using a private-print asset.

Import normalizes to RGB PNG (strips incidental EXIF/private metadata), computes a SHA-256 digest, stores private 0600 bytes in `originals/HEX.png` and a versioned `records/HEX.json`. The record includes source kind, optional restricted HTTPS provenance URL (no credentials/query string), checksum, dimensions, attribution, caption, alt text, focal coordinates, crop policy, license and scope. New file creation is exclusive and duplicate normalized images are rejected. SVG, remote URLs, symlinks, missing files, bad image formats and files above 8 MiB/24 million pixels do not enter the store.

## Explicit story attachment

Import **alone** never adds images to newspapers. Find the target editorial story's stable `id` in a local edition's `metadata.json`. Then intentionally pin the imported asset to that exact ID:

```bash
kushluk media-assign --store /private/kushluk-media \
  --story-id LOCAL_STORY_ID --asset-id HEX_FROM_IMPORT
```

The operation validates the rights record, image checksum and proposed 66 × 33 mm crop at a minimum **180 effective DPI** before writing private `bindings.json`. The production pipeline only reads bindings when `KUSHLUK_MEDIA_DIR=/private/kushluk-media` is explicitly set in the owner environment. It never uses RSS image URLs to infer permissions. Story ranking, source attribution and archive identity do not depend on images. Pinned media not eligible for a chosen archetype remains text-only with an explicit `remove_image` composition decision.

### Deterministic roles, crops and fallbacks

The first print-certified role is `lead-66x33` (66 × 33 mm, 2:1), at most one eligible lead in **balanced** or **practical-heavy** compositions. Multi-lead news-heavy covers, practical blocks and brief cards remain text-only until their separate geometry proof exists. Crops are computed from normalized image pixels and bounded `focal_x/y` in [0,1]; `contain` uses a white letterbox rather than stretching. Unsupported crops and low effective DPI fall back to text. There is no AI/guesswork that invents a missing image, no external hotlink and no dynamic crop service.

Print HTML embeds the approved raster as an inline PNG data URI with attribution, caption, license label and alt text. Rendering rechecks grant metadata and content SHA-256, never loads source URLs. An image missing after import, modified on disk or revoked does **not** reappear from the browser cache or cause a raw external fetch. The current text-only fallback preserves the original story's headline, deck and source citation.

**Not claimed:** automated watermark detection, protected-face screening, image editorial appropriateness, authoritative rights verification, and remote acquisition. Those remain IMG-02 / IMG-03 acceptance gaps.

## Reproducibility and deletion

The chosen `MediaPlacement` contains an asset ID, crop checksum and bounded crop box, print dimensions/DPI, alt/caption/attribution/license/scope—never an arbitrary local file URL. During archived edition creation, a verified selected crop is copied to `archive/EDITION_ID/media/CROP_SHA256.png`. Its HTML embeds precisely those pixels and its metadata records the placement. Archive artifacts may therefore remain reproducible if the owner later removes an original image approval.

To revoke **future** use:

```bash
kushluk media-remove --store /private/kushluk-media --asset-id HEX
```

This removes the local import, its record and pinned bindings, but **does not silently rewrite historical editions, their embedded PNGs, exported PDFs or distributed copies**. To fulfill a deletion or takedown obligation, the owner must separately remove applicable archive editions, shared/exported PDFs, backups and any distributed copies. The local tool cannot revoke files already sent to recipients. Archive and backups require owner-controlled retention/deletion policy. The app does not automatically upload personal photographic assets.

## Offline acceptance evidence

`tests/test_media_pipeline.py` uses generated geometry, not third-party copyrighted photographs. Cases include landscape, portrait, square, extreme wide, unusual focus, contain, 65×43-pixel tiny rejection, missing assets, symlink and SVG rejection, duplicate checksums, disallowed/unknown license, tampered metadata, corrupt bytes, reproducible crop and optional **four-page A4 PDF**. PDF tests run on both macOS architectures under CI. No real artist, media provider, printer or public-copyright determination is asserted.

### Outstanding gates

IMG-02 acquisition from a permitted source endpoint and IMG-03 comprehensive visible watermark/rights assessment are *not* implemented; IMG-09 software fixtures do not replace actual paper/legibility QA. Device acceptance and other G1–G8 release evidence remain **0/8**. Version stays `0.1.0`.
