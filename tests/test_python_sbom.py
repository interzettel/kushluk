"""Offline and privacy checks for installed-package inventory."""
import json
from types import SimpleNamespace

import pytest

from tools import python_sbom


def pkg(name, version, **meta):
    return SimpleNamespace(metadata={"Name": name, **meta}, version=version)


def test_deterministic_cyclonedx_inventory_from_installed_metadata():
    records = [
        pkg("Kushluk", "0.1.0"), pkg("Pillow", "12.3.0", **{"License-Expression": "MIT"}),
        pkg("httpx", "0.28.1", **{"License-Expression": "BSD-3-Clause"}),
        pkg("PRIVATE/TOKEN", "0.1.0", License="private-key"),
        pkg("jInJA_2", "3.1.6", License="legacy unverified metadata"),
        pkg("Pillow", "12.3.0", **{"License-Expression": "MIT"}),
    ]
    result = python_sbom.make_inventory(iter(records))
    assert result["bomFormat"] == "CycloneDX"
    assert result["specVersion"] == "1.5"
    assert result["metadata"]["component"]["version"] == "0.1.0"
    assert [c["name"] for c in result["components"]] == ["httpx", "jinja-2", "pillow"]
    assert len(result["components"]) == 3
    assert result["components"][-1]["licenses"] == [{"expression": "MIT"}]
    assert "licenses" not in result["components"][1]
    assert "private-key" not in json.dumps(result)
    assert "PRIVATE/TOKEN" not in json.dumps(result)
    assert python_sbom.make_inventory(reversed(records)) == result


def test_no_unsafe_expressions_or_paths_can_escape_into_component_names():
    value = python_sbom.make_inventory([
        pkg("Test", "0.2", **{"License-Expression": "SECRET;/home/user/id_rsa"}),
        pkg("owner@host", "1.0"),
        pkg("valid_name", "1.0"),
        pkg("badpackage", "1.0\nPRIVATE_PASSWORD"),
    ])
    raw = json.dumps(value)
    assert "SECRET" not in raw and "PRIVATE_PASSWORD" not in raw
    assert "owner@host" not in raw
    assert value["components"] == [{
        "type": "library", "name": "test", "version": "0.2",
        "purl": "pkg:pypi/test@0.2",
    }, {"type": "library", "name": "valid-name", "version": "1.0",
        "purl": "pkg:pypi/valid-name@1.0"}]


def test_create_only_writes_deterministic_private_bom(tmp_path, monkeypatch, capsys):
    original = python_sbom.make_inventory
    monkeypatch.setattr(python_sbom, "make_inventory",
                        lambda: original([pkg("kushluk", "0.1.0"),
                                          pkg("pypdf", "6.0")]))
    output = tmp_path / "evidence" / "installed.json"
    assert python_sbom.main(["--output", str(output)]) == 0
    first = output.read_bytes()
    assert first.endswith(b"\n")
    assert json.loads(first)["components"][0]["purl"] == "pkg:pypi/pypdf@6.0"
    assert output.stat().st_mode & 0o777 == 0o600
    summary = json.loads(capsys.readouterr().out)
    assert summary["license_signoff"] is False
    assert summary["dependency_graph_complete"] is False
    with pytest.raises(SystemExit):
        python_sbom.main(["--output", str(output)])
    assert output.read_bytes() == first


def test_symlinked_output_is_never_followed(tmp_path, monkeypatch):
    monkeypatch.setattr(python_sbom, "make_inventory",
                        lambda: python_sbom.make_inventory([]))
    dest = tmp_path / "existing"
    dest.write_text("Unchanged!")
    link = tmp_path / "sbom.json"
    link.symlink_to(dest)
    with pytest.raises(SystemExit):
        python_sbom.main(["--output", str(link)])
    assert dest.read_text() == "Unchanged!"
