"""The installed module must physically reside in the isolated venv on all OSes."""
from pathlib import Path

from tools.release_check import _installed_inside_venv


def test_resolves_macos_style_symlink_alias_for_true_venv(tmp_path):
    real = tmp_path / "private" / "var" / "trial" / "venv"
    installed = real / "lib" / "python3.12" / "site-packages" / "kushluk" / "__init__.py"
    installed.parent.mkdir(parents=True)
    installed.write_text("")
    alias = tmp_path / "var"
    alias.symlink_to(tmp_path / "private" / "var", target_is_directory=True)
    aliased_module = alias / "trial" / "venv" / "lib" / "python3.12" / (
        "site-packages"
    ) / "kushluk" / "__init__.py"
    assert str(aliased_module) != str(installed)
    assert _installed_inside_venv(str(aliased_module), real) is True
    assert _installed_inside_venv(str(installed), alias / "trial" / "venv") is True


def test_refuses_venv_sibling_prefix_and_site_packages_outside(tmp_path):
    venv = tmp_path / "venv"
    venv.mkdir()
    wrong = tmp_path / "venv-not-the-same" / "lib" / "site-packages" / "pkg.py"
    wrong.parent.mkdir(parents=True)
    wrong.write_text("v1")
    assert _installed_inside_venv(str(wrong), venv) is False
    within_but_not_installed = venv / "script.py"
    within_but_not_installed.write_text("v2")
    assert _installed_inside_venv(str(within_but_not_installed), venv) is False
    assert _installed_inside_venv(str(venv / "missing.py"), venv) is False
    assert _installed_inside_venv(str(Path("~/.config/secret").expanduser()), venv) is False
