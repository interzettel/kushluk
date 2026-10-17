"""Offline, non-authoritative Python distribution and license metadata inventory.

This lists *installed* packages, not native Pango/fonts, vulnerabilities, or
legally approved licenses. No absolute filesystem paths or private settings
are written. Intended to run from each fresh M1 install environment.
"""
from __future__ import annotations

import argparse
from collections import Counter
from importlib import metadata
import json
from pathlib import Path
import re
import sys

NAME = re.compile(r"[a-z0-9][a-z0-9._-]{0,119}")
VERSION = re.compile(r"[A-Za-z0-9][A-Za-z0-9.!+_-]{0,119}")
LICENSE_EXPR = re.compile(r"[A-Za-z0-9][A-Za-z0-9.()+_ -]{0,159}")


def installed_inventory() -> dict:
    packages = []
    for distribution in metadata.distributions():
        fields = distribution.metadata
        name = (fields.get("Name") or "").strip().lower().replace("_", "-")
        version = (fields.get("Version") or "").strip()
        if not NAME.fullmatch(name) or not VERSION.fullmatch(version):
            raise ValueError("unsafe_distribution_metadata")
        expression = fields.get("License-Expression")
        if expression is not None and LICENSE_EXPR.fullmatch(expression.strip()):
            expression = expression.strip()
            status = "license_expression_declared"
        else:
            expression = None
            classifiers = fields.get_all("Classifier", []) or []
            if any(isinstance(v, str) and v.startswith("License :: ") for v in classifiers):
                status = "license_classifier_only"
            elif fields.get("License"):
                status = "legacy_license_field_only"
            else:
                status = "license_metadata_missing"
        packages.append({
            "name": name, "version": version,
            "license_expression_metadata": expression,
            "license_metadata_status": status,
            "is_python_install_tool": name in {"pip", "setuptools", "wheel"},
        })
    packages.sort(key=lambda x: (x["name"], x["version"]))
    if len({pkg["name"] for pkg in packages}) != len(packages):
        raise ValueError("duplicate_distribution_name")
    if "kushluk" not in {pkg["name"] for pkg in packages}:
        raise ValueError("kushluk_not_installed")
    summary = dict(sorted(Counter(
        pkg["license_metadata_status"] for pkg in packages
    ).items()))
    return {
        "schema_version": 1,
        "kind": "installed-python-environment-inventory",
        "python_version": ".".join(map(str, sys.version_info[:3])),
        "installed_packages": packages,
        "license_metadata_summary": summary,
        "legal_license_review_complete": False,
        "vulnerability_audit_complete": False,
        "native_font_and_library_inventory_complete": False,
        "contains_absolute_install_paths": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.is_symlink() or args.output.exists():
        parser.error("inventory destination must be a new regular file")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    inventory = installed_inventory()
    with args.output.open("x", encoding="utf-8") as file:
        json.dump(inventory, file, indent=2, sort_keys=True)
        file.write("\n")
    print(json.dumps({
        "status": "inventory_written",
        "packages": len(inventory["installed_packages"]),
        "legal_license_review_complete": False,
        "vulnerability_audit_complete": False,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
