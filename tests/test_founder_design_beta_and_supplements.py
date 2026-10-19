"""Guard founder-reviewed scope while leaving delivery evidence and accepted ADRs intact."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_private_beta_has_additive_physical_design_acceptance():
    release = read("docs/RELEASE_PLAN.md")
    assert "Founder-approved M2a-Design gate" in release
    assert "Two materially different visual systems on the identical fixture" in release
    assert "Founder visual signoff" in release
    assert "The **existing** printer/host/reboot/permission/reader requirements" in release
    assert "not a new numbered milestone or evidence gate" in release
    assert "F-015 at M3" in release and "F-024 at M5" in release and "F-027 at M6" in release
    assert release.count("| **M2a · First invited private pilot** |") == 1


def test_supplements_are_future_direction_not_accepted_renderer_behavior():
    for path in ("docs/RELEASE_PLAN.md", "docs/ROADMAP.md", "docs/strategy/OWNER_NORTH_STAR.md"):
        data = read(path)
        assert "four" in data.lower() and "supplement" in data.lower()
        assert "ADR 0013" in data
    assert "requires separately approved ADR/requirement migration" in read("docs/RELEASE_PLAN.md")
    assert "not implemented" in read("docs/RELEASE_PLAN.md")


def test_impact_matrix_is_nonbinding_and_links_to_merged_public_snapshot():
    matrix = read("docs/strategy/IMPACT_MATRIX.md")
    assert "../../site/decision-atlas/decision-atlas.json" in matrix
    assert "historical" in matrix.lower()
    assert "not a live issue tracker" in matrix
    assert "G1–G8" in matrix
    assert "#issuecomment-6277794493" in matrix
