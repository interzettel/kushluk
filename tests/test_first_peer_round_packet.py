"""First multi-AI round: verify frozen facts and status boundaries, not consensus.

Static repository consistency only. No models launched, GitHub writes, issue
monitoring or A2A transport started by these tests.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "coordination/rounds/2026-10-19-wave1/SOURCE_PACKET.md"
CONSTITUTION = ROOT / "docs/coordination/CONSTITUTION.md"
AGENTS = ROOT / "AGENTS.md"
HANDOVER = ROOT / "coordination/agents/chatgpt/HANDOVER.md"


def test_first_round_packet_has_same_three_primary_issues_for_all_peers():
    data = PACKET.read_text(encoding="utf-8")
    for issue in ("#171", "#172", "#173"):
        assert issue in data
    assert "fe25c90fa14e6875845074247a8a2b75e19e249c" in data
    for path in (
        "models.py", "publication.py", "validation.py", "print_profiles.py",
        "editor.py", "media.py", "REQUIREMENTS.md", "CONSTITUTION.md",
    ):
        assert path in data
    assert "no authenticated Claude Code or local DeepSeek review verified" in data
    assert "never a second independent peer" in data
    assert "source facts" in data.lower()
    assert "ADR 0013" in data


def test_constitution_status_matches_real_accepted_merge_without_new_adr():
    text = CONSTITUTION.read_text(encoding="utf-8")
    assert "FOUNDER-APPROVED" in text
    assert "PR #178" in text
    assert "PR #179" in text
    assert "not synchronized cross-model memory" in text
    assert "four logical A4 pages" in text
    assert "No automated peer meetings" in text
    root = AGENTS.read_text(encoding="utf-8")
    assert "Founder-approved collaboration constitution" in root
    assert "PR #179 merged" in root
    assert "## Documentation precedence" in root


def test_only_chatgpt_self_reports_continuation_and_uninitialized_other_peers():
    text = HANDOVER.read_text(encoding="utf-8")
    for issue_comment in (
        "6270728035", "6270759201", "6270760176", "6270761103",
    ):
        assert issue_comment in text
    assert "not independent extra votes" in text
    for peer in ("claude", "deepseek"):
        handover = (
            ROOT / "coordination/agents" / peer / "HANDOVER.md"
        ).read_text(encoding="utf-8")
        assert "UNINITIALIZED" in handover
        assert "NO REVIEW" in handover or "NO REVIEW YET" in handover


def test_proposal_records_not_mistaken_for_delivered_model_discussions():
    queue = (
        ROOT / "coordination/collective/DISCUSSION_QUEUE.md"
    ).read_text(encoding="utf-8")
    decisions = (
        ROOT / "coordination/collective/DECISIONS.md"
    ).read_text(encoding="utf-8")
    assert "2026-10-19-W1" in queue
    assert "no verified independent comments" in queue.lower()
    assert "C-008" in decisions
    assert "STEP 2 DOCUMENTATION MERGED" in decisions
    assert "not A2A transport" in decisions


def test_packet_relative_links_resolve_to_actual_files():
    source = PACKET.read_text(encoding="utf-8")
    for target in re.findall(r"\\]\\(([^)]+)\\)", source):
        if target.startswith(("https://", "http://")):
            continue
        local_path = PACKET.parent / target.split("#", 1)[0]
        assert local_path.is_file(), f"Broken packet source link: {target}"
