"""No-network media rights, provenance, geometry and fallback regression tests."""
from __future__ import annotations

from dataclasses import replace
from datetime import date
from io import BytesIO
import json
from pathlib import Path
import re

from PIL import Image, ImageDraw
import pytest

from kushluk.archive import archive_publication
from kushluk.media import (
    MIN_DPI, MediaError, import_local_media, prepare_placement, read_asset, render_bytes,
)
from kushluk.models import Story
from kushluk.publication import build_publication
from kushluk.renderer import render_html


def fixture(path: Path, *, size=(1200, 720), form="PNG", focal=True) -> Path:
    image = Image.new("RGB", size, "#eceddf")
    draw = ImageDraw.Draw(image)
    if focal:
        w, h = size
        draw.ellipse((int(w * .65), int(h * .27),
                      int(w * .80), int(h * .55)), fill="#c94b44")
        draw.rectangle((0, 0, w // 5, h // 4), fill="#27735a")
    image.save(path, format=form)
    return path


def imported(tmp_path, *, dimensions=(1200, 720), scope="shareable",
             crop="focal-crop", focal_x=.72, focal_y=.42):
    src = fixture(tmp_path / "fixture.png", size=dimensions)
    store = tmp_path / "store"
    item = import_local_media(
        src, store, license_id="own-work", attribution="Original synthetic artwork",
        alt_text="Simple flat-color geometry with an offset coral focus",
        caption="Locally generated layout fixture", permission_scope=scope,
        approved_for_print=True, focal_x=focal_x, focal_y=focal_y, crop_policy=crop,
    )
    return store, item


def paper(store: Path | None, asset_id: str | None, *,
          archetype="balanced", caption=None):
    return build_publication(
        target_date=date(2026, 10, 17), timezone="Europe/Berlin",
        location_name="Test city", practical=[],
        stories=[Story(
            "fixture-1", "Synthetic rights-aware image",
            "An exclusively synthetic local print fixture; this is not real journalism.",
            "Fixture publisher", image_asset_id=asset_id,
            image_caption=caption,
        )],
        archetype=archetype, media_store=store,
    )


@pytest.mark.parametrize("size", [
    (1200, 720), (720, 1200), (1100, 1100), (2400, 800),
])
def test_landscape_portrait_square_and_awkward_ratio_crop(tmp_path, size):
    store, asset = imported(tmp_path, dimensions=size)
    crop = prepare_placement(store, asset.asset_id, "fixture-1")
    assert crop.effective_dpi >= MIN_DPI
    assert crop.width_mm == 66 and crop.height_mm == 33
    assert crop.license_id == "own-work"
    assert crop.permission_scope == "shareable"
    assert crop.crop_box[2] <= size[0]
    assert crop.crop_box[3] <= size[1]
    assert crop.crop_box[0] >= 0 and crop.crop_box[1] >= 0
    body = render_bytes(store, crop)
    assert Image.open(BytesIO(body)).format == "PNG"
    assert prepare_placement(store, asset.asset_id, "fixture-1") == crop


def test_focal_point_changes_crop_but_does_not_invent_new_permission(tmp_path):
    store, item = imported(tmp_path)
    first = prepare_placement(store, item.asset_id, "s")
    other_src = fixture(tmp_path / "other.png")
    second_asset = import_local_media(
        other_src, tmp_path / "another-store", license_id="own-work",
        attribution="Original synthetic artwork", alt_text="Offset test object",
        caption="Different focus", permission_scope="private_print",
        approved_for_print=True, focal_x=.05, focal_y=.90,
    )
    other = prepare_placement(tmp_path / "another-store", second_asset.asset_id, "s")
    assert first.crop_box != other.crop_box
    assert first.crop_sha256 != other.crop_sha256


def test_contain_letterboxes_instead_of_distorting_portrait(tmp_path):
    store, asset = imported(tmp_path, dimensions=(900, 1500), crop="contain")
    crop = prepare_placement(store, asset.asset_id, "s")
    data = render_bytes(store, crop)
    with Image.open(BytesIO(data)) as im:
        assert im.width == round(66 / 25.4 * 180)
        assert im.height == round(33 / 25.4 * 180)
        assert im.getpixel((0, 0)) == (255, 255, 255)
        assert im.getpixel((im.width // 2, im.height // 2)) != (255, 255, 255)


def test_tiny_asset_is_text_only_and_records_reason(tmp_path):
    store, asset = imported(tmp_path, dimensions=(65, 43))
    with pytest.raises(MediaError, match="image_below_print_dpi"):
        prepare_placement(store, asset.asset_id, "s")
    pub = paper(store, asset.asset_id)
    assert pub.media == []
    assert pub.stories[0].image_asset_id is None
    assert any(d.action == "remove_image" for d in pub.composition_decisions)
    html = render_html(pub, tmp_path / "tiny.html").read_text()
    assert "data:image/png" not in html
    assert "Synthetic rights-aware image" in html


def test_rights_checked_pdf_html_is_self_contained_and_archive_copy_is_identical(tmp_path):
    store, asset = imported(tmp_path)
    pub = paper(store, asset.asset_id)
    assert len(pub.media) == 1
    assert pub.media[0].slot == "lead-66x33"
    assert pub.pages[0].blocks[0].budget.image_slots == 1
    html = render_html(pub, tmp_path / "print.html", media_store=store).read_text()
    assert 'src="data:image/png;base64,' in html
    assert 'alt="Simple flat-color geometry' in html
    assert "Original synthetic artwork" in html
    assert "own-work" in html
    assert not re.search(r"<img[^>]+(?:https?://|file://)", html)
    archive = archive_publication(
        pub, tmp_path / "archive", html_path=tmp_path / "print.html",
        media_store=store,
    )
    exported = archive / "media" / (pub.media[0].crop_sha256 + ".png")
    assert exported.read_bytes() == render_bytes(store, pub.media[0])
    assert (archive / "edition.html").read_text() == html
    meta = json.loads((archive / "metadata.json").read_text())
    assert meta["media"][0]["permission_scope"] == "shareable"
    assert meta["media"][0]["effective_dpi"] >= MIN_DPI


@pytest.mark.parametrize("scope", ["shareable", "private_print"])
def test_approved_scope_is_recorded_not_guessed(tmp_path, scope):
    store, item = imported(tmp_path, scope=scope)
    assert read_asset(store, item.asset_id)[0].permission_scope == scope
    assert paper(store, item.asset_id).media[0].permission_scope == scope


@pytest.mark.parametrize("bad", [
    {"approved_for_print": False},
    {"license_id": "unknown"},
    {"license_id": "CC-BY-NC-4.0"},
    {"permission_scope": "wrong"},
    {"permission_scope": "shareable", "license_id": "explicit-permission"},
    {"source_url": "https://host.test/images?private=secret"},
    {"source_url": "http://host.test/images"},
    {"source_url": "https://user:password@host.test/img"},
    {"crop_policy": "unsupported"},
    {"focal_x": 1.3},
])
def test_no_rights_grant_or_unsafe_provenance_is_rejected(tmp_path, bad):
    src = fixture(tmp_path / "image.png")
    args = dict(
        license_id="own-work", attribution="Synthetic", alt_text="Shapes",
        caption="Synthetic fixture", permission_scope="shareable",
        approved_for_print=True,
    )
    args.update(bad)
    with pytest.raises(MediaError):
        import_local_media(src, tmp_path / "store", **args)
    assert not (tmp_path / "store" / "records").exists()


def test_duplicate_or_tampered_asset_falls_back_without_new_approval(tmp_path):
    store, asset = imported(tmp_path)
    src = tmp_path / "fixture.png"
    with pytest.raises(MediaError, match="media_already_exists"):
        import_local_media(
            src, store, license_id="own-work", attribution="Fake reapproval",
            alt_text="Fake", caption="", permission_scope="shareable",
            approved_for_print=True,
        )
    meta = store / "records" / f"{asset.asset_id}.json"
    payload = json.loads(meta.read_text())
    payload["license_id"] = "unknown"
    meta.write_text(json.dumps(payload))
    pub = paper(store, asset.asset_id)
    assert pub.media == [] and pub.stories[0].image_asset_id is None


def test_changed_image_pixels_fail_closed_at_render(tmp_path):
    store, item = imported(tmp_path)
    pub = paper(store, item.asset_id)
    file = store / "originals" / f"{item.asset_id}.png"
    file.write_bytes(b"tampered file")
    html = render_html(pub, tmp_path / "tampered.html", media_store=store).read_text()
    assert "data:image/png;base64," not in html
    assert "Synthetic rights-aware image" in html


def test_missing_symlinked_svg_and_invalid_image_are_never_imported(tmp_path):
    store = tmp_path / "store"
    src = fixture(tmp_path / "image.png")
    sym = tmp_path / "alias.png"
    sym.symlink_to(src)
    for bad in (sym, tmp_path / "missing.png"):
        with pytest.raises(MediaError):
            import_local_media(
                bad, store, license_id="own-work", attribution="Self", alt_text="Shapes",
                caption="", permission_scope="private_print", approved_for_print=True,
            )
    svg = tmp_path / "image.svg"
    svg.write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
    with pytest.raises(MediaError, match="invalid_image_content"):
        import_local_media(svg, store, license_id="own-work", attribution="Self",
                           alt_text="Shapes", caption="",
                           permission_scope="private_print", approved_for_print=True)


def test_malformed_or_missing_id_remains_text_only(tmp_path):
    pub = paper(tmp_path / "empty", "not-a-normalized-id")
    assert pub.media == []
    assert pub.stories[0].image_asset_id is None


def test_no_images_allowed_on_news_heavy_multi_lead_even_if_grant_exists(tmp_path):
    store, asset = imported(tmp_path)
    pub = paper(store, asset.asset_id, archetype="news-heavy")
    assert pub.media == []
    assert all(b.budget.image_slots == 0 for b in pub.pages[0].blocks)
    assert pub.stories[0].image_asset_id is None


def test_media_cli_is_explicit_local_and_never_accepts_unapproved_import(
    tmp_path, monkeypatch, capsys,
):
    from kushluk.cli import main
    src = fixture(tmp_path / "input.png")
    cmd = [
        "media-import", "--file", str(src), "--store", str(tmp_path / "store"),
        "--license-id", "CC0-1.0", "--credit", "Local creator",
        "--alt", "Flat colored geometric fixture", "--caption", "Test graphic",
        "--scope", "private_print",
    ]
    assert main(cmd) == 2
    assert json.loads(capsys.readouterr().out)["error"] == "explicit_media_permission_required"
    assert main(cmd + ["--approve-print"]) == 0
    info = json.loads(capsys.readouterr().out)
    assert info["scope"] == "private_print"
    assert main(["media-info", "--store", str(tmp_path / "store"),
                 "--asset-id", info["asset_id"]]) == 0
    assert json.loads(capsys.readouterr().out)["asset_id"] == info["asset_id"]


@pytest.mark.parametrize("size", [(1200, 720), (900, 1600), (1100, 1100)])
def test_pdf_proof_with_approved_media_is_still_four_a4_pages(tmp_path, size):
    pytest.importorskip("weasyprint")
    pytest.importorskip("pypdf")
    from kushluk.renderer import render_pdf
    from kushluk.validation import validate_pdf

    store, asset = imported(tmp_path, dimensions=size)
    pub = paper(store, asset.asset_id)
    html_path = render_html(pub, tmp_path / "paper.html", media_store=store)
    pdf = render_pdf(html_path, tmp_path / "paper.pdf")
    validation = validate_pdf(pdf, expected_pages=4)
    assert validation.ok, validation.errors
    assert pdf.stat().st_size > 1000
