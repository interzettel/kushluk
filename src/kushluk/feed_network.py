"""Bounded RSS fetch with pinned public DNS addresses and manual safe redirects.

No proxies, private/link-local/loopback targets, DNS rebinding between check and
connection, embedded credentials, unbounded responses, or HTTPS downgrade.
Not a sandbox for user-supplied content: keep the reader-only source policy too.
"""
from __future__ import annotations

from http.client import HTTPConnection, HTTPSConnection
from ipaddress import ip_address
import socket
import ssl
from urllib.parse import urljoin, urlsplit


class FeedNetworkError(ValueError):
    """Deliberately generic: private subscription URLs must never enter logs."""


_MAX_BYTES = 1_048_576
_MAX_REDIRECTS = 3
_TIMEOUT = 12


def _target(value: str, *, previous_scheme: str | None = None) -> tuple:
    if not isinstance(value, str) or len(value) > 2048 or any(
        ord(ch) < 32 or ch.isspace() for ch in value
    ):
        raise FeedNetworkError("Invalid feed URL")
    try:
        parts = urlsplit(value)
        host = parts.hostname
        port = parts.port
    except ValueError as exc:
        raise FeedNetworkError("Invalid feed URL") from exc
    scheme = parts.scheme.lower()
    if (scheme not in {"https", "http"} or not host
            or parts.username is not None or parts.password is not None
            or parts.fragment
            or (previous_scheme == "https" and scheme != "https")):
        raise FeedNetworkError("Unsafe feed target or redirect")
    expected_port = 443 if scheme == "https" else 80
    if port is not None and port != expected_port:
        raise FeedNetworkError("Nonstandard feed ports are not supported")
    host = host.rstrip(".").lower()
    if (not host or host.endswith(
        (".localhost", ".local", ".internal", ".test", ".invalid", ".onion")
    ) or host in {"localhost", "metadata.google.internal"}):
        raise FeedNetworkError("Non-public feed host")
    try:
        literal = ip_address(host)
    except ValueError:
        literal = None
    if literal is None:
        if "." not in host or len(host) > 253:
            raise FeedNetworkError("Non-public feed host")
        try:
            ascii_host = host.encode("idna").decode("ascii")
        except UnicodeError as exc:
            raise FeedNetworkError("Invalid feed hostname") from exc
        if any(
            not label or len(label) > 63 or label.startswith("-")
            or label.endswith("-") or not all(
                char.isascii() and (char.isalnum() or char == "-")
                for char in label
            ) for label in ascii_host.split(".")
        ):
            raise FeedNetworkError("Invalid feed hostname")
        host = ascii_host
    elif not literal.is_global:
        raise FeedNetworkError("Non-public feed IP address")
    target = parts.path or "/"
    if parts.query:
        target += "?" + parts.query
    return scheme, host, expected_port, target


def _public_ip(host: str, port: int) -> str:
    try:
        records = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
        addresses = [record[4][0] for record in records]
    except (OSError, ValueError) as exc:
        raise FeedNetworkError("Feed hostname could not be resolved") from exc
    if not addresses:
        raise FeedNetworkError("Feed host has no address records")
    try:
        parsed = [ip_address(address) for address in addresses]
    except ValueError as exc:
        raise FeedNetworkError("Invalid resolved IP address") from exc
    # Fail the entire answer set, never silently choose only a public result.
    if not all(ip.is_global for ip in parsed):
        raise FeedNetworkError("Feed resolved to a non-public IP address")
    return addresses[0]


class _PublicHTTP(HTTPConnection):
    def __init__(self, host: str, address: str, port: int):
        super().__init__(host, port=port, timeout=_TIMEOUT)
        self._pinned = address

    def connect(self) -> None:
        self.sock = socket.create_connection((self._pinned, self.port), self.timeout)


class _PublicHTTPS(HTTPSConnection):
    def __init__(self, host: str, address: str, port: int):
        super().__init__(
            host, port=port, timeout=_TIMEOUT, context=ssl.create_default_context()
        )
        self._pinned = address

    def connect(self) -> None:
        # TLS verifies the *original hostname*, not the pinned numeric IP.
        raw = socket.create_connection((self._pinned, self.port), self.timeout)
        try:
            self.sock = self._context.wrap_socket(raw, server_hostname=self.host)
        except BaseException:
            raw.close()
            raise


def fetch_public_xml(url: str) -> bytes:
    """Fetch one permitted RSS XML response; reject unsafe redirects and large feeds."""
    current = url
    previous_scheme = None
    for redirect in range(_MAX_REDIRECTS + 1):
        scheme, host, port, target = _target(
            current, previous_scheme=previous_scheme
        )
        address = _public_ip(host, port)
        conn = (_PublicHTTPS if scheme == "https" else _PublicHTTP)(host, address, port)
        try:
            conn.request("GET", target, headers={
                "User-Agent": "Kushluk/0.1 (+https://github.com/interzettel/kushluk)",
                "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml",
                "Accept-Encoding": "identity",
                "Connection": "close",
            })
            response = conn.getresponse()
            if response.status in {301, 302, 303, 307, 308}:
                location = response.getheader("Location")
                if not location or redirect >= _MAX_REDIRECTS:
                    raise FeedNetworkError("Feed redirect limit or missing destination")
                previous_scheme = scheme
                current = urljoin(current, location)
                continue
            if response.status != 200:
                raise FeedNetworkError("Feed server returned an unsuccessful status")
            raw_length = response.getheader("Content-Length")
            if raw_length:
                try:
                    if int(raw_length) > _MAX_BYTES:
                        raise FeedNetworkError("Feed response exceeds 1 MiB")
                except ValueError as exc:
                    raise FeedNetworkError("Invalid feed content length") from exc
            if (response.getheader("Content-Encoding") or "identity").lower() != "identity":
                raise FeedNetworkError("Compressed feeds are not enabled")
            payload = response.read(_MAX_BYTES + 1)
            if len(payload) > _MAX_BYTES:
                raise FeedNetworkError("Feed response exceeds 1 MiB")
            return payload
        except (OSError, ssl.SSLError) as exc:
            raise FeedNetworkError("Feed connection failed") from exc
        finally:
            conn.close()
    raise FeedNetworkError("Too many feed redirects")
