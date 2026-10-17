"""The proposed 0.2.0a1 build trial changes only a disposable source snapshot."""
from __future__ import annotations

import io
import json
from pathlib import Path
import tarfile

import pytest

from tools import alpha_build_trial as trial


def _tar(entries):
    data = io.BytesIO()
    with tarfile.open(fileobj=data, mode="w") as archive:
        for name, content in entries:
            info = tarfile.TarInfo(name)
            info.size = len(content)
            info.mode = 0o644
            archive.addfile(info, io.BytesIO(content))
    return data.getvalue()


def test_changes_only_project_version_not_docs_or_unrelated_metadata():
    source = (
        '[build-system]\nrequires = ["hatchling>=1.25"]\n\n'
        '[project]\nname = "kushluk"\nversion = "0.1.0"\n'
        'description = "0.1.0 documentation"\n\n'
        '[tool.optional]\nversion = "0.1.0"\n'
    )
    result = trial.patch_project_version(source)
    assert '[project]\nname = "kushluk"\nversion = "0.2.0a1"' in result
    assert 'description = "0.1.0 documentation"' in result
    assert '[tool.optional]\nversion = "0.1.0"' in result
    assert result.count('version = "0.2.0a1"') == 1
    assert source.count('version = "0.1.0"') == 2


@pytest.mark.parametrize("source", [
    '[project]\nname = "kushluk"\nversion = "0.2.0a1"\n',
    '[tool.other]\nversion = "0.1.0"\n',
    '[project]\nname = "kushluk"\n',
])
def test_refuses_unexpected_package_version_or_missing_project(source):
    with pytest.raises(trial.AlphaTrialError):
        trial.patch_project_version(source)


def test_tar_snapshot_only_extracts_regular_tracked_files(tmp_path):
    arc = _tar([
        ("pyproject.toml", b'[project]\nversion = "0.1.0"\n'),
        ("src/kushluk/__init__.py", b""),
        ("src/kushluk/cli.py", b"# harmless\n"),
    ])
    assert trial.unpack_tracked_source(arc, tmp_path / "stage") == 3
    assert (tmp_path / "stage" / "src/kushluk/__init__.py").read_bytes() == b""


def test_blocks_traversal_and_symlink_entries(tmp_path):
    path = _tar([("../escape", b"contents")])
    with pytest.raises(trial.AlphaTrialError, match="unsafe_tracked_archive_path"):
        trial.unpack_tracked_source(path, tmp_path / "files")
    assert not (tmp_path / "escape").exists()
    data = io.BytesIO()
    with tarfile.open(fileobj=data, mode="w") as arc:
        info = tarfile.TarInfo("untrusted-link")
        info.type = tarfile.SYMTYPE
        info.linkname = "/etc/passwd"
        arc.addfile(info)
    with pytest.raises(trial.AlphaTrialError, match="symlink"):
        trial.unpack_tracked_source(data.getvalue(), tmp_path / "files")


def test_isolated_alpha_trial_holds_release_signoff_false(tmp_path, monkeypatch):
    pyproject = Path("pyproject.toml").read_bytes()
    entries = [("pyproject.toml", pyproject)]
    entries += [(f"docs/synthetic-{i}.txt", b"fictional text") for i in range(24)]
    snapshot = _tar(entries)
    calls = []
    repo_version = Path("pyproject.toml").read_bytes()

    def fake_run(cmd, *, cwd, env=None, timeout=500):
        calls.append((cmd, cwd))
        if cmd[:3] == ["git", "rev-parse", "--verify"]:
            return b"a" * 40 + b"\n"
        if cmd[:3] == ["git", "archive", "--format=tar"]:
            return snapshot
        assert "tools.release_check" in cmd
        stage_version = (cwd / "pyproject.toml").read_text()
        assert 'version = "0.2.0a1"' in stage_version
        dest = tmp_path / "trial"
        dest.mkdir()
        (dest / "release-evidence.json").write_text(json.dumps({
            "status": "clean_install_passed", "development_version": "0.2.0a1",
        }))
        return b'{"status":"clean_install_passed","version":"0.2.0a1"}'

    monkeypatch.setattr(trial, "_run", fake_run)
    import tools.m1_bundle_preflight as preflight
    monkeypatch.setattr(preflight, "inspect_bundle", lambda p, require_pdf=False: {
        "installed_version": "0.2.0a1", "release_authorized": False,
    })
    result = trial.alpha_version_trial(artifact_dir=tmp_path / "trial")
    assert result["status"] == "alpha_version_software_trial_passed"
    assert result["isolated_trial_package_version"] == "0.2.0a1"
    assert result["repository_version_bumped"] is False
    assert result["release_authorized"] is False
    assert result["tag_created"] is False
    assert result["release_published"] is False
    assert len(calls) == 3
    assert Path("pyproject.toml").read_bytes() == repo_version
    assert json.loads((tmp_path / "trial" / "alpha-version-trial.json").read_text())[
        "tag_created"
    ] is False


def test_existing_destination_is_not_overwritten(tmp_path):
    directory = tmp_path / "candidate"
    directory.mkdir()
    with pytest.raises(trial.AlphaTrialError, match="destination"):
        trial.alpha_version_trial(artifact_dir=directory)
