"""Owner-imported local image media: explicit permission, reproducible print crops.

This module never downloads URLs, executes image metadata, or trusts hotlinks.
Pillow is optional except when the owner enables local media operations.
"""
from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
from io import BytesIO
import json
import os
from pathlib import Path
import tempfile
import re
from urllib.parse import urlsplit

from kushluk.models import MediaAsset, MediaPlacement

MAX_FILE_BYTES = 8_388_608
MAX_PIXELS = 24_000_000
SLOT_WIDTH_MM, SLOT_HEIGHT_MM = 66, 33
MIN_DPI = 180
ALLOWED_LICENSES = frozenset({"CC0-1.0", "CC-BY-4.0", "own-work", "explicit-permission"})
ALLOWED_POLICIES = frozenset({"focal-crop", "contain"})
ASSET_ID = re.compile(r"^[0-9a-f]{64}$")


class MediaError(ValueError):
    """Reason-coded public failure: do not embed private source paths or URLs."""


def _pillow():
    try:
        from PIL import Image, ImageOps
    except ImportError as exc:
        raise MediaError("pillow_dependency_required") from exc
    Image.MAX_IMAGE_PIXELS = MAX_PIXELS
    return Image, ImageOps


def _safe_text(value: str, *, maximum: int, required: bool = True) -> str:
    if not isinstance(value, str):
        raise MediaError("invalid_media_text")
    clean = " ".join(value.split())
    if (required and not clean) or len(clean) > maximum or any(
        ord(ch) < 32 for ch in clean
    ):
        raise MediaError("invalid_media_text")
    return clean


def _source_url(value: str | None) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or len(value) > 500:
        raise MediaError("invalid_provenance_url")
    parsed = urlsplit(value)
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username
            or parsed.password or parsed.query or parsed.fragment
            or parsed.port not in (None, 443)):
        raise MediaError("invalid_provenance_url")
    return value


def _file(root: Path, name: str) -> Path:
    if not ASSET_ID.fullmatch(name):
        raise MediaError("invalid_asset_id")
    if root.is_symlink():
        raise MediaError("invalid_media_store")
    return root / name


def _read_file(path: Path, maximum: int) -> bytes:
    try:
        if path.is_symlink() or not path.is_file() or path.stat().st_size > maximum:
            raise MediaError("unsafe_or_oversized_media_file")
        return path.read_bytes()
    except OSError as exc:
        raise MediaError("media_file_unavailable") from exc


def _store_file(path: Path, body: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if path.is_symlink():
        raise MediaError("unsafe_media_path")
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise MediaError("media_already_exists") from exc
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(body)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def import_local_media(
    input_file: Path, store: Path, *,
    license_id: str, attribution: str, alt_text: str, caption: str,
    permission_scope: str, approved_for_print: bool,
    source_url: str | None = None, focal_x: float = 0.5, focal_y: float = 0.5,
    crop_policy: str = "focal-crop",
) -> MediaAsset:
    """No remote acquisition. Owner must explicitly assert grant and print permission."""
    if approved_for_print is not True or permission_scope not in ("private_print", "shareable"):
        raise MediaError("explicit_media_permission_required")
    if license_id not in ALLOWED_LICENSES:
        raise MediaError("unknown_or_disallowed_media_license")
    if permission_scope == "shareable" and license_id == "explicit-permission":
        raise MediaError("shareable_grant_not_verified")
    if crop_policy not in ALLOWED_POLICIES or not (0 <= focal_x <= 1 and 0 <= focal_y <= 1):
        raise MediaError("invalid_media_crop")
    attribution = _safe_text(attribution, maximum=130)
    alt_text = _safe_text(alt_text, maximum=170)
    caption = _safe_text(caption, maximum=105, required=False)
    source_url = _source_url(source_url)
    Image, ImageOps = _pillow()
    original = _read_file(input_file, MAX_FILE_BYTES)
    try:
        with Image.open(BytesIO(original)) as image:
            if image.format not in ("JPEG", "PNG") or image.width * image.height > MAX_PIXELS:
                raise MediaError("unsupported_media_format_or_dimensions")
            image.load()
            fixed = ImageOps.exif_transpose(image).convert("RGB")
        output = BytesIO()
        fixed.save(output, format="PNG", optimize=False)
    except (OSError, ValueError, Image.DecompressionBombError) as exc:
        raise MediaError("invalid_image_content") from exc
    body = output.getvalue()
    if len(body) > MAX_FILE_BYTES:
        raise MediaError("normalized_media_oversized")
    digest = sha256(body).hexdigest()
    meta_path = _file(store / "records", digest).with_suffix(".json")
    original_path = _file(store / "originals", digest).with_suffix(".png")
    if meta_path.exists() or original_path.exists():
        raise MediaError("media_already_exists")
    asset = MediaAsset(
        schema_version=1, asset_id=digest, sha256=digest, source_kind="local_file",
        source_url=source_url, license_id=license_id, permission_scope=permission_scope,
        approved_for_print=True, attribution=attribution, alt_text=alt_text,
        caption=caption, width_px=fixed.width, height_px=fixed.height,
        focal_x=focal_x, focal_y=focal_y, crop_policy=crop_policy,
    )
    _store_file(original_path, body)
    try:
        _store_file(meta_path, (json.dumps(asdict(asset), sort_keys=True) + "\n").encode())
    except BaseException:
        original_path.unlink(missing_ok=True)
        raise
    return asset


def read_asset(store: Path, asset_id: str) -> tuple[MediaAsset, bytes]:
    """Fail closed on renamed/tampered/corrupt or nonapproved local records."""
    meta = _file(store / "records", asset_id).with_suffix(".json")
    raw = _read_file(meta, 8192)
    try:
        info = json.loads(raw)
        if set(info) != set(MediaAsset.__dataclass_fields__):
            raise ValueError("fields mismatch")
        asset = MediaAsset(**info)
        if (asset.schema_version != 1 or asset.asset_id != asset_id
                or asset.sha256 != asset_id or asset.approved_for_print is not True
                or asset.permission_scope not in ("shareable", "private_print")
                or asset.license_id not in ALLOWED_LICENSES
                or (asset.permission_scope == "shareable"
                    and asset.license_id == "explicit-permission")
                or asset.crop_policy not in ALLOWED_POLICIES
                or not (0 <= asset.focal_x <= 1 and 0 <= asset.focal_y <= 1)):
            raise ValueError("unapproved record")
        _safe_text(asset.attribution, maximum=130)
        _safe_text(asset.alt_text, maximum=170)
        _safe_text(asset.caption, maximum=105, required=False)
        _source_url(asset.source_url)
    except (ValueError, TypeError, KeyError) as exc:
        raise MediaError("invalid_media_record") from exc
    body = _read_file(_file(store / "originals", asset_id).with_suffix(".png"), MAX_FILE_BYTES)
    if sha256(body).hexdigest() != asset.sha256:
        raise MediaError("image_checksum_mismatch")
    return asset, body


def prepare_placement(store: Path, asset_id: str, story_id: str) -> MediaPlacement:
    """Deterministic focal crop/contain + effective print DPI, or text-only fallback."""
    asset, body = read_asset(store, asset_id)
    Image, ImageOps = _pillow()
    target_w = round(SLOT_WIDTH_MM / 25.4 * MIN_DPI)
    target_h = round(SLOT_HEIGHT_MM / 25.4 * MIN_DPI)
    with Image.open(BytesIO(body)) as original:
        image = original.convert("RGB")
    if asset.crop_policy == "focal-crop":
        ratio = SLOT_WIDTH_MM / SLOT_HEIGHT_MM
        width, height = image.size
        crop_w = min(width, int(height * ratio))
        crop_h = min(height, int(width / ratio))
        left = max(0, min(width - crop_w, round(asset.focal_x * width - crop_w / 2)))
        top = max(0, min(height - crop_h, round(asset.focal_y * height - crop_h / 2)))
        bounds = (left, top, left + crop_w, top + crop_h)
        cropped = image.crop(bounds)
        dpi = min(crop_w * 25.4 / SLOT_WIDTH_MM, crop_h * 25.4 / SLOT_HEIGHT_MM)
    else:
        bounds = (0, 0, image.width, image.height)
        # White letterboxing preserves the entire source, no stretching or focal cut.
        scale = min(image.width / target_w, image.height / target_h)
        dpi = scale * MIN_DPI
        if dpi < MIN_DPI:
            raise MediaError("image_below_print_dpi")
        contained = ImageOps.contain(image, (target_w, target_h))
        cropped = Image.new("RGB", (target_w, target_h), "#ffffff")
        cropped.paste(contained, (
            (target_w - contained.width) // 2,
            (target_h - contained.height) // 2,
        ))
    if dpi < MIN_DPI or cropped.width < target_w or cropped.height < target_h:
        # For contain, compare intrinsic pixel density in each slot dimension.
        raise MediaError("image_below_print_dpi")
    output = BytesIO()
    cropped.save(output, format="PNG", optimize=False)
    data = output.getvalue()
    digest = sha256(data).hexdigest()
    return MediaPlacement(
        story_id=story_id, asset_id=asset.asset_id, slot="lead-66x33",
        crop_sha256=digest, crop_box=bounds, crop_policy=asset.crop_policy,
        width_mm=SLOT_WIDTH_MM, height_mm=SLOT_HEIGHT_MM,
        effective_dpi=round(dpi, 1), license_id=asset.license_id,
        permission_scope=asset.permission_scope, attribution=asset.attribution,
        alt_text=asset.alt_text, caption=asset.caption,
    )


def render_bytes(store: Path, placement: MediaPlacement) -> bytes:
    """Regenerate pixels from immutable approved original; never trust a file URI."""
    asset, _ = read_asset(store, placement.asset_id)
    if (asset.license_id != placement.license_id or
            asset.permission_scope != placement.permission_scope or
            asset.attribution != placement.attribution):
        raise MediaError("media_grant_changed")
    proof = prepare_placement(store, placement.asset_id, placement.story_id)
    if proof != placement:
        raise MediaError("media_placement_changed")
    # prepare_placement validates but does not write to disk; crop deterministically.
    _, original = read_asset(store, placement.asset_id)
    Image, ImageOps = _pillow()
    with Image.open(BytesIO(original)) as src:
        image = src.convert("RGB")
        if placement.crop_policy == "focal-crop":
            image = image.crop(placement.crop_box)
        else:
            target_w = round(SLOT_WIDTH_MM / 25.4 * MIN_DPI)
            target_h = round(SLOT_HEIGHT_MM / 25.4 * MIN_DPI)
            fitted = ImageOps.contain(image, (target_w, target_h))
            letterbox = Image.new("RGB", (target_w, target_h), "#ffffff")
            letterbox.paste(fitted, (
                (target_w - fitted.width) // 2,
                (target_h - fitted.height) // 2,
            ))
            image = letterbox
        output = BytesIO()
        image.save(output, format="PNG", optimize=False)
    data = output.getvalue()
    if sha256(data).hexdigest() != placement.crop_sha256:
        raise MediaError("media_crop_checksum_mismatch")
    return data


STORY_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$")


def read_media_assignments(store: Path) -> dict[str, str]:
    """No source guessing: only versioned, explicitly mapped owner choices."""
    path = store / "bindings.json"
    if not path.exists() and not path.is_symlink():
        return {}
    try:
        payload = json.loads(_read_file(path, 65536))
        if set(payload) != {"schema_version", "bindings"} or payload["schema_version"] != 1:
            return {}
        bindings = payload["bindings"]
        if (not isinstance(bindings, dict) or len(bindings) > 500
                or any(not isinstance(k, str) or not STORY_ID.fullmatch(k)
                       or not isinstance(v, str) or not ASSET_ID.fullmatch(v)
                       for k, v in bindings.items())):
            return {}
        return bindings
    except (ValueError, UnicodeError, TypeError):
        return {}


def assign_media(store: Path, *, story_id: str, asset_id: str) -> None:
    """Owner explicitly pins a reviewed asset to a stable editorial story ID."""
    if not isinstance(story_id, str) or not STORY_ID.fullmatch(story_id):
        raise MediaError("invalid_story_id")
    # Never bind an image that already fails approved rights, checksum or print DPI.
    prepare_placement(store, asset_id, story_id)
    if store.is_symlink():
        raise MediaError("invalid_media_store")
    path = store / "bindings.json"
    if path.is_symlink():
        raise MediaError("unsafe_bindings_file")
    bindings = read_media_assignments(store)
    if path.exists() and not bindings:
        raise MediaError("invalid_bindings_file")
    bindings[story_id] = asset_id
    content = (json.dumps({"schema_version": 1, "bindings": bindings},
                          sort_keys=True) + "\n").encode()
    store.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, filename = tempfile.mkstemp(prefix=".bindings-", suffix=".tmp", dir=store)
    try:
        with os.fdopen(fd, "wb") as stream:
            os.fchmod(stream.fileno(), 0o600)
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(filename, path)
    finally:
        Path(filename).unlink(missing_ok=True)


def remove_local_media(store: Path, asset_id: str) -> None:
    """Remove a local approval and origin. Already archived editions are separate."""
    _file(store / "records", asset_id)
    if store.is_symlink():
        raise MediaError("invalid_media_store")
    # Caller explicitly revokes locally; no remote fetch or archive rewrite.
    for path in (
        (store / "records" / asset_id).with_suffix(".json"),
        (store / "originals" / asset_id).with_suffix(".png"),
    ):
        if path.is_symlink():
            raise MediaError("unsafe_media_path")
    meta = (store / "records" / asset_id).with_suffix(".json")
    original = (store / "originals" / asset_id).with_suffix(".png")
    if not meta.exists() and not original.exists():
        raise MediaError("media_not_found")
    meta.unlink(missing_ok=True)
    original.unlink(missing_ok=True)
    path = store / "bindings.json"
    if path.exists() and not path.is_symlink():
        bindings = read_media_assignments(store)
        if bindings:
            remaining = {k: v for k, v in bindings.items() if v != asset_id}
            content = (json.dumps({"schema_version": 1, "bindings": remaining},
                                  sort_keys=True) + "\n").encode()
            fd, filename = tempfile.mkstemp(prefix=".bindings-", suffix=".tmp", dir=store)
            try:
                with os.fdopen(fd, "wb") as stream:
                    os.fchmod(stream.fileno(), 0o600)
                    stream.write(content)
                os.replace(filename, path)
            finally:
                Path(filename).unlink(missing_ok=True)
