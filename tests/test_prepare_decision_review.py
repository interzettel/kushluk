"""No-network source packet for independent generalist reviewers."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "prepare_decision_review.py"
ATLAS = ROOT / "site" / "decision-atlas" / "decision-atlas.json"


def test_same_sources_and_options_for_any_reviewing_model():
    node = next(
        n for n in json.loads(ATLAS.read_text(encoding="utf-8"))["nodes"]
        if n["id"] == "length"
    )
    assert len(node["options"]) >= 3
    arguments = ["--node", "length"]
    reviews = []
    for reviewer in ("ChatGPT", "Claude", "DeepSeek V4.1 Flash"):
        run = subprocess.run(
            [sys.executable, str(SCRIPT), *arguments, "--reviewer", reviewer],
            text=True, capture_output=True, timeout=10
        )
        assert run.returncode == 0, run.stderr
        assert f"**Reviewer (self-reported):** {reviewer}" in run.stdout
        assert "/issues/171" in run.stdout
        assert "ADR 0013" in run.stdout
        assert "FMT-01" in run.stdout
        assert "strongest counterargument" in run.stdout.lower()
        reviews.append(run.stdout.replace(
            f"**Reviewer (self-reported):** {reviewer}",
            "**Reviewer (self-reported):** REVIEWER",
        ))
    assert reviews[0] == reviews[1] == reviews[2]


def test_cross_exam_packet_does_not_fake_peer_comments():
    run = subprocess.run(
        [sys.executable, str(SCRIPT), "--node", "prompt",
         "--reviewer", "Manual Claude runner", "--phase", "cross_exam"],
        capture_output=True, text=True, timeout=10
    )
    assert run.returncode == 0, run.stderr
    assert "Read peers' comments only after" in run.stdout
    assert "Do not assert that another AI agreed" in run.stdout
    assert "only the founder/authorized maintainer" in run.stdout
    assert "Atlas snapshot date: 2026-10-19" in run.stdout


def test_unknown_node_rejected_before_side_effects():
    run = subprocess.run(
        [sys.executable, str(SCRIPT), "--node", "does-not-exist",
         "--reviewer", "Local DeepSeek"],
        capture_output=True, text=True, timeout=10
    )
    assert run.returncode != 0
    assert "Unknown decision" in run.stderr


def test_reviewer_script_has_no_network_or_publish_side_effects():
    src = SCRIPT.read_text(encoding="utf-8")
    for forbidden in (
        "requests.get", "urllib.request", "gh issue comment",
        "Register-ScheduledTask", "--print", "socket.", "subprocess.Popen",
    ):
        assert forbidden not in src
    assert "print(build_prompt" in src
    assert 'ROOT / "site" / "decision-atlas" / "decision-atlas.json"' in src
