"""Offline, rights-cleared local-image print proof; no acquisition or device delivery."""
from __future__ import annotations

from dataclasses import asdict
from datetime import date
import json
from pathlib import Path

from kushluk.media import import_local_media
from kushluk.models import Story
from kushluk.publication import build_publication
from kushluk.renderer import render_html, render_pdf
from kushluk.validation import validate_pdf


def make_proof(output_dir: Path) -> dict:
    from PIL import Image, ImageDraw

    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError("media_proof_output_not_empty")
    output_dir.mkdir(parents=True, exist_ok=True)
    store = output_dir / "private-local-media"
    evidence = {
        "schema_version": 1, "synthetic_fixture": True,
        "original_creator_permission": "owner-generated test geometry",
        "no_external_source_acquisition": True,
        "public_fixture_rights_scope": "shareable", "physical_verified": False,
        "variants": {},
    }
    samples = {
        "landscape-focal": ((1200, 800), "focal-crop", (0.72, 0.45)),
        "portrait-contain": ((900, 1300), "contain", (0.5, 0.5)),
        "square-focal": ((1100, 1100), "focal-crop", (0.18, 0.25)),
    }
    for name, (size, crop_policy, focus) in samples.items():
        original = output_dir / f"{name}-source.png"
        image = Image.new("RGB", size, "#eeebdf")
        draw = ImageDraw.Draw(image)
        w, h = size
        draw.rectangle((w // 12, h // 12, w // 3, h // 2), fill="#366d57")
        draw.ellipse((int(w * .65), int(h * .3),
                      int(w * .84), int(h * .65)), fill="#cc7066")
        image.save(original, format="PNG")
        media = import_local_media(
            original, store, license_id="own-work", permission_scope="shareable",
            approved_for_print=True, attribution="Kushluk original test artwork",
            alt_text="Forest and coral geometry on a light background",
            caption=f"Synthetic {name} print-fit proof",
            crop_policy=crop_policy, focal_x=focus[0], focal_y=focus[1],
        )
        edition = build_publication(
            target_date=date(2026, 10, 17), timezone="Europe/Berlin",
            location_name="Synthetic city", practical=[],
            stories=[Story("one", "Controlled local image without external rights",
                           "A generated, owner-licensed raster with a safe caption and source.",
                           "Original synthetic fixture", image_asset_id=media.asset_id)],
            archetype="balanced", media_store=store,
        )
        edition.generated_at = "2026-10-17T07:00:00+02:00"
        html = render_html(edition, output_dir / f"{name}.html", media_store=store)
        pdf = render_pdf(html, output_dir / f"{name}.pdf")
        check = validate_pdf(pdf, expected_pages=4)
        if not check.ok or not edition.media:
            raise RuntimeError("media_proof_print_ineligible")
        evidence["variants"][name] = {
            "asset_id": media.asset_id, "pdf": pdf.name, "html": html.name,
            "page_count": check.page_count, "rights_scope": media.permission_scope,
            "license_id": media.license_id,
            "placement": asdict(edition.media[0]),
            "passed": check.ok,
        }
    (output_dir / "media-proof.json").write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8",
    )
    return evidence


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("output/media-proof"))
    args = parser.parse_args()
    data = make_proof(args.output_dir)
    print(json.dumps({"status": "passed", "variants": len(data["variants"]),
                      "physical_verified": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
