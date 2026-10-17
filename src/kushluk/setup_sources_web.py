"""Local source-review step: inert OPML proposals and one-by-one consent.

No feed fetching, article reuse, direct inclusion or remote service. Private URLs
remain on the local machine and are never printed to logs or HTML.
"""
from __future__ import annotations

from html import escape
from pathlib import Path
from urllib.parse import urlsplit

from kushluk.opml import FeedProposal, OPMLImportError, parse_opml
from kushluk.source_registry import (
    SourceApprovalError, approve_feed, read_registry, set_source_mode,
)

MAX_BROWSER_FEEDS = 50


def import_review_opml(value: str) -> tuple[FeedProposal, ...]:
    """Bound the one-session ephemeral proposal list, without saving or activating."""
    if not isinstance(value, str) or not value.strip():
        raise OPMLImportError("Paste an OPML source list")
    feeds = parse_opml(value.encode("utf-8"))
    if len(feeds) > MAX_BROWSER_FEEDS:
        raise OPMLImportError("Review at most 50 feeds in one browser import")
    return tuple(
        FeedProposal(
            title=(f"Feed from {urlsplit(feed.url).hostname}" if feed.title == feed.url
                   else feed.title),
            url=feed.url,
        )
        for feed in feeds
    )


def approve_reviewed(pending: tuple[FeedProposal, ...], index: str,
                     *, consent: bool, path: Path) -> bool:
    if not consent:
        raise SourceApprovalError("Explicit feed-access permission is required")
    try:
        number = int(index)
    except (TypeError, ValueError) as exc:
        raise SourceApprovalError("Invalid source selection") from exc
    if str(number) != index or number < 1 or number > len(pending):
        raise SourceApprovalError("Invalid source selection")
    _, _, created = approve_feed(pending[number - 1], acknowledge=True, path=path)
    return created


def change_reviewed_mode(identifier: str, mode: str,
                         *, consent: bool, path: Path) -> None:
    """Only reader-visible pause/resume; higher reuse modes stay nonexecutable."""
    if mode not in {"ignore", "reference-only"}:
        raise SourceApprovalError("Only pause or reference-only resume is available")
    if mode == "reference-only" and not consent:
        raise SourceApprovalError("Resume requires explicit feed-access permission")
    set_source_mode(identifier, mode, path=path)


_STYLE = """<style>
:root{color-scheme:light;font-family:system-ui,-apple-system,sans-serif;background:#f4f0e8;color:#25372c}
*{box-sizing:border-box}body{margin:0}.wrap{max-width:1050px;margin:auto;padding:40px 24px}
header{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #bfc5ba;padding-bottom:20px;gap:16px}
.brand{font:700 26px Georgia,serif;letter-spacing:-.05em}.eyebrow{font-size:12px;color:#55715f;text-transform:uppercase;letter-spacing:.14em}
h1{font:normal clamp(38px,6vw,65px)/1.08 Georgia,serif;letter-spacing:-.04em;max-width:690px;margin:45px 0 14px}
h2{font:normal 26px Georgia,serif;margin:0 0 10px}p{line-height:1.65;color:#435348}
main{display:grid;grid-template-columns:1fr 1fr;gap:26px;margin-top:30px}
.panel{background:#fffefa;border:1px solid #d7dacf;padding:28px;min-width:0}
label{font-weight:650;font-size:14px;display:block;margin:15px 0 8px}
textarea{width:100%;min-height:145px;border:1px solid #adbbae;padding:12px;font:13px/1.5 ui-monospace,monospace;resize:vertical}
button{background:#24513a;color:white;border:0;padding:12px 18px;font:600 14px system-ui;cursor:pointer;margin-top:14px}
button:focus-visible,textarea:focus-visible{outline:3px solid #427c56;outline-offset:3px}
button.secondary{background:#e5eae1;color:#254736;border:1px solid #9fb09d}
.feed{border-top:1px solid #d8ded4;padding:18px 0}.feed strong{font-size:16px}
.meta{font-size:12px;color:#606d64;overflow-wrap:anywhere}
.check{font-weight:400;font-size:13px;line-height:1.6;display:flex;gap:10px;align-items:flex-start}
.check input{margin-top:4px}.status{background:#e7ece6;padding:12px 16px;font-size:14px}
a{color:#24513a}footer{border-top:1px solid #bfc5ba;font-size:12px;color:#69756b;margin-top:48px;padding-top:18px}
@media(max-width:780px){main{grid-template-columns:1fr}.wrap{padding:22px 18px}}
</style>"""


def render_source_review(
    pending: tuple[FeedProposal, ...], *, path: Path,
    csrf: str, notice: str | None = None,
) -> str:
    """HTML-escape untrusted titles; never embed secret-bearing feed URLs."""
    approved = read_registry(path)
    approved_ids = {row["url"] for row in approved}
    items = []
    for index, feed in enumerate(pending, 1):
        # Reveal only hostname. The feed URL may embed a private subscription key.
        hostname = escape(urlsplit(feed.url).hostname or "Feed", quote=True)
        title = escape(feed.title, quote=True)
        if feed.url in approved_ids:
            action = '<p class="meta">Already in your private source registry</p>'
        else:
            action = (
                '<form action="/sources/approve" method="post">'
                f'<input type="hidden" name="csrf" value="{csrf}">'
                f'<input type="hidden" name="index" value="{index}">'
                '<label class="check"><input type="checkbox" name="consent" value="yes" required>'
                '<span>I have permission to access this specific feed. '
                'Only headlines and public references will be used; not article bodies.</span>'
                '</label><button type="submit">Approve this feed only</button></form>'
            )
        items.append(
            '<div class="feed"><strong>' + title + '</strong>'
            f'<div class="meta">{hostname} · Proposed only</div>' + action + '</div>'
        )
    active = []
    for row in approved:
        safe_name = (
            urlsplit(row["url"]).hostname or "Feed"
            if row["title"] == row["url"] else row["title"]
        )
        name = escape(safe_name, quote=True)
        host = escape(urlsplit(row["url"]).hostname or "Feed", quote=True)
        status = "Active reference only" if row["enabled"] else "Paused / unsupported"
        action = "ignore" if row["enabled"] else "reference-only"
        label = "Pause feed" if row["enabled"] else "Resume reference only"
        permission = (
            '<label class="check"><input type="checkbox" name="consent" value="yes" required>'
            '<span>I confirm permission to access this feed again.</span></label>'
            if action == "reference-only" else ""
        )
        active.append(
            f'<div class="feed"><strong>{name}</strong><div class="meta">{host} · {status}</div>'
            '<form action="/sources/mode" method="post">'
            f'<input type="hidden" name="csrf" value="{csrf}">'
            f'<input type="hidden" name="id" value="{row["id"]}">'
            f'<input type="hidden" name="mode" value="{action}">'
            + permission
            + f'<button class="secondary" type="submit">{label}</button></form></div>'
        )
    banner = f'<p class="status" role="status">{escape(notice)}</p>' if notice else ""
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>Kuşluk · Review sources</title>' + _STYLE + '</head><body>'
        '<div class="wrap"><header><span class="brand">kuşluk.</span>'
        '<span class="eyebrow">Your sources · 02 / 03</span></header>'
        '<h1>Choose what belongs in your paper.</h1>'
        '<p>Import a reading list for review. Nothing is activated until you approve '
        'each feed. Only reference-only use is enabled: headlines and public links, '
        'never copied articles. All changes stay on this computer.</p>'
        + banner + '<main><section class="panel"><h2>Bring a reading list</h2>'
        '<p>Paste OPML exported from an RSS reader. Import only previews it; '
        'this page never fetches articles.</p>'
        '<form method="post" action="/sources/import">'
        f'<input type="hidden" name="csrf" value="{csrf}">'
        '<label for="opml">OPML source list (up to 50)</label>'
        '<textarea id="opml" name="opml" required spellcheck="false" '
        'placeholder="&lt;opml version=&quot;2.0&quot;&gt;…&lt;/opml&gt;"></textarea>'
        '<button type="submit">Review without activating</button></form>'
        '<h2 style="margin-top:36px">Proposed feeds</h2>'
        + ("".join(items) if items else '<p>No unactivated OPML proposals yet.</p>')
        + '</section><section class="panel"><h2>Your approved feeds</h2>'
        '<p>Pause or resume one feed at a time. Direct inclusion and derivative '
        'reuse remain disabled until separate rights evidence exists.</p>'
        + ("".join(active) if active else '<p>No feeds approved yet.</p>')
        + '<p class="meta">Status is local. No full-text permission is inferred '
        'from your approval.</p></section></main>'
        '<footer><a href="/">Home setup</a> · Local-only source management · '
        'No network requests during import, review, approval or pause</footer></div>'
        '</body></html>'
    )
