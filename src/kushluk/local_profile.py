"""Private, offline first-run profile. No credentials, feeds or article content.

Simple owner-visible setup data is separate from source permissions and from
environment-managed secrets. Existing environment variables always win.
"""
from __future__ import annotations

import json
import math
import os
import stat
import tempfile
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class LocalProfileError(ValueError):
    """Fail closed without echoing private location or input content."""


_FIELDS = frozenset({
    "schema_version", "home_name", "latitude", "longitude", "timezone", "printer",
})
_MAX_BYTES = 8192


def profile_path() -> Path:
    override = os.getenv("KUSHLUK_PROFILE_FILE")
    if override:
        return Path(override).expanduser()
    base = Path(os.getenv("XDG_CONFIG_HOME", str(Path.home() / ".config")))
    return base / "kushluk" / "profile.json"


def _validate(data: object) -> dict:
    if not isinstance(data, dict) or set(data) != _FIELDS or data.get("schema_version") != 1:
        raise LocalProfileError("Unsupported local profile schema")
    name = data["home_name"]
    if (not isinstance(name, str) or not name.strip() or len(name) > 120
            or any(ord(c) < 32 for c in name)):
        raise LocalProfileError("Home label must be 1–120 printable characters")
    for field, lower, upper in (
        ("latitude", -90, 90), ("longitude", -180, 180),
    ):
        number = data[field]
        if type(number) not in {float, int} or not math.isfinite(number) or not lower <= number <= upper:
            raise LocalProfileError("Location coordinates are outside valid ranges")
    zone = data["timezone"]
    if not isinstance(zone, str) or not zone or len(zone) > 100:
        raise LocalProfileError("A valid IANA timezone is required")
    try:
        ZoneInfo(zone)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise LocalProfileError("Unknown IANA timezone") from exc
    printer = data["printer"]
    if (printer is not None and
            (not isinstance(printer, str) or len(printer) > 120
             or any(ord(c) < 32 for c in printer))):
        raise LocalProfileError("Printer queue name is invalid")
    return {
        "schema_version": 1,
        "home_name": name.strip(),
        "latitude": float(data["latitude"]),
        "longitude": float(data["longitude"]),
        "timezone": zone,
        "printer": printer,
    }


def read_local_profile(path: Path | None = None) -> dict:
    path = path or profile_path()
    if not path.exists() and not path.is_symlink():
        return {}
    if path.is_symlink() or not path.is_file():
        raise LocalProfileError("Local profile must be a regular private file")
    try:
        with path.open("rb") as stream:
            data = stream.read(_MAX_BYTES + 1)
        if len(data) > _MAX_BYTES:
            raise LocalProfileError("Local profile exceeds the size limit")
        parsed = json.loads(data)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LocalProfileError("Could not read a valid local profile") from exc
    return _validate(parsed)


def write_local_profile(path: Path, *, home_name: str, latitude: float,
                        longitude: float, timezone: str,
                        printer: str | None = None) -> None:
    checked = _validate({
        "schema_version": 1, "home_name": home_name,
        "latitude": latitude, "longitude": longitude,
        "timezone": timezone, "printer": printer,
    })
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    payload = (json.dumps(checked, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise LocalProfileError("Local profile already exists; no overwrite") from exc
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def update_local_printer(path: Path, *, printer: str) -> None:
    """Change only the queue in an existing private profile, by explicit action.

    The initial profile remains create-only. Reject symlinks and non-private
    files; atomically replace the checked file without in-place truncation.
    This stores a preference, never a permission to submit a print job.
    """
    current = read_local_profile(path)
    if not current:
        raise LocalProfileError("Create a local profile before saving a printer")
    checked = _validate({**current, "printer": printer})
    if not printer:
        raise LocalProfileError("A discovered printer queue must be selected")
    try:
        before = path.lstat()
    except OSError as exc:
        raise LocalProfileError("Local profile is not available") from exc
    if not stat.S_ISREG(before.st_mode) or before.st_mode & 0o077:
        raise LocalProfileError("Local profile must be an owner-only regular file")
    if current["printer"] == printer:
        return
    payload = (json.dumps(checked, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    filename = None
    try:
        fd, filename = tempfile.mkstemp(prefix=".profile-", suffix=".tmp", dir=str(path.parent))
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        after = path.lstat()
        if (not stat.S_ISREG(after.st_mode) or after.st_ino != before.st_ino
                or after.st_dev != before.st_dev or after.st_mtime_ns != before.st_mtime_ns
                or after.st_size != before.st_size or after.st_mode & 0o077):
            raise LocalProfileError("Local profile changed during printer selection")
        os.replace(filename, path)
    finally:
        if filename is not None:
            try:
                os.unlink(filename)
            except FileNotFoundError:
                pass
