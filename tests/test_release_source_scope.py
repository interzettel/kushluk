"""The first alpha release may distribute source, never system fonts/binaries."""
import io
from pathlib import Path
import tarfile
from zipfile import ZipFile, ZIP_DEFLATED

import pytest

from tools.release_source_scope import SourceScopeError, inspect_archives


def packages(tmp_path, *, extra_wheel=None, extra_sdist=None):
    wheel = tmp_path / "kushluk-0.2.0a1-py3-none-any.whl"
    sdist = tmp_path / "kushluk-0.2.0a1.tar.gz"
    with ZipFile(wheel, "w", compression=ZIP_DEFLATED) as stream:
        for i in range(21):
            stream.writestr(f"kushluk/module_{i}.py", "x = 1\n")
        stream.writestr("kushluk/templates/edition.html", "Synthetic")
        stream.writestr("kushluk-0.2.0a1.dist-info/licenses/LICENSE", "MIT")
        if extra_wheel:
            stream.writestr(extra_wheel, "External proprietary binary")
    with tarfile.open(sdist, mode="w:gz") as archive:
        def add(name, data=b"source content"):
            entry = tarfile.TarInfo(f"kushluk-0.2.0a1/{name}")
            entry.size = len(data)
            archive.addfile(entry, io.BytesIO(data))
        add("pyproject.toml")
        add("LICENSE")
        add("THIRD_PARTY_NOTICES.md")
        add("docs/PREVIEW_INSTALL.md")
        add("src/kushluk/cli.py")
        add("src/kushluk/templates/edition.html")
        if extra_sdist:
            add(extra_sdist)
    return wheel, sdist


def test_first_party_source_archive_is_allowed_for_alpha(tmp_path):
    wheel, sdist = packages(tmp_path)
    proof = inspect_archives(wheel, sdist)
    assert proof["status"] == "source_only_archive_gate_passed"
    assert proof["third_party_runtime_binary_signoff"] is False
    assert proof["pypi_publication_authorized"] is False
    assert proof["physical_print_verified"] is False


@pytest.mark.parametrize("member", [
    "kushluk/fonts/Arial.ttf",
    "kushluk/share/libpango.dylib",
    "kushluk/templates/sample.pdf",
    "outside/private.pem",
    "kushluk/assets/photo.webp",
])
def test_forbids_binary_font_pdf_and_private_wheel_assets(tmp_path, member):
    wheel, sdist = packages(tmp_path, extra_wheel=member)
    with pytest.raises(SourceScopeError):
        inspect_archives(wheel, sdist)


@pytest.mark.parametrize("member", [
    "src/kushluk/fonts/Calibri.otf",
    "docs/UNREVIEWED.md",
    "data/reader-archive.db",
    "src/kushluk/secret.env",
    "assets/screenshot.png",
])
def test_forbids_binary_assets_or_unreviewed_sdist_files(tmp_path, member):
    wheel, sdist = packages(tmp_path, extra_sdist=member)
    with pytest.raises(SourceScopeError):
        inspect_archives(wheel, sdist)


def test_source_scope_rejects_wrong_version_and_symlink(tmp_path):
    wheel, sdist = packages(tmp_path)
    renamed = tmp_path / "kushluk-0.1.0-py3-none-any.whl"
    renamed.write_bytes(wheel.read_bytes())
    with pytest.raises(SourceScopeError, match="version"):
        inspect_archives(renamed, sdist)
    alias = tmp_path / "alias.tar.gz"
    alias.symlink_to(sdist)
    with pytest.raises(SourceScopeError):
        inspect_archives(wheel, alias)
