"""Fail-closed source-only GitHub alpha archive gate.

Ensures release assets contain Kuşluk's Python source, HTML template and
legally required prose — never system fonts, native libraries, PDFs, private
feeds or images. This is a content boundary, not a legal opinion.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import re
import tarfile
from zipfile import ZipFile

PYTHON_VERSION = "0.2.0a1"
TAG = "v0.2.0-alpha.1"
BLOCKED_SUFFIXES = (
    ".ttf", ".otf", ".woff", ".woff2", ".ttc", ".eot",
    ".so", ".dylib", ".dll", ".pyd", ".a", ".lib", ".exe",
    ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".webp",
    ".db", ".sqlite", ".pem", ".key", ".p12", ".env",
)
ALLOWED_TOP = frozenset({
    "README.md", "LICENSE", "THIRD_PARTY_NOTICES.md", "SECURITY.md",
    "CHANGELOG.md", "pyproject.toml", "PKG-INFO", ".gitignore",
})
ALLOWED_DOCS = frozenset({
    "PREVIEW_INSTALL.md", "RELEASE_PLAN.md", "DEPENDENCY_AUDIT.md",
    "ARCHIVE_COMPATIBILITY.md", "M1_ALPHA_CANDIDATE.md",
    "RELEASE_APPROVAL.md",
})


class SourceScopeError(ValueError):
    """Archive does not meet the limited GitHub source-only release contract."""


def _path(name: str) -> PurePosixPath:
    path = PurePosixPath(name)
    if (path.is_absolute() or not path.parts
            or any(part in {"..", ".", ""} for part in path.parts)
            or "\\" in name):
        raise SourceScopeError("unsafe_archive_member")
    if path.suffix.lower() in BLOCKED_SUFFIXES:
        raise SourceScopeError("bundled_native_binary_or_font_asset")
    return path


def inspect_archives(wheel: Path, sdist: Path) -> dict:
    if (wheel.name != f"kushluk-{PYTHON_VERSION}-py3-none-any.whl"
            or sdist.name != f"kushluk-{PYTHON_VERSION}.tar.gz"):
        raise SourceScopeError("wrong_alpha_distribution_version")
    if any(p.is_symlink() or not p.is_file() for p in (wheel, sdist)):
        raise SourceScopeError("untrusted_release_artifact")
    package_files = 0
    license_file = False
    try:
        with ZipFile(wheel) as archive:
            for info in archive.infolist():
                member = _path(info.filename)
                if info.is_dir():
                    continue
                path = member.as_posix()
                if path.startswith("kushluk/"):
                    if (member.suffix != ".py"
                            and path != "kushluk/templates/edition.html"):
                        raise SourceScopeError("unexpected_wheel_payload")
                    package_files += 1
                elif path.startswith(f"kushluk-{PYTHON_VERSION}.dist-info/"):
                    tail = path.partition(".dist-info/")[2]
                    if tail not in {
                        "METADATA", "WHEEL", "entry_points.txt", "RECORD",
                        "licenses/LICENSE",
                    }:
                        raise SourceScopeError("unexpected_wheel_metadata")
                    if tail == "licenses/LICENSE":
                        license_file = True
                else:
                    raise SourceScopeError("wheel_contains_external_assets")
        if package_files < 20 or not license_file:
            raise SourceScopeError("wheel_missing_python_or_licence")
        prefix = f"kushluk-{PYTHON_VERSION}/"
        docs = set()
        notices = False
        with tarfile.open(sdist, mode="r:gz") as archive:
            for info in archive:
                if info.isdir():
                    continue
                if not info.isfile():
                    raise SourceScopeError("unsafe_source_member_type")
                name = _path(info.name).as_posix()
                if not name.startswith(prefix):
                    raise SourceScopeError("source_archive_bad_prefix")
                remaining = name[len(prefix):]
                member = _path(remaining)
                if remaining.startswith("src/kushluk/"):
                    if member.suffix != ".py" and remaining != (
                        "src/kushluk/templates/edition.html"
                    ):
                        raise SourceScopeError("source_archive_contains_asset")
                elif remaining.startswith("docs/"):
                    if remaining[5:] not in ALLOWED_DOCS:
                        raise SourceScopeError("unreviewed_release_document")
                    docs.add(remaining)
                elif remaining not in ALLOWED_TOP:
                    raise SourceScopeError("unreviewed_source_archive_file")
                if remaining == "THIRD_PARTY_NOTICES.md":
                    notices = True
        if not notices or "docs/PREVIEW_INSTALL.md" not in docs:
            raise SourceScopeError("missing_source_notice_or_instructions")
    except (OSError, ValueError, tarfile.TarError, EOFError) as exc:
        if isinstance(exc, SourceScopeError):
            raise
        raise SourceScopeError("unreadable_release_artifact") from exc
    return {
        "kind": "github_alpha_source_distribution_scope",
        "status": "source_only_archive_gate_passed",
        "tag": TAG,
        "version": PYTHON_VERSION,
        "wheel_python_modules": package_files,
        "first_party_source_only": True,
        "system_fonts_or_native_binaries_bundled": False,
        "third_party_runtime_binary_signoff": False,
        "physical_print_verified": False,
        "pypi_publication_authorized": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel", type=Path, required=True)
    parser.add_argument("--sdist", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = inspect_archives(args.wheel, args.sdist)
    except SourceScopeError as exc:
        print(json.dumps({"status": "rejected", "code": str(exc)}))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
