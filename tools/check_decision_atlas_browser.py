#!/usr/bin/env python3
"""Browser smoke for the public Atlas. Captures review evidence without publishing it.

Runs on GitHub's Ubuntu runner image with Google Chrome preinstalled.
No authentication, external downloads, source uploads or model execution.
"""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = (ROOT / "site" / "decision-atlas" / "index.html").resolve().as_uri() + "#ART"
OUTPUT = ROOT / ".review" / "decision-atlas"


def chrome_binary() -> str:
    path = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chromium-browser")
    if not path:
        raise RuntimeError("Chrome/Chromium not found; cannot claim browser verification")
    return path


def render(chrome: str, size: str, name: str) -> None:
    flags = [
        chrome, "--headless=new", "--no-sandbox", "--disable-gpu",
        "--disable-dev-shm-usage", "--disable-extensions",
        "--no-first-run", "--no-default-browser-check",
        f"--window-size={size}",
    ]
    dom = subprocess.run(
        [*flags, "--dump-dom", PAGE],
        check=True, capture_output=True, text=True, timeout=45,
    ).stdout
    index_items = len(re.findall(r'class="index-item"', dom))
    assert index_items == 56, f"{name}: expected 56 accessible index buttons, got {index_items}"
    assert 'id="decisionIndex"' in dom and 'Selected decision details' in dom
    assert re.search(r'<h2 tabindex="-1">ART DIRECTION', dom), (
        f"{name}: decision inspector did not render the selected hash branch"
    )
    assert len(re.findall(r'class="node-card"', dom)) > 2, (
        f"{name}: interactive SVG nodes missing from rendered DOM"
    )
    assert "PUBLIC PREVIEW" in dom and "Load discussion comments" in dom

    OUTPUT.mkdir(parents=True, exist_ok=True)
    screenshot = OUTPUT / f"{name}.png"
    subprocess.run(
        [*flags, f"--screenshot={screenshot}", PAGE],
        check=True, capture_output=True, text=True, timeout=45,
    )
    assert screenshot.stat().st_size > 2000, f"{name}: screenshot empty"
    print(f"{name}: Chrome rendered 56 HTML decisions, SVG and inspector; screenshot saved")


if __name__ == "__main__":
    chrome = chrome_binary()
    render(chrome, "1440,900", "desktop-1440")
    render(chrome, "390,844", "mobile-390")
