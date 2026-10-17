from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from kushluk.local_profile import read_local_profile
from kushluk.source_registry import approved_urls


@dataclass(slots=True)
class Settings:
    home_name: str = "Cologne"
    latitude: float = 50.9384
    longitude: float = 6.9603
    timezone: str = "Europe/Berlin"
    rss_urls: tuple[str, ...] = ("https://hnrss.org/frontpage",)
    reference_only_rss_urls: tuple[str, ...] = ()
    archive_dir: Path = Path("archive")
    output_dir: Path = Path("output")
    media_dir: Path | None = None  # No media loaded without deliberate local opt-in.
    calendar_ics: str | None = None
    calendar_fixture: Path = Path("fixtures/calendar.json")
    tasks_file: Path | None = None
    research_query: str | None = None
    printer: str | None = None
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from: str | None = None
    email_to: str | None = None
    smtp_starttls: bool = True

    @property
    def email_configured(self) -> bool:
        return bool(self.smtp_host and self.smtp_from and self.email_to)

    @classmethod
    def from_env(cls) -> "Settings":
        # A configured registry is a deliberately approved source list.
        # Legacy explicit KUSHLUK_RSS_URLS remains supported, but no default
        # Hacker News feed is silently added to a registry-backed profile.
        profile = read_local_profile()
        registry = approved_urls()
        raw_urls = os.getenv("KUSHLUK_RSS_URLS")
        if raw_urls is None:
            # Guided first-run profiles imply deliberate source consent:
            # never insert the historical Hacker News example before a user
            # approves a feed. Older no-profile installations keep their
            # original example feed unless a registry exists.
            rss = registry or (
                ("https://hnrss.org/frontpage",)
                if not _has_source_registry() and not profile else ()
            )
        else:
            legacy = tuple(part.strip() for part in raw_urls.split(",") if part.strip())
            rss = tuple(dict.fromkeys((*legacy, *registry)))
        return cls(
            home_name=os.getenv("KUSHLUK_HOME_NAME", profile.get("home_name", "Cologne")),
            latitude=float(os.getenv("KUSHLUK_LATITUDE", profile.get("latitude", 50.9384))),
            longitude=float(os.getenv("KUSHLUK_LONGITUDE", profile.get("longitude", 6.9603))),
            timezone=os.getenv("KUSHLUK_TIMEZONE", profile.get("timezone", "Europe/Berlin")),
            rss_urls=rss,
            reference_only_rss_urls=rss,
            archive_dir=Path(os.getenv("KUSHLUK_ARCHIVE_DIR", "archive")),
            output_dir=Path(os.getenv("KUSHLUK_OUTPUT_DIR", "output")),
            media_dir=Path(os.environ["KUSHLUK_MEDIA_DIR"]) if os.getenv("KUSHLUK_MEDIA_DIR") else None,
            calendar_ics=os.getenv("KUSHLUK_CALENDAR_ICS") or None,
            calendar_fixture=Path(
                os.getenv("KUSHLUK_CALENDAR_FIXTURE", "fixtures/calendar.json")
            ),
            tasks_file=Path(os.environ["KUSHLUK_TASKS_FILE"]) if os.getenv("KUSHLUK_TASKS_FILE") else None,
            research_query=os.getenv("KUSHLUK_RESEARCH_QUERY") or None,
            printer=(
                (os.environ["KUSHLUK_PRINTER"] or None)
                if "KUSHLUK_PRINTER" in os.environ
                else (profile.get("printer") or None)
            ),
            smtp_host=os.getenv("KUSHLUK_SMTP_HOST") or None,
            smtp_port=int(os.getenv("KUSHLUK_SMTP_PORT", "587")),
            smtp_username=os.getenv("KUSHLUK_SMTP_USERNAME") or None,
            smtp_password=os.getenv("KUSHLUK_SMTP_PASSWORD") or None,
            smtp_from=os.getenv("KUSHLUK_SMTP_FROM") or None,
            email_to=os.getenv("KUSHLUK_EMAIL_TO") or None,
            smtp_starttls=_env_bool("KUSHLUK_SMTP_STARTTLS", True),
        )


def _has_source_registry() -> bool:
    from kushluk.source_registry import registry_path
    return registry_path().exists()


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}
