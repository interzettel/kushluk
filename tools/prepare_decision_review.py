#!/usr/bin/env python3
"""Prepare a source-linked, model-neutral Kuşluk decision review prompt.

Offline, stdout-only by default: never polls GitHub, executes another model,
reads private content, writes issue comments, or invokes printing.
"""
import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "docs" / "strategy" / "decision-atlas.json"
REPO = "https://github.com/interzettel/kushluk"


def build_prompt(node: dict, reviewer: str, commit: str, phase: str) -> str:
    refs = "\n".join(f"- {ref}" for ref in node["refs"])
    choices = "\n".join(
        f"{chr(65 + i)}. {value}" for i, value in enumerate(node["options"])
    )
    impact = node.get("impact", {})
    impact_lines = "\n".join(
        f"- {key.replace('_', ' ')}: {', '.join(values) if values else 'none mapped'}"
        for key, values in impact.items()
    )
    extra = (
        "First form an independent opinion from original sources, without "
        "copying previous agents' recommendations."
        if phase == "independent"
        else "Read peers' comments only after identifying your own provisional "
        "position. Critique the strongest contrary evidence and disclose revisions."
    )
    return f"""# Kuşluk peer decision review — {node['id']}

**Reviewer (self-reported):** {reviewer}
**Phase:** {phase}
**Prepared from checkout:** {commit}
**Owning issue:** {REPO}/issues/{node['issue']}
**Founder vision:** {REPO}/issues/170
**Full council:** {REPO}/issues/157

## Exact question

{node['question']}

## Source references (inspect independently)

{refs}

The parent issue, current accepted ADRs, source model, feature catalogue and
work ledger are the primary authorities. This cached atlas is only a dated
discussion snapshot; verify any claim that depends on live status.

## Competing choices — none automatically approved

{choices}

Also consider keeping the present accepted implementation if none of these
alternatives has adequate evidence.

## Proposed downstream impact (hypotheses, not status changes)

{impact_lines}

## Required independent reasoning

{extra}

You are one of three generalist peers (ChatGPT, Claude, user-operated local
DeepSeek); there are NO fixed reviewer job descriptions. Examine all of:
reader comprehension and desire to hold the paper; art direction; copyright,
privacy and source permissions; accessibility; architecture and safe AI/agent
interoperability; open-source economics; failure/replay testing; release order.
Separate observed evidence, inference, strong opinions and missing tests.

Return a GitHub-ready **Markdown review** with:
1. Reviewer identification / actual model, sources and commit inspected.
2. Observed facts versus contested assumptions.
3. A/B/C tradeoffs, plus an honest baseline option.
4. Preferred direction and strongest counterargument against it.
5. Falsifying experiment, paper/reader proof and negative tests.
6. Exact ADR/F-ID/task/gate/milestone effects and reversibility.
7. Your provisional ACCEPT / AMEND / EXPERIMENT / DEFER / REJECT recommendation
   and concrete questions for the founder.

Do not assert that another AI agreed until its own attributable comment exists.
A GitHub comment is a proposal; only the founder/authorized maintainer can
accept a product decision, change an ADR, license, or release.
Do not read private mail, make external requests, execute arbitrary recipes,
post to GitHub or print without separate explicit authorization.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--node", required=True, help="Decision ID, e.g. length")
    parser.add_argument(
        "--reviewer", required=True, help="Your actual model/runner identifier"
    )
    parser.add_argument(
        "--phase", choices=("independent", "cross_exam"),
        default="independent"
    )
    args = parser.parse_args()
    model = json.loads(ATLAS.read_text(encoding="utf-8"))
    node = next((n for n in model["nodes"] if n["id"] == args.node), None)
    if node is None:
        parser.error(f"Unknown decision '{args.node}'. Read DECISION_ATLAS.md.")
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT,
            capture_output=True, text=True, check=True, timeout=5
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        commit = "unavailable — reviewer must supply actual checked-out commit"
    print(build_prompt(node, args.reviewer, commit, args.phase), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
