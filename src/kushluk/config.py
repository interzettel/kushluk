from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

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
    calendar_ics: str | None = None
    calendar_fixture: Path = Path("fixtures/calendar.json")
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
        registry = approved_urls()
        raw_urls = os.getenv("KUSHLUK_RSS_URLS")
        if raw_urls is None:
            rss = registry or (("https://hnrss.org/frontpage",) if not
                               _has_source_registry() else ())
        else:
            legacy = tuple(part.strip() for part in raw_urls.split(",") if part.strip())
            rss = tuple(dict.fromkeys((*legacy, *registry)))
        return cls(
            home_name=os.getenv("KUSHLUK_HOME_NAME", "Cologne"),
            latitude=float(os.getenv("KUSHLUK_LATITUDE", "50.9384")),
            longitude=float(os.getenv("KUSHLUK_LONGITUDE", "6.9603")),
            timezone=os.getenv("KUSHLUK_TIMEZONE", "Europe/Berlin"),
            rss_urls=rss,
            reference_only_rss_urls=registry,
            archive_dir=Path(os.getenv("KUSHLUK_ARCHIVE_DIR", "archive")),
            output_dir=Path(os.getenv("KUSHLUK_OUTPUT_DIR", "output")),
            calendar_ics=os.getenv("KUSHLUK_CALENDAR_ICS") or None,
            calendar_fixture=Path(
                os.getenv("KUSHLUK_CALENDAR_FIXTURE", "fixtures/calendar.json")
            ),
            printer=os.getenv("KUSHLUK_PRINTER") or None,
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
