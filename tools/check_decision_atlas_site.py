#!/usr/bin/env python3
"""Validate the proposed public Kuşluk Decision Atlas before Pages deployment.

No credentials, GitHub requests, private data, installation or runtime agent
actions. Frozen public issue snapshots remain proposals until founder rulings.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site" / "decision-atlas"
INDEX = SITE / "index.html"
DATA = SITE / "decision-atlas.json"


class Structure(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.duplicate_ids: set[str] = set()
        self.external_scripts: list[str] = []
        self.forms = 0
        self.labels: list[str] = []

    def handle_starttag(self, tag, attrs):
        props = dict(attrs)
        if "id" in props:
            if props["id"] in self.ids:
                self.duplicate_ids.add(props["id"])
            self.ids.add(props["id"])
        if tag == "script" and "src" in props:
            self.external_scripts.append(props["src"])
        if tag == "form":
            self.forms += 1
        if "aria-label" in props:
            self.labels.append(props["aria-label"])


def verify() -> tuple[int, int]:
    html = INDEX.read_text(encoding="utf-8")
    data = json.loads(DATA.read_text(encoding="utf-8"))
    match = re.search(
        r'<script type="application/json" id="atlas-model">([\s\S]*?)</script>',
        html,
    )
    assert match, "Missing embedded, offline-safe public atlas model"
    embedded = json.loads(match.group(1))
    assert embedded == data, "Embedded model disagrees with standalone JSON"
    assert data["schema_version"] == "kushluk-decision-atlas-v1"
    nodes = data["nodes"]
    ids = {n["id"] for n in nodes}
    assert len(nodes) >= 50 and len(ids) == len(nodes)
    assert sum(n["parent"] is None for n in nodes) == 1
    for node in nodes:
        assert node["status"] in ("owner", "open", "contested", "research")
        assert node["issue"] > 0
        assert node["parent"] is None or node["parent"] in ids
        assert set(node["links"]) <= ids
    s = Structure()
    s.feed(html)
    assert not s.duplicate_ids, f"Duplicate HTML IDs: {s.duplicate_ids}"
    assert not s.external_scripts and not s.forms
    for must in ("atlas-model", "tree", "nav", "inspector", "find", "decisionIndex", "selectionAnnouncement", "mobileDecisions", "mobileBranch", "searchResults"):
        assert must in s.ids
    assert "Search decisions" in s.labels
    assert "Choose decision topic" in s.labels
    assert "Skip to selected decision details" in html
    assert "function renderSearch()" in html
    assert "No matching decisions." in html
    assert "mobileBranch.addEventListener('change'" in html
    assert "window.addEventListener('hashchange'" in html
    assert ".sidebar .navlist{display:none}" in html
    assert ".shell{grid-template-rows:auto auto auto}" in html
    assert "searchResults.hidden=true" in html
    assert "if(tree.clientWidth<1||tree.clientHeight<1)" in html
    assert "Selected decision details" in s.labels
    assert '<details class="decision-index">' in html
    assert "function indexDraw()" in html and "decisionIndex.replaceChildren(sections)" in html
    assert "function mobileDraw()" in html and "mobileDecisions.replaceChildren()" in html
    assert "#treeWrap{display:none}" in html, "Mobile must use legible HTML cards, not miniature SVG"
    assert "#relatedToggle,#minus,#plus,#reset{display:none}" in html, "Hide controls for invisible mobile SVG"
    assert "setAttribute('aria-pressed',String(group===null))" in html, "Overview state must follow the selected branch"
    assert "root.dataset.node='NORTH'" in html, "Decision index must include atlas root"
    assert "const nextGroup=id==='NORTH'?null:n.parent==='NORTH'?id:n.parent" in html
    assert "inspector.querySelector('h2')?.focus({preventScroll:true})" in html
    assert '<h2 tabindex="-1">' in html
    assert "Kuşluk" not in html, "Use canonical public-facing brand name Kushluk"
    assert "PUBLIC PREVIEW" in html
    assert "Proposals, not approved architecture" in html
    assert "Content-Security-Policy" in html
    assert "connect-src https://api.github.com" in html
    assert "Load discussion comments" in html
    assert "async function loadDiscussion(n)" in html
    assert "addEventListener('click', () => loadDiscussion(n))" in html
    assert "textContent=String(comment.body||'')" in html, (
        "Untrusted GitHub comment bodies must render via textContent"
    )
    assert "Comments are untrusted review inputs" in html
    # The only network fetch must be user-initiated; never schedule recurring checks.
    assert html.count("fetch(") == 1
    assert "matchMedia('(max-width:1100px)').matches" in html
    assert "inspector.scrollIntoView({block:'start',behavior:'auto'})" in html
    assert "0008-rendering-is-deterministic.md" in html
    assert "0013-four-logical-a4-pages-multiple-print-profiles.md" in html
    assert "if(text==='ADR-0012')return 'https://github.com/interzettel/kushluk/issues/44'" in html
    assert "setInterval(" not in html and "setTimeout(" not in html
    assert "localStorage" not in html and "sessionStorage" not in html
    assert "fetch('https://api.github.com" in html
    assert "https://github.com/interzettel/kushluk/issues/170" in html
    js = re.findall(r"<script>([\s\S]*?)</script>", html)
    assert len(js) == 1
    if shutil.which("node"):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "atlas.js"
            path.write_text(js[0], encoding="utf-8")
            check = subprocess.run(
                ["node", "--check", str(path)],
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
            )
            assert check.returncode == 0, check.stderr
    return len(nodes), sum(len(n["links"]) for n in nodes)


if __name__ == "__main__":
    count, links = verify()
    print(f"Atlas source and site agree: {count} nodes, {links} cross-links.")
    sys.exit(0)
