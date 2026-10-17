"""Bounded native print dependency + font *identity* inventory.

No font files are copied or uploaded. Package-reported versions and selected
font-family matches are evidence for human license/compatibility review only.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess


NATIVE_LIBRARIES = ("pango", "fontconfig", "harfbuzz", "cairo")
FONT_QUERIES = ("sans-serif", "serif", "monospace")
SAFE_TEXT = re.compile(r"[A-Za-z0-9 .,+_()/-]{1,120}\Z")


def _probe(args: list[str], *, executable: str | None) -> str | None:
    if executable is None:
        return None
    try:
        result = subprocess.run(
            [executable, *args], capture_output=True, text=True,
            timeout=10, check=False,
        )
        value = result.stdout.strip()
        if result.returncode == 0 and SAFE_TEXT.fullmatch(value):
            return value
    except (OSError, subprocess.TimeoutExpired):
        pass
    return None


def collect_native_inventory() -> dict:
    pkg = shutil.which("pkg-config")
    fonts = shutil.which("fc-match")
    libraries = {
        name: _probe(["--modversion", name], executable=pkg)
        for name in NATIVE_LIBRARIES
    }
    matches = {
        name: _probe(["--format", "%{family}", name], executable=fonts)
        for name in FONT_QUERIES
    }
    return {
        "schema_version": 1,
        "kind": "native-print-dependency-observation",
        "observed_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "os": platform.system(),
        "architecture": platform.machine(),
        "native_library_versions": libraries,
        "font_family_matches": matches,
        "font_files_copied": False,
        "font_licenses_reviewed": False,
        "native_dependency_licenses_reviewed": False,
        "vulnerability_audit_complete": False,
        "physical_print_verified": False,
        "limitations": [
            "pkg-config and fc-match are optional; missing results are unknown, not absent",
            "Font family selection is not a copyright or embedding-license review",
            "Platform-version observations do not guarantee reproducible native builds",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    path = args.output
    if path.is_symlink() or path.exists():
        parser.error("native inventory destination already exists")
    data = collect_native_inventory()
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, sort_keys=True)
            file.write("\n")
    except FileExistsError:
        parser.error("native inventory destination already exists")
    print(json.dumps({
        "status": "native_observation_written",
        "native_versions_observed": sum(v is not None for v in data["native_library_versions"].values()),
        "font_families_observed": sum(v is not None for v in data["font_family_matches"].values()),
        "license_review_complete": False,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
