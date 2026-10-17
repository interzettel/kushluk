"""Feed egress security: deny RFC1918/metadata/redirect/rebinding, bound XML."""
import socket
import pytest

from kushluk import feed_network as network
from kushluk.connectors import rss


@pytest.mark.parametrize("url", [
    "http://127.0.0.1/feed",
    "http://10.12.0.5/latest",
    "https://169.254.169.254/latest/meta-data",
    "http://192.168.1.1/",
    "https://[::1]/",
    "http://localhost/feed",
    "https://news.local/rss",
    "https://metadata.google.internal/latest",
    "https://u:pass@example.com/atom.xml",
    "file:///etc/passwd",
    "https://example.com:8443/rss",
    "https://example.com/rss#fragment",
])
def test_refuse_private_and_unsafe_urls_before_dns(url):
    with pytest.raises(network.FeedNetworkError):
        network._target(url)


def test_public_ip_is_dns_pinned_and_mixed_answers_fail(monkeypatch):
    seen = []

    def resolve(_host, _port, **kwargs):
        seen.append(kwargs)
        return [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443)),
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.0.0.1", 443)),
        ]

    monkeypatch.setattr(network.socket, "getaddrinfo", resolve)
    with pytest.raises(network.FeedNetworkError, match="non-public"):
        network._public_ip("example.org", 443)
    assert seen[0]["type"] == socket.SOCK_STREAM


def test_http_connect_uses_pinned_ip_and_never_resolves_host_again(monkeypatch):
    called = []

    class DummySocket:
        def close(self):
            pass

    def connect(target, timeout):
        called.append((target, timeout))
        return DummySocket()

    monkeypatch.setattr(network.socket, "create_connection", connect)
    client = network._PublicHTTP("public.example", "93.184.216.34", 80)
    client.connect()
    assert called == [(("93.184.216.34", 80), 12)]
    client.close()


def test_redirect_to_private_ip_fails_before_next_connection(monkeypatch):
    calls = []

    class Response:
        status = 302
        def getheader(self, name):
            return ("https://127.0.0.1/private" if name == "Location" else None)

    class Connection:
        def __init__(self, host, address, port):
            calls.append((host, address, port))
        def request(self, *a, **kw):
            pass
        def getresponse(self):
            return Response()
        def close(self):
            pass

    monkeypatch.setattr(network, "_PublicHTTPS", Connection)
    monkeypatch.setattr(network, "_public_ip", lambda *_a: "93.184.216.34")
    with pytest.raises(network.FeedNetworkError, match="Non-public"):
        network.fetch_public_xml("https://example.org/feed")
    assert len(calls) == 1


def test_https_redirect_cannot_downgrade_to_http(monkeypatch):
    class Response:
        status = 302
        def getheader(self, name):
            return "http://other.example.net/feed" if name == "Location" else None

    class Connection:
        def __init__(self, *_args):
            pass
        def request(self, *a, **kw):
            pass
        def getresponse(self):
            return Response()
        def close(self):
            pass

    monkeypatch.setattr(network, "_PublicHTTPS", Connection)
    monkeypatch.setattr(network, "_public_ip", lambda *_a: "93.184.216.34")
    with pytest.raises(network.FeedNetworkError, match="Unsafe feed"):
        network.fetch_public_xml("https://example.org/rss")


def test_public_https_xml_and_size_cap(monkeypatch):
    calls = []

    class Response:
        status = 200
        def __init__(self, payload):
            self.payload = payload
        def getheader(self, name):
            return None
        def read(self, limit):
            assert limit == 1_048_577
            return self.payload

    class Connection:
        def __init__(self, host, address, port):
            calls.append((host, address, port))
        def request(self, method, path, headers):
            assert method == "GET"
            assert path == "/rss?q=one"
            assert headers["Accept-Encoding"] == "identity"
        def getresponse(self):
            return Response(b"<rss><channel /></rss>")
        def close(self):
            pass

    monkeypatch.setattr(network, "_PublicHTTPS", Connection)
    monkeypatch.setattr(network, "_public_ip", lambda *_a: "93.184.216.34")
    assert network.fetch_public_xml("https://example.org/rss?q=one") == b"<rss><channel /></rss>"
    assert calls == [("example.org", "93.184.216.34", 443)]

    def oversized(*_):
        obj = Connection(*_)
        obj.getresponse = lambda: Response(b"X" * (1_048_576 + 1))
        return obj

    monkeypatch.setattr(network, "_PublicHTTPS", oversized)
    with pytest.raises(network.FeedNetworkError, match="exceeds"):
        network.fetch_public_xml("https://example.org/rss?q=one")


def test_xml_entities_rejected_and_body_never_enters_candidates(monkeypatch):
    monkeypatch.setattr(rss, "fetch_public_xml", lambda _url: (
        b'<rss><!DOCTYPE foo [<!ENTITY x SYSTEM "file:///etc/passwd">]>'
        b"<channel><title>Newsletter</title></channel></rss>"
    ))
    blocked = rss.RSSConnector(("https://example.org/feed",))
    assert blocked.fetch() == []
    assert blocked.failed_feeds == [
        {"feed_number": 1, "reason": "invalid_feed_xml"}
    ]

    monkeypatch.setattr(rss, "fetch_public_xml", lambda _url: (
        b"<rss><channel><title>Example</title><item><title>Headline</title>"
        b"<description>PRIVATE_COPYRIGHT_TEXT</description>"
        b"<link>https://example.org/story</link></item></channel></rss>"
    ))
    candidates = rss.RSSConnector(("https://example.org/feed",)).fetch()
    assert len(candidates) == 1
    assert candidates[0].summary == ""
    from kushluk.editor import select_stories
    assert select_stories(candidates)[0].deck == "Open the source for the full story."


def test_private_subscription_endpoint_is_not_exposed_as_story_url(monkeypatch):
    monkeypatch.setattr(rss, "fetch_public_xml", lambda _url: (
        b"<rss><channel><item><title>Public headline without link</title>"
        b"<description>Private full text</description></item></channel></rss>"
    ))
    feed = "https://reader.example.org/private?token=never-publish"
    candidates = rss.RSSConnector((feed,)).fetch()
    assert candidates[0].source.url is None
    assert candidates[0].source.name == "RSS feed"
    from kushluk.editor import select_stories
    stories = select_stories(candidates)
    assert stories[0].source_url is None
    assert "never-publish" not in str(stories)
