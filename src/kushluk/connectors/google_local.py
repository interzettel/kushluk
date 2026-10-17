"""Explicit, locally authorized Google provider adapters. No hosted account proxy.

Separate gmail.metadata and tasks.readonly OAuth grants. The Gmail reader only
requests From, List-ID and internal date metadata; never reads message bodies.
Provider errors and tokens never enter printed editions or logs.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
import json
import os
from pathlib import Path
import re
import stat
import tempfile

from kushluk.models import PracticalItem, SourceRef
from kushluk.newsletter_discovery import discover_headers

_SCOPES = {
    "gmail": "https://www.googleapis.com/auth/gmail.metadata",
    "tasks": "https://www.googleapis.com/auth/tasks.readonly",
}
_ENDPOINTS = {
    "gmail": "https://gmail.googleapis.com/gmail/v1/users/me/messages",
    "tasks": "https://tasks.googleapis.com/tasks/v1",
}
MAX_RESPONSE_BYTES = 1_048_576


class GoogleProviderError(ValueError):
    """Public fixed reason code, with no raw Google error details."""


def _credential_path(vault: Path, provider: str) -> Path:
    if provider not in _SCOPES:
        raise GoogleProviderError("unknown_google_provider")
    if vault.is_symlink():
        raise GoogleProviderError("unsafe_provider_vault")
    return vault / (provider + "-token.json")


def _read_private(path: Path, limit: int = 32768) -> dict:
    try:
        if (path.is_symlink() or not path.is_file()
                or path.stat().st_size > limit
                or stat.S_IMODE(path.stat().st_mode) != 0o600):
            raise GoogleProviderError("unsafe_google_credentials")
        content = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(content, dict):
            raise GoogleProviderError("unsafe_google_credentials")
        return content
    except (OSError, ValueError, UnicodeError) as exc:
        raise GoogleProviderError("unsafe_google_credentials") from exc


def _write_private(path: Path, payload: dict) -> None:
    if path.parent.is_symlink() or path.is_symlink():
        raise GoogleProviderError("unsafe_provider_vault")
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".oauth-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as file:
            os.fchmod(file.fileno(), 0o600)
            json.dump(payload, file, sort_keys=True)
            file.write("\n")
            file.flush()
            os.fsync(file.fileno())
        os.replace(tmp, path)
    finally:
        Path(tmp).unlink(missing_ok=True)


def authorize(provider: str, *, oauth_client: Path, vault: Path) -> None:
    """Explicit desktop OAuth in a local browser; never invoked from a news item."""
    path = _credential_path(vault, provider)
    config = _read_private(oauth_client, limit=65536)
    if set(config) != {"installed"} or not isinstance(config["installed"], dict):
        raise GoogleProviderError("desktop_oauth_client_required")
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        flow = InstalledAppFlow.from_client_config(config, scopes=[_SCOPES[provider]])
        credentials = flow.run_local_server(port=0, open_browser=True)
        if set(credentials.scopes or ()) != {_SCOPES[provider]}:
            raise GoogleProviderError("oauth_scope_mismatch")
        _write_private(path, json.loads(credentials.to_json()))
    except ImportError as exc:
        raise GoogleProviderError("google_oauth_extra_required") from exc
    except GoogleProviderError:
        raise
    except Exception as exc:
        raise GoogleProviderError("google_oauth_authorization_failed") from exc


def _session(provider: str, vault: Path):
    path = _credential_path(vault, provider)
    payload = _read_private(path)
    scopes = payload.get("scopes")
    if not isinstance(scopes, list) or set(scopes) != {_SCOPES[provider]}:
        raise GoogleProviderError("oauth_scope_mismatch")
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import AuthorizedSession
        credentials = Credentials.from_authorized_user_info(
            payload, scopes=[_SCOPES[provider]],
        )
        if not credentials.valid and not credentials.refresh_token:
            raise GoogleProviderError("google_token_expired")
        return AuthorizedSession(credentials)
    except ImportError as exc:
        raise GoogleProviderError("google_oauth_extra_required") from exc
    except GoogleProviderError:
        raise
    except Exception as exc:
        raise GoogleProviderError("google_authentication_unavailable") from exc


def _get(session, url: str, params: dict | None = None) -> dict:
    """Bounded responses from a constant official endpoint, never user URLs."""
    if not (url.startswith(_ENDPOINTS["gmail"] + "/")
            or url == _ENDPOINTS["gmail"]
            or url.startswith(_ENDPOINTS["tasks"] + "/")):
        raise GoogleProviderError("unapproved_google_endpoint")
    try:
        response = session.get(
            url, params=params or {}, timeout=12, allow_redirects=False, stream=True,
        )
        try:
            if response.status_code != 200:
                raise GoogleProviderError("google_provider_unavailable")
            if int(response.headers.get("Content-Length", "0")) > MAX_RESPONSE_BYTES:
                raise GoogleProviderError("google_response_too_large")
            chunks = []
            length = 0
            for chunk in response.iter_content(chunk_size=65536):
                length += len(chunk)
                if length > MAX_RESPONSE_BYTES:
                    raise GoogleProviderError("google_response_too_large")
                chunks.append(chunk)
            data = json.loads(b"".join(chunks))
            if not isinstance(data, dict):
                raise GoogleProviderError("invalid_google_response")
            return data
        finally:
            response.close()
    except GoogleProviderError:
        raise
    except (OSError, ValueError, TypeError, UnicodeError) as exc:
        raise GoogleProviderError("google_provider_unavailable") from exc
    except Exception as exc:
        raise GoogleProviderError("google_provider_unavailable") from exc


def discover_gmail(vault: Path, *, days: int = 30, now: datetime | None = None,
                   session=None, max_messages: int = 100) -> dict:
    """Bounded recent Gmail metadata scan, never a claim of exhaustive discovery."""
    if type(days) is not int or not 1 <= days <= 60 or not 1 <= max_messages <= 100:
        raise GoogleProviderError("invalid_gmail_scan_bounds")
    session = session or _session("gmail", vault)
    base = _ENDPOINTS["gmail"]
    rows = []
    seen: set[str] = set()
    page_token = None
    scanned = 0
    partial = False
    reference = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    for _ in range(2):
        params = {"maxResults": min(50, max_messages - scanned),
                  "fields": "messages(id),nextPageToken"}
        if page_token:
            params["pageToken"] = page_token
        payload = _get(session, base, params)
        messages = payload.get("messages", [])
        if not isinstance(messages, list) or len(messages) > params["maxResults"]:
            raise GoogleProviderError("invalid_gmail_message_list")
        for row in messages:
            if not isinstance(row, dict) or not isinstance(row.get("id"), str):
                raise GoogleProviderError("invalid_gmail_message_list")
            message_id = row["id"]
            if not re.fullmatch(r"[A-Za-z0-9]{1,100}", message_id):
                raise GoogleProviderError("invalid_gmail_message_id")
            if message_id in seen:
                continue
            seen.add(message_id)
            scanned += 1
            message = _get(session, base + "/" + message_id, {
                "format": "metadata",
                "metadataHeaders": ["From", "List-ID", "Date"],
                "fields": "internalDate,payload(headers)",
            })
            try:
                timestamp = int(message["internalDate"]) / 1000
                stamp = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                headers = message["payload"]["headers"]
                if not isinstance(headers, list) or len(headers) > 60:
                    continue
                header_values = {
                    h["name"].lower(): h["value"] for h in headers
                    if isinstance(h, dict) and isinstance(h.get("name"), str)
                    and isinstance(h.get("value"), str)
                    and h["name"].lower() in {"from", "list-id"}
                }
            except (KeyError, TypeError, ValueError, OverflowError, OSError):
                continue
            if "from" in header_values and "list-id" in header_values:
                rows.append({
                    "sender": header_values["from"],
                    "date": stamp.isoformat(), "list_id": header_values["list-id"],
                    "subject": "",  # Subject and message body never requested.
                })
            if scanned >= max_messages:
                break
        token = payload.get("nextPageToken")
        if token is not None and (not isinstance(token, str) or len(token) > 512):
            raise GoogleProviderError("invalid_gmail_page_token")
        page_token = token
        if not token or scanned >= max_messages:
            partial = bool(token)
            break
    else:
        partial = bool(page_token)
    return {
        "sources": discover_headers(rows, days=days, now=reference),
        "scanned_messages": scanned, "partial_scan": partial,
        "ingestion_enabled": False, "provider": "gmail-metadata",
    }


def fetch_google_tasks(vault: Path, *, target_date: date, session=None,
                       max_lists: int = 3) -> list[PracticalItem]:
    """Read-only Tasks API, bounded lists and tasks; no mutation or body export."""
    if not 1 <= max_lists <= 3:
        raise GoogleProviderError("invalid_task_scan_bounds")
    session = session or _session("tasks", vault)
    base = _ENDPOINTS["tasks"]
    lists = _get(session, base + "/users/@me/lists", {"maxResults": max_lists, "fields": "items(id),nextPageToken"})
    entries = lists.get("items", [])
    if not isinstance(entries, list) or len(entries) > max_lists:
        raise GoogleProviderError("invalid_task_list_response")
    found: list[tuple[str, str, str]] = []
    for task_list in entries:
        if not isinstance(task_list, dict) or not isinstance(task_list.get("id"), str):
            raise GoogleProviderError("invalid_task_list_response")
        # Google task list IDs are opaque. URL path segment must be safely encoded.
        from urllib.parse import quote
        list_id = task_list["id"]
        if len(list_id) > 150 or not list_id:
            raise GoogleProviderError("invalid_task_list_response")
        url = base + "/lists/" + quote(list_id, safe="") + "/tasks"
        data = _get(session, url, {
            "maxResults": 50, "showCompleted": "false", "showDeleted": "false",
            "showHidden": "false",
            "fields": "items(id,title,due,status),nextPageToken",
        })
        if not isinstance(data.get("items", []), list):
            raise GoogleProviderError("invalid_task_page")
        for row in data.get("items", [])[:50]:
            if not isinstance(row, dict) or row.get("status") != "needsAction":
                continue
            title, due = row.get("title"), row.get("due")
            if not isinstance(title, str) or not isinstance(due, str):
                continue
            try:
                day = date.fromisoformat(due[:10])
            except ValueError:
                continue
            if not 1 <= len(title.strip()) <= 140 or day > target_date:
                continue
            uid = row.get("id", "")
            if not isinstance(uid, str):
                continue
            found.append((day.isoformat(), uid[:100], " ".join(title.split())))
    found.sort(key=lambda item: (item[0], item[1]))
    return [
        PracticalItem(
            label="Task" if due == target_date.isoformat() else "Overdue task",
            value=title, source=SourceRef(kind="task", name="Google Tasks (read-only)"),
        ) for due, _id, title in found[:6]
    ]


def disconnect(provider: str, *, vault: Path) -> None:
    """Delete local token only. Remote Google revocation must be done in Google settings."""
    path = _credential_path(vault, provider)
    if path.is_symlink():
        raise GoogleProviderError("unsafe_google_credentials")
    if path.exists():
        _read_private(path)  # Reject an unsafe file rather than following it.
        try:
            path.unlink()
        except OSError as exc:
            raise GoogleProviderError("google_disconnect_failed") from exc
