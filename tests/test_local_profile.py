"""First-run home profile is local/private, reversible by editing one's own file."""
import json
import os

import pytest

from kushluk.cli import main
from kushluk.config import Settings
from kushluk.local_profile import (
    LocalProfileError, read_local_profile, update_local_printer,
    update_local_paper_size, write_local_profile,
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
    assert profile["paper_size"] == "a4"
    cfg = Settings.from_env()
    assert cfg.home_name == "My Home"
    assert cfg.longitude == 6.7735
    assert cfg.timezone == "Europe/Berlin"
    assert cfg.paper_size == "a4"
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
    {"paper_size": "tabloid"},
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


def test_explicit_printer_preference_preserves_profile_and_mode(tmp_path):
    path = tmp_path / "profile.json"
    write_local_profile(path, **_params())
    old = read_local_profile(path)
    update_local_printer(path, printer="DeskJet_2820e")
    new = read_local_profile(path)
    assert {**new, "printer": None} == old
    assert new["printer"] == "DeskJet_2820e"
    assert path.stat().st_mode & 0o777 == 0o600
    assert list(tmp_path.glob(".profile-*")) == []
    update_local_printer(path, printer="DeskJet_2820e")
    assert read_local_profile(path) == new


def test_printer_update_cannot_create_or_follow_symlinks_or_weak_permissions(tmp_path):
    missing = tmp_path / "missing.json"
    with pytest.raises(LocalProfileError):
        update_local_printer(missing, printer="Queue_A")
    assert not missing.exists()
    target = tmp_path / "real.json"
    write_local_profile(target, **_params())
    link = tmp_path / "link.json"
    link.symlink_to(target)
    with pytest.raises(LocalProfileError):
        update_local_printer(link, printer="Queue_A")
    assert read_local_profile(target)["printer"] is None
    target.chmod(0o644)
    with pytest.raises(LocalProfileError, match="owner-only"):
        update_local_printer(target, printer="Queue_A")
    assert read_local_profile(target)["printer"] is None


def test_invalid_printer_update_never_rewrites_existing_profile(tmp_path):
    path = tmp_path / "profile.json"
    write_local_profile(path, **_params())
    original = path.read_bytes()
    for value in ("", "injected\nqueue", "x" * 121):
        with pytest.raises(LocalProfileError):
            update_local_printer(path, printer=value)
    assert path.read_bytes() == original


def test_legacy_v1_profile_without_paper_size_reads_as_a4(tmp_path, monkeypatch):
    path = tmp_path / "existing.json"
    path.write_text(json.dumps({"schema_version": 1, **_params()}))
    monkeypatch.setenv("KUSHLUK_PROFILE_FILE", str(path))
    monkeypatch.delenv("KUSHLUK_PAPER_SIZE", raising=False)
    assert read_local_profile(path)["paper_size"] == "a4"
    assert Settings.from_env().paper_size == "a4"
    assert "paper_size" not in json.loads(path.read_text())


def test_letter_selection_and_explicit_preference_change(tmp_path, monkeypatch):
    path = tmp_path / "profile.json"
    write_local_profile(path, **_params(), paper_size="letter")
    monkeypatch.setenv("KUSHLUK_PROFILE_FILE", str(path))
    monkeypatch.delenv("KUSHLUK_PAPER_SIZE", raising=False)
    assert Settings.from_env().paper_size == "letter"
    original = read_local_profile(path)
    update_local_paper_size(path, paper_size="a4")
    current = read_local_profile(path)
    assert current["paper_size"] == "a4"
    assert {**current, "paper_size": "letter"} == original
    assert path.stat().st_mode & 0o777 == 0o600
    assert not list(tmp_path.glob(".profile-*"))
    unchanged = path.read_bytes()
    for rejected in ("Letter", "a3", "", "custom", None):
        with pytest.raises(LocalProfileError):
            update_local_paper_size(path, paper_size=rejected)
        assert path.read_bytes() == unchanged


def test_paper_env_override_is_validated(tmp_path, monkeypatch):
    path = tmp_path / "profile.json"
    write_local_profile(path, **_params(), paper_size="letter")
    monkeypatch.setenv("KUSHLUK_PROFILE_FILE", str(path))
    monkeypatch.setenv("KUSHLUK_PAPER_SIZE", "a4")
    assert Settings.from_env().paper_size == "a4"
    monkeypatch.setenv("KUSHLUK_PAPER_SIZE", "custom")
    with pytest.raises(ValueError, match="KUSHLUK_PAPER_SIZE"):
        Settings.from_env()


def test_cli_setup_letter_is_explicit_and_never_prints(tmp_path, monkeypatch, capsys):
    path = tmp_path / "profile.json"
    monkeypatch.setenv("KUSHLUK_PROFILE_FILE", str(path))
    monkeypatch.setattr("kushluk.printing.print_pdf",
                        lambda *a, **kw: pytest.fail("No printing in setup"))
    assert main([
        "setup", "--home-name", "Example", "--latitude", "40.0",
        "--longitude", "-74.0", "--timezone", "America/New_York",
        "--paper-size", "letter", "--non-interactive",
    ]) == 0
    assert read_local_profile(path)["paper_size"] == "letter"
    reply = json.loads(capsys.readouterr().out)
    assert reply["contacts_network"] is False
    assert reply["source_permissions_modified"] is False
