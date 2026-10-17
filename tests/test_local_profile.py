"""First-run home profile is local/private, reversible by editing one's own file."""
import json
import os

import pytest

from kushluk.cli import main
from kushluk.config import Settings
from kushluk.local_profile import (
    LocalProfileError, read_local_profile, write_local_profile,
)


def _params():
    return dict(
        home_name="My Home",
        latitude=51.2277,
        longitude=6.7735,
        timezone="Europe/Berlin",
        printer=None,
    )


def test_profile_round_trip_and_env_override(tmp_path, monkeypatch):
    path = tmp_path / "private" / "profile.json"
    monkeypatch.setenv("KUSHLUK_PROFILE_FILE", str(path))
    for key in ("KUSHLUK_HOME_NAME", "KUSHLUK_LATITUDE", "KUSHLUK_LONGITUDE",
                "KUSHLUK_TIMEZONE", "KUSHLUK_PRINTER"):
        monkeypatch.delenv(key, raising=False)
    write_local_profile(path, **_params())
    profile = read_local_profile(path)
    assert profile["schema_version"] == 1
    assert profile["latitude"] == 51.2277
    cfg = Settings.from_env()
    assert cfg.home_name == "My Home"
    assert cfg.longitude == 6.7735
    assert cfg.timezone == "Europe/Berlin"
    if os.name != "nt":
        assert path.stat().st_mode & 0o777 == 0o600

    monkeypatch.setenv("KUSHLUK_HOME_NAME", "Explicitly overridden")
    monkeypatch.setenv("KUSHLUK_LATITUDE", "52.52")
    assert Settings.from_env().home_name == "Explicitly overridden"
    assert Settings.from_env().latitude == 52.52


def test_setup_cli_noninteractive_never_fetches_or_exposes_coordinates(
        tmp_path, monkeypatch, capsys):
    path = tmp_path / "profile.json"
    monkeypatch.setenv("KUSHLUK_PROFILE_FILE", str(path))
    monkeypatch.setattr("builtins.input", lambda _: pytest.fail("unexpected prompt"))
    args = [
        "setup", "--home-name", "Personal Home", "--latitude", "40.0",
        "--longitude", "-74.5", "--timezone", "America/New_York",
        "--non-interactive",
    ]
    assert main(args) == 0
    reply = json.loads(capsys.readouterr().out)
    assert reply["status"] == "local_profile_created"
    assert reply["contacts_network"] is False
    assert reply["contains_credentials"] is False
    assert "40.0" not in json.dumps(reply)
    assert read_local_profile(path)["timezone"] == "America/New_York"
    original = path.read_bytes()
    assert main(args) == 2
    assert json.loads(capsys.readouterr().out)["status"] == "rejected"
    assert path.read_bytes() == original


def test_setup_guided_prompts_for_only_required_values(tmp_path, monkeypatch, capsys):
    path = tmp_path / "guided.json"
    monkeypatch.setenv("KUSHLUK_PROFILE_FILE", str(path))
    items = iter(["Local display name", "48.13", "11.58", "Europe/Berlin"])
    monkeypatch.setattr("builtins.input", lambda _: next(items))
    assert main(["setup"]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "local_profile_created"
    assert read_local_profile(path)["home_name"] == "Local display name"


@pytest.mark.parametrize("overrides", [
    {"latitude": 91.0},
    {"latitude": -91.0},
    {"longitude": 181.0},
    {"longitude": -181.0},
    {"home_name": "\x00secret"},
    {"home_name": ""},
    {"timezone": "Not/A-Timezone"},
    {"printer": "queue\nInjected"},
    {"latitude": float("nan")},
    {"longitude": float("inf")},
])
def test_reject_invalid_profile_without_creating_file(tmp_path, overrides):
    options = _params()
    options.update(overrides)
    path = tmp_path / "invalid.json"
    with pytest.raises(LocalProfileError):
        write_local_profile(path, **options)
    assert not path.exists()


def test_invalid_manual_profile_is_not_silently_accepted(tmp_path, monkeypatch):
    path = tmp_path / "profile.json"
    path.write_text(json.dumps({
        "schema_version": 1, **_params(), "smtp_password": "SHOULD_NOT_BE_STORED"
    }))
    monkeypatch.setenv("KUSHLUK_PROFILE_FILE", str(path))
    with pytest.raises(LocalProfileError, match="schema"):
        Settings.from_env()


def test_profile_file_symlink_rejected(tmp_path):
    a = tmp_path / "real.json"
    write_local_profile(a, **_params())
    b = tmp_path / "symlink.json"
    b.symlink_to(a)
    with pytest.raises(LocalProfileError):
        read_local_profile(b)


def test_setup_needs_explicit_values_in_noninteractive_mode(tmp_path, monkeypatch, capsys):
    path = tmp_path / "new.json"
    monkeypatch.setenv("KUSHLUK_PROFILE_FILE", str(path))
    assert main(["setup", "--home-name", "No location", "--non-interactive"]) == 2
    assert not path.exists()
    assert json.loads(capsys.readouterr().out)["status"] == "rejected"


def test_no_profile_preserves_legacy_behavior(tmp_path, monkeypatch):
    path = tmp_path / "does-not-exist.json"
    monkeypatch.setenv("KUSHLUK_PROFILE_FILE", str(path))
    for key in ("KUSHLUK_HOME_NAME", "KUSHLUK_LATITUDE",
                "KUSHLUK_LONGITUDE", "KUSHLUK_TIMEZONE"):
        monkeypatch.delenv(key, raising=False)
    cfg = Settings.from_env()
    assert cfg.home_name == "Cologne"
    assert cfg.latitude == 50.9384
    assert cfg.timezone == "Europe/Berlin"


def test_explicit_empty_printer_env_can_disable_saved_printer(tmp_path, monkeypatch):
    path = tmp_path / "profile.json"
    write_local_profile(path, **{**_params(), "printer": "My Printer"})
    monkeypatch.setenv("KUSHLUK_PROFILE_FILE", str(path))
    monkeypatch.delenv("KUSHLUK_PRINTER", raising=False)
    assert Settings.from_env().printer == "My Printer"
    monkeypatch.setenv("KUSHLUK_PRINTER", "")
    assert Settings.from_env().printer is None
