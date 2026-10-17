"""New guided setups must not silently retrieve a sample RSS publisher."""
from kushluk.config import Settings
from kushluk.local_profile import write_local_profile
from kushluk.opml import parse_opml, write_proposal
from kushluk.source_registry import approve_source, set_source_mode


def test_profile_creation_disables_implicit_sample_until_per_feed_approval(
        tmp_path, monkeypatch):
    profile = tmp_path / "profile.json"
    registry = tmp_path / "approved-sources.json"
    monkeypatch.setenv("KUSHLUK_PROFILE_FILE", str(profile))
    monkeypatch.setenv("KUSHLUK_SOURCE_REGISTRY", str(registry))
    monkeypatch.delenv("KUSHLUK_RSS_URLS", raising=False)

    # Preserve previous behavior for users without any setup/registry.
    assert Settings.from_env().rss_urls == ("https://hnrss.org/frontpage",)

    write_local_profile(
        profile, home_name="Reader's Home",
        latitude=50.0, longitude=7.0, timezone="Europe/Berlin",
    )
    assert Settings.from_env().rss_urls == ()
    assert Settings.from_env().reference_only_rss_urls == ()
    assert not registry.exists()

    # A preview alone must not change the list of executable feeds.
    proposal = tmp_path / "proposal.json"
    write_proposal(proposal, parse_opml(
        b'<opml version="2.0"><body>'
        b'<outline text="My permitted feed" xmlUrl="https://example.org/feed"/>'
        b'</body></opml>'
    ))
    assert Settings.from_env().rss_urls == ()
    identifier, _, _ = approve_source(
        proposal, 1, acknowledge=True, path=registry,
    )
    assert len(identifier) == 20
    assert Settings.from_env().rss_urls == ("https://example.org/feed",)

    set_source_mode(identifier, "ignore", path=registry)
    assert Settings.from_env().rss_urls == ()
    assert Settings.from_env().reference_only_rss_urls == ()


def test_existing_explicit_configuration_remains_authoritative(tmp_path, monkeypatch):
    monkeypatch.setenv("KUSHLUK_PROFILE_FILE", str(tmp_path / "profile.json"))
    monkeypatch.setenv("KUSHLUK_SOURCE_REGISTRY", str(tmp_path / "sources.json"))
    write_local_profile(
        tmp_path / "profile.json",
        home_name="Local", latitude=48.0, longitude=11.0, timezone="Europe/Berlin",
    )
    monkeypatch.setenv("KUSHLUK_RSS_URLS", "https://reader.example.net/express")
    assert Settings.from_env().rss_urls == ("https://reader.example.net/express",)
    assert Settings.from_env().reference_only_rss_urls == Settings.from_env().rss_urls


def test_old_registry_path_still_blocks_fallback_even_without_profile(
        tmp_path, monkeypatch):
    monkeypatch.setenv("KUSHLUK_PROFILE_FILE", str(tmp_path / "missing-profile"))
    registry = tmp_path / "approved-sources.json"
    monkeypatch.setenv("KUSHLUK_SOURCE_REGISTRY", str(registry))
    monkeypatch.delenv("KUSHLUK_RSS_URLS", raising=False)
    registry.write_text('{"version": 1, "sources": []}')
    assert Settings.from_env().rss_urls == ()
