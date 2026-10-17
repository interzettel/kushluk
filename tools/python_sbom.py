"""Deterministic CycloneDX *installed-Python-environment* component inventory.

No downloads, wheel-file reads, source content, local paths, system fonts or
application credentials. This is NOT a verified release SBOM or licence signoff.
"""
from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
from pathlib import Path
import re

NAME = re.compile(r"[a-z0-9][a-z0-9._-]{0,127}\Z")
VERSION = re.compile(r"[A-Za-z0-9][A-Za-z0-9.+!_-]{0,79}\Z")
LICENSE = re.compile(r"[A-Za-z0-9 ().+_-]{1,160}\Z")


def make_inventory(distributions=None) -> dict:
    if distributions is None:
        distributions = importlib.metadata.distributions()
    components = {}
    app_version = None
    for dist in distributions:
        source_name = dist.metadata.get("Name")
        version = dist.version
        if not isinstance(source_name, str) or not isinstance(version, str):
            continue
        name = re.sub(r"[-_.]+", "-", source_name.lower())
        if not NAME.fullmatch(name) or not VERSION.fullmatch(version):
            continue
        if name == "kushluk":
            app_version = version
            continue
        key = (name, version)
        component = {
            "type": "library", "name": name, "version": version,
            "purl": f"pkg:pypi/{name}@{version}",
        }
        expression = dist.metadata.get("License-Expression")
        if isinstance(expression, str) and LICENSE.fullmatch(expression):
            component["licenses"] = [{"expression": expression}]
        # Unknown/legacy license statements are intentionally not
        # interpreted as SPDX approval or embedded into public artifacts.
        components[key] = component
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "version": 1,
        "metadata": {
            "component": {
                "type": "application", "name": "kushluk",
                "version": app_version or "unknown",
            },
        },
        "components": [components[k] for k in sorted(components)],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    path = args.output
    if path.exists() or path.is_symlink() or path.parent.is_symlink():
        parser.error("output_already_exists_or_unsafe")
    inventory = make_inventory()
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags, 0o600)
    except (FileExistsError, OSError):
        parser.error("output_already_exists_or_unsafe")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(inventory, stream, ensure_ascii=True, sort_keys=True, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise
    print(json.dumps({
        "status": "installed_environment_inventory_written",
        "component_count": len(inventory["components"]),
        "license_signoff": False,
        "dependency_graph_complete": False,
        "binary_artifacts_verified": False,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
