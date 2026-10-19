"""Verify durable three-peer handover scaffolds do not impersonate active agents.

These are documentation consistency checks. They do not start a model,
connect to GitHub, watch issue events, read private data, or run A2A.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COORD = ROOT / "coordination"
PEERS = ("chatgpt", "claude", "deepseek")


def test_constitution_and_workspace_are_linked_but_non_authoritative():
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    constitution = (ROOT / "docs/coordination/CONSTITUTION.md").read_text(
        encoding="utf-8"
    )
    index = (COORD / "README.md").read_text(encoding="utf-8")
    assert "## Documentation precedence" in agents
    assert "coordination/README.md" in agents
    assert "docs/coordination/CONSTITUTION.md" in index
    assert "not synchronized cross-model memory" in constitution
    assert "not a second issue tracker" in index.lower()
    assert "A2A" in index
    assert "PR #178" in index


def test_exactly_three_isolated_agent_handovers_and_restart_prompts():
    handovers = {p.parent.name: p for p in (COORD / "agents").glob("*/HANDOVER.md")}
    assert set(handovers) == set(PEERS)
    for peer in PEERS:
        text = handovers[peer].read_text(encoding="utf-8")
        assert "# " in text
        assert "2026-10-19" in text
        assert "source" in text.lower() or "commit" in text.lower()
    assert "not independent peer review" in handovers["chatgpt"].read_text(
        encoding="utf-8"
    ).lower()
    for peer in ("claude", "deepseek"):
        text = handovers[peer].read_text(encoding="utf-8")
        assert "UNINITIALIZED" in text
        assert "NOT" in text
        assert "NONE" in text

    restarts = {p.stem for p in (COORD / "restarts").glob("*.md")}
    assert restarts == {"chatgpt-work", "claude-code", "deepseek-local"}


def test_restarts_share_same_core_authorities_with_no_fake_cross_model_review():
    for peer in ("chatgpt-work", "claude-code", "deepseek-local"):
        text = (COORD / "restarts" / (peer + ".md")).read_text(encoding="utf-8")
        for authority in ("AGENTS.md", "CONSTITUTION.md", "#170", "#176",
                          "#171", "#172", "#173", "ADR 0013"):
            assert authority in text, (peer, authority)
        assert "independent" in text.lower()
        assert "founder" in text.lower()
        assert "not" in text.lower() and "A2A" in text
        assert "do not" in text.lower()
    assert "NOT POSTED" in (COORD / "restarts" / "chatgpt-work.md").read_text(
        encoding="utf-8"
    )
    assert "UNINITIALIZED" in (COORD / "restarts" / "claude-code.md").read_text(
        encoding="utf-8"
    )
    assert "UNINITIALIZED" in (COORD / "restarts" / "deepseek-local.md").read_text(
        encoding="utf-8"
    )


def test_collective_decisions_and_dissent_do_not_claim_three_ai_consensus():
    required = ("ASSUMPTIONS.md", "DECISIONS.md", "DISSENT.md", "DISCUSSION_QUEUE.md")
    for name in required:
        assert (COORD / "collective" / name).exists()
    decisions = (COORD / "collective/DECISIONS.md").read_text(encoding="utf-8")
    dissent = (COORD / "collective/DISSENT.md").read_text(encoding="utf-8")
    assumptions = (COORD / "collective/ASSUMPTIONS.md").read_text(
        encoding="utf-8"
    )
    queue = (COORD / "collective/DISCUSSION_QUEUE.md").read_text(
        encoding="utf-8"
    )
    assert "PR #178" in decisions
    assert "MERGED" in decisions
    assert "not accepted" in assumptions.lower()
    assert "no invented independent opinions" in dissent.lower()
    for issue in ("#171", "#172", "#173"):
        assert issue in queue
    assert "not a monitoring daemon" in queue.lower()
    assert "A2A" in queue


def test_no_fabricated_completed_peer_sessions():
    sessions = sorted((COORD / "sessions").glob("*"))
    assert {p.name for p in sessions} == {"README.md"}
    assert "No live three-peer round" in sessions[0].read_text(encoding="utf-8")
