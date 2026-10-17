"""Offline tests for safe, bounded native print dependency observations."""
import json
import subprocess

import pytest

from tools import native_inventory


def test_native_inventory_records_only_names_and_versions(monkeypatch):
    monkeypatch.setattr(native_inventory.shutil, "which", lambda name: "/usr/bin/" + name)

    def fixture_run(cmd, **kwargs):
        if cmd[0].endswith("pkg-config"):
            return subprocess.CompletedProcess(cmd, 0, "1.52.0\n", "")
        return subprocess.CompletedProcess(cmd, 0, "Noto Sans\n", "")

    monkeypatch.setattr(native_inventory.subprocess, "run", fixture_run)
    observation = native_inventory.collect_native_inventory()
    assert observation["native_library_versions"]["pango"] == "1.52.0"
    assert observation["font_family_matches"]["sans-serif"] == "Noto Sans"
    assert observation["font_files_copied"] is False
    assert observation["font_licenses_reviewed"] is False
    assert observation["physical_print_verified"] is False
    assert "/usr/bin" not in json.dumps(observation)


def test_rejects_sensitive_command_output(monkeypatch):
    monkeypatch.setattr(native_inventory.shutil, "which", lambda name: "/usr/bin/" + name)
    monkeypatch.setattr(native_inventory.subprocess, "run",
                        lambda *args, **kwargs: subprocess.CompletedProcess(
                            args, 0, "PRIVATE=/home/user/PASSWORD?secret=hi", ""))
    result = native_inventory.collect_native_inventory()
    assert all(x is None for x in result["font_family_matches"].values())
    assert all(x is None for x in result["native_library_versions"].values())


def test_missing_tools_and_no_overwrite(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(native_inventory.shutil, "which", lambda name: None)
    file = tmp_path / "private" / "native.json"
    assert native_inventory.main(["--output", str(file)]) == 0
    report = json.loads(file.read_text())
    assert all(x is None for x in report["font_family_matches"].values())
    old = file.read_bytes()
    with pytest.raises(SystemExit):
        native_inventory.main(["--output", str(file)])
    assert file.read_bytes() == old
