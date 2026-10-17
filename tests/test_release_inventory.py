"""Dependency metadata inventory does not imply a license or security approval."""
from __future__ import annotations

from email.message import Message
import json

import pytest

from tools import release_inventory


class FakeDist:
    def __init__(self, name, version, *, expression=None, license_text=None,
                 classifier=None):
        self.metadata = Message()
        self.metadata["Name"] = name
        self.metadata["Version"] = version
        if expression is not None:
            self.metadata["License-Expression"] = expression
        if license_text is not None:
            self.metadata["License"] = license_text
        if classifier:
            self.metadata["Classifier"] = classifier


def test_licenses_are_marked_declared_not_legally_approved(monkeypatch):
    distributions = [
        FakeDist("kushluk", "0.1.0", license_text="MIT"),
        FakeDist("jinja2", "3.1.6", expression="BSD-3-Clause"),
        FakeDist("httpx", "0.28.1", classifier="License :: OSI Approved :: BSD License"),
        FakeDist("unknown-library", "1.0"),
        FakeDist("pip", "26.0", expression="MIT"),
    ]
    monkeypatch.setattr(release_inventory.metadata, "distributions", lambda: distributions)
    report = release_inventory.installed_inventory()
    assert report["legal_license_review_complete"] is False
    assert report["vulnerability_audit_complete"] is False
    assert report["native_font_and_library_inventory_complete"] is False
    assert report["license_metadata_summary"] == {
        "legacy_license_field_only": 1, "license_classifier_only": 1,
        "license_expression_declared": 2, "license_metadata_missing": 1,
    }
    body = json.dumps(report)
    assert "site-packages" not in body
    assert "MY_SUPER_SECRET" not in body
    packages = {row["name"]: row for row in report["installed_packages"]}
    assert packages["jinja2"]["license_expression_metadata"] == "BSD-3-Clause"
    assert packages["pip"]["is_python_install_tool"] is True


def test_inventory_strips_unsafe_license_expression_metadata(monkeypatch):
    monkeypatch.setattr(release_inventory.metadata, "distributions", lambda: [
        FakeDist("kushluk", "0.1.0", expression="private path /home/alice/token"),
    ])
    report = release_inventory.installed_inventory()
    assert report["installed_packages"][0]["license_expression_metadata"] is None
    assert report["installed_packages"][0]["license_metadata_status"] == (
        "license_metadata_missing"
    )


def test_inventory_refuses_bad_package_id_and_missing_installed_kushluk(monkeypatch):
    monkeypatch.setattr(release_inventory.metadata, "distributions", lambda: [
        FakeDist("secret/path", "1.0"), FakeDist("kushluk", "0.1.0"),
    ])
    with pytest.raises(ValueError, match="unsafe_distribution_metadata"):
        release_inventory.installed_inventory()
    monkeypatch.setattr(release_inventory.metadata, "distributions", lambda: [
        FakeDist("httpx", "0.28.1"),
    ])
    with pytest.raises(ValueError, match="kushluk_not_installed"):
        release_inventory.installed_inventory()


def test_inventory_refuses_duplicate_normalized_names(monkeypatch):
    monkeypatch.setattr(release_inventory.metadata, "distributions", lambda: [
        FakeDist("kushluk", "0.1.0"), FakeDist("kushluk", "0.1.1"),
    ])
    with pytest.raises(ValueError, match="duplicate_distribution_name"):
        release_inventory.installed_inventory()
