"""Build/test the proposed alpha VERSION inside a disposable tracked-source snapshot.

Not a version bump, approved release, Git tag, PyPI push, installer, or legal
signoff. Only git-tracked public files enter the disposable staging checkout.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tarfile
import tempfile

SOURCE_ROOT = Path(__file__).resolve().parent.parent
DEVELOPMENT_VERSION = "0.1.0"
ALPHA_PACKAGE_VERSION = "0.2.0a1"
ALPHA_TAG_PROPOSED = "v0.2.0-alpha.1"
FILE_LIMIT = 20 * 1024 * 1024
TOTAL_LIMIT = 100 * 1024 * 1024


class AlphaTrialError(ValueError):
    """A staged version-build precondition failed."""


def patch_project_version(text: str) -> str:
    """Modify exactly [project].version, never unrelated documentation/strings."""
    match = re.search(r"(?ms)^\[project\]\s*\n(?P<body>.*?)(?=^\[|\Z)", text)
    if match is None:
        raise AlphaTrialError("missing_project_metadata")
    old = re.compile(r'(?m)^version = "0\.1\.0"$')
    block, count = old.subn('version = "0.2.0a1"', match["body"])
    if count != 1:
        raise AlphaTrialError("unexpected_source_version")
    return text[:match.start("body")] + block + text[match.end("body"):]


def unpack_tracked_source(archive: bytes, dest: Path) -> int:
    """Extract only safe regular git archive entries to a temporary directory."""
    extracted = 0
    count = 0
    try:
        with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as source:
            for entry in source:
                target = PurePosixPath(entry.name)
                if (target.is_absolute()
                        or not target.parts
                        or any(p in {"..", "."} for p in target.parts)
                        or "\\" in entry.name or "\x00" in entry.name):
                    raise AlphaTrialError("unsafe_tracked_archive_path")
                location = dest.joinpath(*target.parts)
                if entry.isdir():
                    location.mkdir(parents=True, exist_ok=True)
                    continue
                if not entry.isfile():
                    raise AlphaTrialError("symlink_or_unsupported_tracked_entry")
                if (entry.size < 0 or entry.size > FILE_LIMIT
                        or extracted + entry.size > TOTAL_LIMIT or count > 5000):
                    raise AlphaTrialError("oversized_tracked_archive")
                location.parent.mkdir(parents=True, exist_ok=True)
                if location.exists() or location.is_symlink():
                    raise AlphaTrialError("duplicate_tracked_archive_entry")
                inp = source.extractfile(entry)
                if inp is None:
                    raise AlphaTrialError("invalid_git_archive_entry")
                payload = inp.read(FILE_LIMIT + 1)
                if len(payload) != entry.size:
                    raise AlphaTrialError("incorrect_tracked_entry_size")
                location.write_bytes(payload)
                extracted += entry.size
                count += 1
    except (tarfile.TarError, OSError) as exc:
        raise AlphaTrialError("unreadable_git_archive") from exc
    return count


def _run(args: list[str], *, cwd: Path, env: dict | None = None,
         timeout: int = 500) -> bytes:
    try:
        done = subprocess.run(
            args, cwd=cwd, env=env, capture_output=True, check=False, timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise AlphaTrialError("trial_command_unavailable") from exc
    if done.returncode != 0:
        # Never echo raw stdout/stderr, which could include local paths or tokens.
        raise AlphaTrialError("trial_command_failed")
    return done.stdout


def alpha_version_trial(*, artifact_dir: Path, pdf: bool = False) -> dict:
    if artifact_dir.is_symlink() or artifact_dir.exists():
        raise AlphaTrialError("trial_destination_must_be_new")
    revision = _run(
        ["git", "rev-parse", "--verify", "HEAD"], cwd=SOURCE_ROOT,
    ).decode("ascii").strip()
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise AlphaTrialError("invalid_source_commit")
    archived = _run(
        ["git", "archive", "--format=tar", "HEAD"], cwd=SOURCE_ROOT,
        timeout=70,
    )
    if not archived or len(archived) > 150 * 1024 * 1024:
        raise AlphaTrialError("invalid_tracked_snapshot_size")
    with tempfile.TemporaryDirectory(prefix="kushluk-alpha-version-trial-") as home:
        staged = Path(home) / "source"
        staged.mkdir()
        count = unpack_tracked_source(archived, staged)
        if count < 20:
            raise AlphaTrialError("incomplete_tracked_source")
        pyproject = staged / "pyproject.toml"
        if pyproject.is_symlink() or not pyproject.is_file():
            raise AlphaTrialError("missing_project_metadata")
        pyproject.write_text(
            patch_project_version(pyproject.read_text(encoding="utf-8")),
            encoding="utf-8",
        )
        env = os.environ.copy()
        env.pop("PYTHONPATH", None)
        env["PYTHONNOUSERSITE"] = "1"
        # release_check performs two fixed-epoch builds + fresh wheel/sdist
        # venv installs. It does not contact feeds, printer, mail or accounts.
        cli = [
            sys.executable, "-m", "tools.release_check",
            "--artifact-dir", str(artifact_dir.resolve()),
        ]
        if pdf:
            cli.append("--pdf")
        result = json.loads(_run(cli, cwd=staged, env=env, timeout=2000))
        if (result.get("status") != "clean_install_passed"
                or result.get("version") != ALPHA_PACKAGE_VERSION):
            # The release_check CLI might use development_version in its
            # output; authoritative version is the generated receipt below.
            evidence = json.loads(
                (artifact_dir / "release-evidence.json").read_text(encoding="utf-8")
            )
            if (evidence.get("status") != "clean_install_passed"
                    or evidence.get("development_version") != ALPHA_PACKAGE_VERSION):
                raise AlphaTrialError("wrong_installed_alpha_version")
        from tools.m1_bundle_preflight import inspect_bundle
        preflight = inspect_bundle(artifact_dir, require_pdf=pdf)
        if preflight.get("installed_version") != ALPHA_PACKAGE_VERSION:
            raise AlphaTrialError("wrong_installed_alpha_version")
        summary = {
            "schema_version": 1, "kind": "isolated_alpha_version_build_trial",
            "status": "alpha_version_software_trial_passed",
            "tracked_git_source_sha": revision,
            "tracked_file_count": count,
            "original_development_version": DEVELOPMENT_VERSION,
            "isolated_trial_package_version": ALPHA_PACKAGE_VERSION,
            "proposed_tag": ALPHA_TAG_PROPOSED,
            "trial_project_metadata_sha256": sha256(pyproject.read_bytes()).hexdigest(),
            "clean_wheel_and_sdist_installs": True,
            "independent_m1_bundle_preflight_passed": True,
            "pdf_validation_in_trial": pdf,
            "repository_version_bumped": False,
            "release_authorized": False,
            "native_and_font_licence_signoff": False,
            "tag_created": False, "release_published": False,
            "unattended_or_hardware_verified": False,
        }
        target = artifact_dir / "alpha-version-trial.json"
        target.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n",
                          encoding="utf-8")
        return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--pdf", action="store_true")
    args = parser.parse_args(argv)
    try:
        output = alpha_version_trial(artifact_dir=args.artifact_dir, pdf=args.pdf)
    except (OSError, UnicodeError, ValueError) as exc:
        code = str(exc) if isinstance(exc, AlphaTrialError) else "trial_input_invalid"
        print(json.dumps({"status": "rejected", "error": code,
                          "tag_created": False, "release_published": False}))
        return 2
    print(json.dumps(output, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
