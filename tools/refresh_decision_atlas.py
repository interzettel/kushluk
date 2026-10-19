#!/usr/bin/env python3
"""Refresh/check the embedded offline Kuşluk Decision Atlas snapshot.

This does not call GitHub, change issue state, register a scheduler, or print.
The single current JSON snapshot is docs/strategy/decision-atlas.json.
"""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "docs" / "strategy"
JSON = ROOT / "decision-atlas.json"
HTML = ROOT / "decision-atlas.html"
MARKER = re.compile(
    r'(<script type="application/json" id="atlas-model">)(.*?)(</script>)',
    re.DOTALL,
)

def refresh(write: bool = False) -> bool:
    model = json.loads(JSON.read_text(encoding="utf-8"))
    page = HTML.read_text(encoding="utf-8")
    matches = list(MARKER.finditer(page))
    if len(matches) != 1:
        raise ValueError("Exactly one embedded atlas model must exist")
    embedded = json.dumps(model, ensure_ascii=True, separators=(",", ":")).replace("<", r"\u003c")
    expected = MARKER.sub(lambda m: m.group(1) + embedded + m.group(3), page, count=1)
    if write:
        if page != expected:
            HTML.write_text(expected, encoding="utf-8")
        return True
    actual = json.loads(matches[0].group(2))
    return actual == model

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="check HTML embedded data match without edits")
    mode.add_argument("--write", action="store_true", help="rewrite HTML snapshot from JSON only")
    args = parser.parse_args()
    ok = refresh(write=args.write)
    print("decision atlas snapshot: " + ("synchronized" if ok else "STALE (run --write)"))
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
