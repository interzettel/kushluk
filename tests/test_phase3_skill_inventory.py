"""Static Phase III skill inventory: no remote installs or model execution."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents" / "skills"
EXPECTED = ("design-maturity-review", "design-taste-frontend", "good-css", "impeccable", "awwwards", "jury")


def test_pinned_text_only_six_skill_entrypoints_and_licences():
    for name in EXPECTED:
        root = SKILLS / name
        skill = (root / "SKILL.md").read_text(encoding="utf-8")
        assert "name: " + name in skill or "name: '" + name in skill
        assert (root / "LICENSE").is_file()
        assert list(root.rglob("*.md")), name
        assert not list(root.rglob("*.mjs")), name
        assert not list(root.rglob("*.js")), name
        assert not list(root.rglob("*.exe")), name
    assert sorted(p.name for p in SKILLS.iterdir() if p.is_dir()) == sorted(EXPECTED)


def test_provenance_and_capability_boundaries_are_documented():
    notice = (ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
    audit = (ROOT / "docs/design/PHASE3_SKILLS_AUDIT.md").read_text(encoding="utf-8")
    readme = (SKILLS / "README.md").read_text(encoding="utf-8")
    for name in EXPECTED:
        assert name in notice and name in audit and name in readme
    assert "Not installed" in readme
    assert "unverified" in audit.lower()
    assert "a72969932bd4fb850eafd9694a5b54a62c68dd9f" in audit
    assert "f193f6745aae738e9d54a0ca28792822e4777a63" in audit
