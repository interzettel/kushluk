"""Guard that three-peer governance text never overrides current product authority.

Static checks only; no GitHub calls, external agents, files outside the
checkout, actual printing, or background monitoring.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / "AGENTS.md"
CONSTITUTION = ROOT / "docs" / "coordination" / "CONSTITUTION.md"
AUDIT = ROOT / "docs" / "coordination" / "RECONCILIATION_AUDIT_2026-10-19.md"
REVIEW = ROOT / "docs" / "coordination" / "REVIEW_TEMPLATE.md"
METHOD = ROOT / "docs" / "WORKING_METHOD.md"
DECISIONS = ROOT / "docs" / "OPEN_DECISIONS.md"


def test_root_precedence_and_present_print_contract_still_explicit():
    src = AGENTS.read_text(encoding="utf-8")
    assert "## Documentation precedence" in src
    assert "Accepted ADRs under `docs/adr/`" in src
    assert "Four logical DIN A4 pages by default" in src
    assert "ADR 0013" in src and "exactly four logical A4 pages" in src
    assert "ADR 0008/0015" in src
    assert "duplicate **accepted ADR 0012**" in src
    assert "## GitHub issue, Project and development traceability" in src


def test_governance_is_nonrole_silo_and_truthful_about_a2a():
    src = CONSTITUTION.read_text(encoding="utf-8")
    assert "no permanent Designer/Architect/PM/Tester AI silos".lower() in src.lower()
    for s in ("ChatGPT Work", "Claude Code", "DeepSeek", "founder",
              "Independent round", "Cross-examination", "Founder ruling",
              "No agent may say it contacted another participant",
              "not A2A protocol compliance"):
        # The latter is in the review template rather than the constitution.
        if s == "not A2A protocol compliance":
            assert s.lower() in REVIEW.read_text(encoding="utf-8").lower()
        else:
            assert s.lower() in src.lower()
    for required in ("PROPOSED", "REVIEWED", "DECIDED", "IMPLEMENTED", "VERIFIED"):
        assert required in src
    assert "No automated peer meetings" in src
    assert "explicit approval" in src.lower()


def test_source_audit_preserves_real_unresolved_conflicts():
    src = AUDIT.read_text(encoding="utf-8")
    for key in ("S01", "S03", "S04", "S05", "S07", "S09", "S10", "S15"):
        assert f"**{key}**" in src
    for authority in ("ADR 0013", "ADR 0012", "#44", "#38",
                      "#169", "#177", "not a silent"):
        assert authority.lower() in src.lower()
    assert "not installed" in src.lower()
    assert "No checkbox changes" in src


def test_review_template_distinguishes_peer_and_founder_authorship():
    src = REVIEW.read_text(encoding="utf-8")
    for required in ("Independent peer review", "Cross-examination reply",
                     "Founder-only decision record", "model and runner",
                     "strongest counterargument"):
        assert required.lower() in src.lower()
    assert "no" in src.lower() and "fictitious" not in src.lower()


def test_existing_project_hierarchy_and_open_decisions_remain_visible():
    method = METHOD.read_text(encoding="utf-8")
    decisions = DECISIONS.read_text(encoding="utf-8")
    assert "Project #3" in method
    assert "temporary execution ownership" in method
    assert "three" in method.lower()
    assert "## 1. Final production typefaces" in decisions
    assert "#171" in decisions and "#176" in decisions
    assert "not a silent amendment" in decisions.lower()


def test_unchanged_accepted_adr_and_current_requirement_source():
    adr = (ROOT / "docs/adr/0013-four-logical-a4-pages-multiple-print-profiles.md").read_text(
        encoding="utf-8"
    )
    requirements = (ROOT / "docs/REQUIREMENTS.md").read_text(encoding="utf-8")
    assert "**Status:** Accepted" in adr
    assert "four logical DIN A4 pages" in requirements
    assert "**MUST**" in requirements
