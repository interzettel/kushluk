"""M1 distribution acceptance: build, inspect and *clean-install* wheel + sdist.

No repository import path is exposed to installed tests. Outputs contain only
original synthetic previews and package artifacts. A green software proof does
not verify a printer, inbox, unattended machine or permission-bearing source.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import tomllib
import venv
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parent.parent
FIXED_SOURCE_DATE_EPOCH = str(int(
    datetime(2026, 10, 17, tzinfo=timezone.utc).timestamp()
))
REQUIRED_FILES = (
    "kushluk/cli.py",
    "kushluk/preview.py",
    "kushluk/renderer.py",
    "kushluk/models.py",
    "kushluk/templates/edition.html",
)


class ReleaseCheckError(ValueError):
    """Installable preview evidence was not established."""


def _run(command: list[str], *, cwd: Path, env: dict | None = None) -> str:
    result = subprocess.run(
        command, cwd=cwd, env=env, capture_output=True, text=True,
        check=False, timeout=240,
    )
    if result.returncode:
        # CI fixtures contain no user content. Never include credential-bearing
        # environment values or optional secret source files in output.
        raise ReleaseCheckError(
            f"release smoke command failed: {command[0:3]!r}\n"
            + result.stdout[-2200:] + result.stderr[-2200:]
        )
    return result.stdout


def _digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _installed_inside_venv(installed_path: str, venv_dir: Path) -> bool:
    """Resolve macOS /var vs /private/var aliases before checking isolation.

    A raw string-prefix test incorrectly rejects valid macOS virtualenvs and
    can also accept a similarly named sibling directory. The installed module
    must be a real file under the same real virtualenv and inside site-packages.
    """
    try:
        target = Path(installed_path).resolve(strict=True)
        root = venv_dir.resolve(strict=True)
        return target.is_file() and target.is_relative_to(root) and (
            "site-packages" in target.parts
        )
    except (OSError, RuntimeError):
        return False


def _check_packages(directory: Path, *, version: str) -> tuple[Path, Path]:
    wheels = list(directory.glob("kushluk-*.whl"))
    sdists = list(directory.glob("kushluk-*.tar.gz"))
    if len(wheels) != 1 or len(sdists) != 1:
        raise ReleaseCheckError("expected_exactly_one_wheel_and_sdist")
    wheel, sdist = wheels[0], sdists[0]
    if not wheel.name.startswith(f"kushluk-{version}-"):
        raise ReleaseCheckError("wheel_version_mismatch")
    if not sdist.name.startswith(f"kushluk-{version}.tar.gz"):
        raise ReleaseCheckError("sdist_version_mismatch")
    with ZipFile(wheel) as opened:
        names = set(opened.namelist())
        for name in REQUIRED_FILES:
            if name not in names:
                raise ReleaseCheckError(f"wheel_missing_required_module:{name}")
        metadata_names = [name for name in names if name.endswith(".dist-info/METADATA")]
        entry_names = [name for name in names if name.endswith(".dist-info/entry_points.txt")]
        if len(metadata_names) != 1 or len(entry_names) != 1:
            raise ReleaseCheckError("wheel_metadata_missing")
        metadata = opened.read(metadata_names[0]).decode()
        if f"Version: {version}" not in metadata:
            raise ReleaseCheckError("wheel_version_metadata_wrong")
        if "kushluk = kushluk.cli:main" not in opened.read(entry_names[0]).decode():
            raise ReleaseCheckError("wheel_cli_entrypoint_missing")
    with tarfile.open(sdist, mode="r:gz") as opened:
        names = set(opened.getnames())
        prefix = f"kushluk-{version}/"
        for name in REQUIRED_FILES:
            if prefix + "src/" + name not in names:
                raise ReleaseCheckError(f"sdist_missing_required_module:{name}")
        for name in ("pyproject.toml", "README.md", "LICENSE",
                     "THIRD_PARTY_NOTICES.md", "SECURITY.md", "CHANGELOG.md",
                     "docs/PREVIEW_INSTALL.md", "docs/RELEASE_PLAN.md",
                     "docs/DEPENDENCY_AUDIT.md", "docs/ARCHIVE_COMPATIBILITY.md"):
            if prefix + name not in names:
                raise ReleaseCheckError(f"sdist_missing_required_file:{name}")
        if any(
            "/.env" in name or "/archive/" in name or "/output/" in name
            or name.endswith(".pem") or name.endswith(".key")
            for name in names
        ):
            raise ReleaseCheckError("private_or_runtime_file_in_source_distribution")
    return wheel, sdist


def _clean_install(
    artifact: Path, *, home: Path, version: str, pdf: bool,
) -> dict:
    home.mkdir(parents=True)
    venv_dir = home / "venv"
    venv.EnvBuilder(with_pip=True, clear=False).create(venv_dir)
    binary = "Scripts" if os.name == "nt" else "bin"
    python = venv_dir / binary / ("python.exe" if os.name == "nt" else "python")
    command = venv_dir / binary / ("kushluk.exe" if os.name == "nt" else "kushluk")
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    env["PYTHONNOUSERSITE"] = "1"
    env["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
    env["KUSHLUK_RSS_URLS"] = "https://invalid.example.test/no-network-allowed"
    requirement = str(artifact) + ("[pdf]" if pdf else "")
    _run(
        [str(python), "-m", "pip", "install", "--no-input", "--no-cache-dir", requirement],
        cwd=home, env=env,
    )
    check_code = (
        "from importlib.metadata import version; "
        "from importlib.resources import files; import kushluk; "
        f"assert version('kushluk') == {version!r}; "
        "assert files('kushluk').joinpath('templates/edition.html').is_file(); "
        "assert 'site-packages' in kushluk.__file__, kushluk.__file__; "
        "print(kushluk.__file__)"
    )
    installed_path = _run(
        [str(python), "-c", check_code], cwd=home, env=env,
    ).strip()
    if not _installed_inside_venv(installed_path, venv_dir):
        raise ReleaseCheckError("installed_module_outside_clean_venv")
    _run([str(python), "-m", "pip", "check"], cwd=home, env=env)
    # Execute the stdlib-only inventory tool using the *installed* venv Python.
    # Never record metadata_location, installer paths, direct_url or user settings.
    inventory_path = home / "installed-environment.json"
    _run([
        str(python), str(ROOT / "tools" / "release_inventory.py"),
        "--output", str(inventory_path),
    ], cwd=home, env=env)
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    if (not any(package["name"] == "kushluk" and package["version"] == version
                for package in inventory["installed_packages"])
            or inventory["legal_license_review_complete"]
            or inventory["vulnerability_audit_complete"]):
        raise ReleaseCheckError("invalid_installed_dependency_inventory")
    # Machine-generated review gaps only; do not grant license or native-font approval.
    worksheet_path = home / "license-review" / "worksheet.json"
    _run([
        str(python), str(ROOT / "tools" / "license_review_matrix.py"),
        "--python", str(inventory_path), "--output", str(worksheet_path),
    ], cwd=home, env=env)
    worksheet = json.loads(worksheet_path.read_text(encoding="utf-8"))
    if (worksheet.get("approved_for_release") is not False
            or worksheet.get("human_signoff_required") is not True
            or worksheet["review_counts"]["python_pending"] != len(
                inventory["installed_packages"])):
        raise ReleaseCheckError("invalid_license_review_worksheet")
    _run([str(command), "--help"], cwd=home, env=env)
    # This is the *installed* wheel/sdist CLI, not an editable checkout.
    # The kit must be private, completely blank and unable to self-approve.
    kit_dir = home / "blank-pilot-kit"
    kit_result = json.loads(_run([
        str(command), "pilot-kit", "--output-dir", str(kit_dir),
    ], cwd=home, env=env))
    if (kit_result.get("status") != "private_blank_pilot_kit_created"
            or kit_result.get("files_created") != 5
            or kit_result.get("beta_publication_authorized") is not False):
        raise ReleaseCheckError("invalid_clean_install_pilot_kit_cli")
    kit_manifest = json.loads((kit_dir / "MANIFEST.json").read_text())
    if (kit_manifest.get("kind") != "m2a_private_blank_operator_kit"
            or kit_manifest.get("status") != "template_not_an_observation"
            or kit_manifest.get("source_commit_verified_against_installation") is not False
            or kit_manifest.get("participant_tested") is not False
            or kit_manifest.get("paper_physically_tested") is not False
            or kit_manifest.get("beta_publication_authorized") is not False
            or kit_manifest.get("release_gates_independently_verified") != 0):
        raise ReleaseCheckError("invalid_installed_blank_pilot_kit_manifest")
    kit_files = kit_manifest.get("files_sha256")
    if (not isinstance(kit_files, dict)
            or set(kit_files) != {
                "first-reader.json", "accessibility.json", "safety.json", "SESSION.md"
            }):
        raise ReleaseCheckError("invalid_installed_blank_pilot_kit_files")
    for name, expected_sha in kit_files.items():
        if _digest(kit_dir / name) != expected_sha:
            raise ReleaseCheckError("installed_pilot_kit_checksum_mismatch")
    if (json.loads((kit_dir / "first-reader.json").read_text()).get("status")
            != "template-not-observation"):
        raise ReleaseCheckError("installed_pilot_kit_not_blank")
    if (json.loads((kit_dir / "safety.json").read_text()).get("status")
            != "template-not-observation"):
        raise ReleaseCheckError("installed_safety_kit_not_blank")
    preview_dir = home / "preview"
    args = [str(command), "preview", "--output-dir", str(preview_dir)]
    if pdf:
        args.append("--pdf")
    result = json.loads(_run(args, cwd=home, env=env))
    if (result.get("status") != "synthetic_preview_created"
            or result.get("logical_pages") != 4
            or result.get("physical_verified") is not False
            or result.get("pdf_validated") is not pdf):
        raise ReleaseCheckError("invalid_installed_cli_preview_status")
    manifest = json.loads((preview_dir / "preview-manifest.json").read_text())
    if (manifest["fixture_date"] != "2026-10-17"
            or manifest["fixture_generated_at"] != "2026-10-17T07:00:00+02:00"
            or manifest["synthetic_only"] is not True
            or manifest["network_requests"] != 0
            or manifest["printer_submissions"] != 0
            or manifest["mail_submissions"] != 0):
        raise ReleaseCheckError("invalid_preview_provenance_manifest")
    for name, digest in manifest["files"].items():
        if "/" in name or "\\" in name or _digest(preview_dir / name) != digest:
            raise ReleaseCheckError("installed_preview_digest_mismatch")
    if pdf:
        pdf_check = (
            "from pathlib import Path; from kushluk.validation import validate_pdf; "
            "import sys; result = validate_pdf(Path(sys.argv[1]), 4); "
            "assert result.ok, result.errors; print(result.page_count)"
        )
        output = _run(
            [str(python), "-c", pdf_check, str(preview_dir / "kushluk-preview.pdf")],
            cwd=home, env=env,
        ).strip()
        if output != "4":
            raise ReleaseCheckError("installed_four_page_pdf_invalid")
    return {
        "installed_distribution": artifact.name,
        "dependency_inventory": "installed-environment.json",
        "dependency_inventory_sha256": _digest(inventory_path),
        "dependency_count": len(inventory["installed_packages"]),
        "license_review_worksheet": "license-review-worksheet.json",
        "license_review_worksheet_sha256": _digest(worksheet_path),
        "license_signoff_complete": False,
        "legal_license_review_complete": False,
        "vulnerability_audit_complete": False,
        "installed_package_location": "isolated-venv-site-packages",
        "runtime_module_from_venv": True,  # strictly checked above after realpath resolution
        "fixture_version": manifest["fixture_version"],
        "pdf_validated": pdf,
        "synthetic_only": True,
        "physical_verified": False,
        "files": manifest["files"],
    }


def verify_preview(*, artifact_dir: Path, pdf: bool = False) -> dict:
    data = tomllib.loads((ROOT / "pyproject.toml").read_text())
    version = data["project"]["version"]
    with tempfile.TemporaryDirectory(prefix="kushluk-release-smoke-") as root:
        temp = Path(root)
        first = temp / "build-one"
        second = temp / "build-two"
        first.mkdir()
        second.mkdir()
        env = os.environ.copy()
        env["SOURCE_DATE_EPOCH"] = FIXED_SOURCE_DATE_EPOCH
        for target in (first, second):
            _run(
                [sys.executable, "-m", "build", "--sdist", "--wheel", "--outdir",
                 str(target)],
                cwd=ROOT, env=env,
            )
        wheel, sdist = _check_packages(first, version=version)
        second_wheel, second_sdist = _check_packages(second, version=version)
        if _digest(wheel) != _digest(second_wheel):
            raise ReleaseCheckError("wheel_not_reproducible")
        if _digest(sdist) != _digest(second_sdist):
            raise ReleaseCheckError("sdist_not_reproducible")
        installs = {}
        for label, artifact in (("wheel", wheel), ("sdist", sdist)):
            installs[label] = _clean_install(
                artifact, home=temp / label, version=version, pdf=pdf,
            )
        artifact_dir.mkdir(parents=True, exist_ok=True)
        if any(artifact_dir.iterdir()):
            raise ReleaseCheckError("release_evidence_destination_not_empty")
        shutil.copy2(wheel, artifact_dir / wheel.name)
        shutil.copy2(sdist, artifact_dir / sdist.name)
        for label in ("wheel", "sdist"):
            shutil.copytree(temp / label / "preview", artifact_dir / label)
            shutil.copy2(
                temp / label / "installed-environment.json",
                artifact_dir / label / "installed-environment.json",
            )
            shutil.copy2(
                temp / label / "license-review" / "worksheet.json",
                artifact_dir / label / "license-review-worksheet.json",
            )
        evidence = {
            "schema_version": 1, "status": "clean_install_passed",
            "development_version": version,
            "suggested_prerelease": "v0.2.0-alpha.1",
            "tag_created": False, "published": False,
            "platform": platform.system(), "machine": platform.machine(),
            "python_version": platform.python_version(),
            "builds_byte_reproducible": True,
            "installed_dependency_inventory_available": True,
            "legal_license_review_complete": False,
            "vulnerability_audit_complete": False,
            "native_dependency_review_complete": False,
            "pdf_validated": pdf,
            "physical_verified": False, "network_used_by_preview": False,
            "wheel_sha256": _digest(wheel),
            "sdist_sha256": _digest(sdist),
            "installs": installs,
        }
        (artifact_dir / "release-evidence.json").write_text(
            json.dumps(evidence, sort_keys=True, indent=2) + "\n", encoding="utf-8",
        )
        return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--artifact-dir", type=Path, default=Path("output/m1-preview-candidate"),
    )
    parser.add_argument(
        "--pdf", action="store_true",
        help="Require native PDF dependencies and four-page PDF in both clean installs",
    )
    args = parser.parse_args()
    report = verify_preview(artifact_dir=args.artifact_dir, pdf=args.pdf)
    print(json.dumps({
        "status": report["status"], "version": report["development_version"],
        "pdf_validated": report["pdf_validated"],
        "builds_byte_reproducible": report["builds_byte_reproducible"],
        "physical_verified": False, "published": False,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
