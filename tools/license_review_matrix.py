"""Create a bounded, reviewable Python/native/font licence evidence worksheet.

This does not decide licenses or bundle font files. No network, no legal
approval, no source paths in output. Inputs are existing CI inventories.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import re

PACKAGE = re.compile(r"[a-z0-9][a-z0-9._-]{0,119}\Z")
VERSION = re.compile(r"[A-Za-z0-9][A-Za-z0-9.!+_-]{0,119}\Z")
STATUS = frozenset({
    "license_expression_declared", "license_classifier_only",
    "legacy_license_field_only", "license_metadata_missing",
})
LIBRARIES = ("cairo", "fontconfig", "harfbuzz", "pango")
FONT_CATEGORIES = ("sans-serif", "serif", "monospace")


class ReviewMatrixError(ValueError):
    """The evidence is unsafe or does not match the expected inventory schema."""


def _read(path: Path, expected_kind: str) -> tuple[dict, str]:
    if path.is_symlink() or not path.is_file():
        raise ReviewMatrixError("invalid_inventory_file")
    try:
        if path.stat().st_size <= 0 or path.stat().st_size > 2 * 1024 * 1024:
            raise ReviewMatrixError("invalid_inventory_file_size")
        raw = path.read_bytes()
        data = json.loads(raw)
    except (OSError, UnicodeError, ValueError) as exc:
        raise ReviewMatrixError("invalid_inventory_json") from exc
    if (not isinstance(data, dict) or data.get("kind") != expected_kind
            or data.get("schema_version") != 1):
        raise ReviewMatrixError("invalid_inventory_schema")
    return data, sha256(raw).hexdigest()


def build_matrix(python: dict, *, native: dict | None = None,
                 python_sha256: str = "", native_sha256: str | None = None) -> dict:
    if (python.get("schema_version") != 1
            or python.get("kind") != "installed-python-environment-inventory"
            or not isinstance(python.get("installed_packages"), list)):
        raise ReviewMatrixError("invalid_python_inventory")
    packages = []
    names = set()
    for obj in python["installed_packages"]:
        if not isinstance(obj, dict):
            raise ReviewMatrixError("invalid_python_package")
        name, version, status = (
            obj.get("name"), obj.get("version"), obj.get("license_metadata_status"),
        )
        if (not isinstance(name, str) or not PACKAGE.fullmatch(name)
                or not isinstance(version, str) or not VERSION.fullmatch(version)
                or status not in STATUS or name in names):
            raise ReviewMatrixError("invalid_or_duplicate_python_package")
        names.add(name)
        # License text in an input snapshot is evidence of a *claim*, not
        # proof of actual terms or a redistribution grant.
        packages.append({
            "package": name, "version": version,
            "metadata_class": status,
            "requires_human_license_review": True,
            "license_review_state": "pending",
            "redistribution_rights_verified": False,
        })
    if "kushluk" not in names:
        raise ReviewMatrixError("missing_kushluk_installation")
    packages.sort(key=lambda x: (x["package"], x["version"]))
    if native is not None:
        if (not isinstance(native, dict) or native.get("schema_version") != 1
                or native.get("kind") != "native-print-dependency-observation"
                or not isinstance(native.get("native_library_versions"), dict)
                or not isinstance(native.get("font_family_matches"), dict)):
            raise ReviewMatrixError("invalid_native_inventory")
    libraries = []
    fonts = []
    for name in LIBRARIES:
        raw = (native or {}).get("native_library_versions", {}).get(name)
        # Record version only when it has the strict expected numerical shape;
        # never echo arbitrary environment / command error output.
        version = raw if isinstance(raw, str) and re.fullmatch(
            r"[0-9]+(?:\.[0-9]+){1,3}", raw
        ) else None
        libraries.append({
            "library": name, "observed_version": version,
            "needs_license_review": True, "review_state": "pending",
            "native_rights_verified": False,
        })
    for category in FONT_CATEGORIES:
        raw = (native or {}).get("font_family_matches", {}).get(category)
        fonts.append({
            "requested_family": category,
            "family_match_observed": bool(isinstance(raw, str) and raw),
            # Do NOT include actual font names or font-file locations;
            # classification alone cannot establish font rights.
            "license_review_state": "pending",
            "embedding_rights_verified": False,
            "redistribution_rights_verified": False,
        })
    return {
        "schema_version": 1,
        "kind": "license-review-evidence-worksheet",
        "python_inventory_sha256": python_sha256,
        "native_inventory_sha256": native_sha256,
        "python_environment_packages": packages,
        "native_libraries": libraries,
        "font_matches": fonts,
        "review_counts": {
            "python_pending": len(packages),
            "native_pending": len(libraries),
            "font_pending": len(fonts),
            "packages_missing_modern_license_expression": sum(
                p["metadata_class"] != "license_expression_declared" for p in packages
            ),
            "native_environment_observed": native is not None,
        },
        "signoffs": {
            "python_transitive_licenses": False,
            "native_library_licenses": False,
            "font_embedding_and_redistribution": False,
            "approved_release_bill_of_materials": False,
        },
        "human_signoff_required": True,
        "physical_device_verified": False,
        "approved_for_release": False,
        "limitations": [
            "Installed environments can differ from distributed release assets",
            "License metadata claims are not legal proof of redistribution rights",
            "Font family matches do not identify underlying font assets or embedding rights",
            "Native library versions do not identify all statically or dynamically linked libraries",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python", type=Path, required=True, help="Installed environment JSON")
    parser.add_argument("--native", type=Path, help="Optional native/font observation JSON")
    parser.add_argument("--output", type=Path, required=True, help="Private create-only worksheet")
    args = parser.parse_args(argv)
    try:
        py, py_hash = _read(args.python, "installed-python-environment-inventory")
        native = None
        native_hash = None
        if args.native is not None:
            native, native_hash = _read(args.native, "native-print-dependency-observation")
        worksheet = build_matrix(py, native=native, python_sha256=py_hash,
                                 native_sha256=native_hash)
        if args.output.is_symlink() or args.output.exists() or args.output.parent.is_symlink():
            raise ReviewMatrixError("output_already_exists_or_unsafe")
        args.output.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        if args.output.parent.stat().st_mode & 0o077:
            raise ReviewMatrixError("output_parent_must_be_private")
        fd = os.open(args.output,
                     os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
                     0o600)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump(worksheet, stream, sort_keys=True, indent=2)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
        except BaseException:
            args.output.unlink(missing_ok=True)
            raise
    except (OSError, ReviewMatrixError):
        print(json.dumps({"status": "rejected", "error": "license_evidence_preflight_failed"}))
        return 2
    print(json.dumps({
        "status": "pending_human_license_review",
        "python_packages": len(worksheet["python_environment_packages"]),
        "native_environment_observed": native is not None,
        "signoff_complete": False,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
