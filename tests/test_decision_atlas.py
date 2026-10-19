"""Decision atlas source, offline viewer, and GitHub diagram consistency.

The structured atlas is a proposal snapshot. These tests do not infer live
GitHub decisions or award original 90-task / 8-gate evidence.
"""
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STRAT = ROOT / "docs" / "strategy"
MODEL = STRAT / "decision-atlas.json"
VIEWER = STRAT / "decision-atlas.html"
DIAGRAM = STRAT / "DECISION_ATLAS.md"

def load():
    return json.loads(MODEL.read_text(encoding="utf-8"))

def test_atlas_nodes_unique_hierarchical_and_cross_links_valid():
    data = load()
    nodes = data["nodes"]
    id_to = {n["id"]: n for n in nodes}
    assert data["schema_version"] == "kushluk-decision-atlas-v1"
    assert len(nodes) >= 50
    assert len(id_to) == len(nodes)
    assert [n["id"] for n in nodes if n["parent"] is None] == ["NORTH"]
    assert len([n for n in nodes if n["parent"] == "NORTH"]) >= 7
    for n in nodes:
        assert n["id"].isascii()
        assert n["id"].replace("-", "").isalnum()
        assert n["status"] in {"owner", "open", "contested", "research"}
        assert n["question"]
        assert isinstance(n["options"], list)
        assert len(n["options"]) >= 2
        assert isinstance(n["issue"], int) and n["issue"] > 0
        assert any(s.startswith("#") for s in n["refs"])
        if n["parent"]:
            assert n["parent"] in id_to
            assert n["id"] != n["parent"]
        for v in n["links"]:
            assert v in id_to and v != n["id"]
        visited = {n["id"]}
        p = n["parent"]
        while p:
            assert p not in visited, f"cycle containing {n['id']}"
            visited.add(p)
            p = id_to[p]["parent"]
    assert len([n for n in nodes if n["status"] == "contested"]) >= 10

def test_offline_viewer_embeds_exact_current_machine_readable_snapshot():
    model = load()
    html = VIEWER.read_text(encoding="utf-8")
    match = re.search(
        r'<script type="application/json" id="atlas-model">(.*?)</script>',
        html, re.DOTALL,
    )
    assert match, "expected self-contained offline JSON model"
    snapshot = json.loads(match.group(1))
    assert snapshot == model, "run tools/refresh_decision_atlas.py after editing JSON"
    assert "https://github.com/interzettel/kushluk/issues/170" in html
    assert "https://github.com/interzettel/kushluk/issues/157" in html
    assert "Drag to pan" in html
    assert "Impact links" in html
    assert not re.search(r'(?<![\w.])fetch\s*\(', html)
    assert 'src="http' not in html and "google-analytics" not in html

def test_github_native_mermaid_diagram_includes_every_node():
    doc = DIAGRAM.read_text(encoding="utf-8")
    assert doc.count("```mermaid") >= 2
    assert "ADR 0013" in doc and "R6 #171" in doc
    for n in load()["nodes"]:
        assert re.search(r"(?m)^  " + re.escape(n["id"]) + r'\["', doc), n["id"]
        assert f"https://github.com/interzettel/kushluk/issues/{n['issue']}" in doc

def test_viewer_javascript_parses_with_node_when_installed(tmp_path):
    node = shutil.which("node")
    if not node:
        return  # model/HTML structural checks are still unconditional
    html = VIEWER.read_text(encoding="utf-8")
    match = re.search(r'<script>\s*(\(\(\)=>\{.*?\}\)\(\);)\s*</script>', html, re.DOTALL)
    assert match, "viewer javascript bundle missing"
    script = tmp_path / "viewer.js"
    script.write_text(match.group(1), encoding="utf-8")
    result = subprocess.run([node, "--check", str(script)], capture_output=True,
                            text=True, timeout=20)
    assert result.returncode == 0, result.stderr


def test_mapped_impact_ids_match_existing_feature_and_task_authorities():
    from importlib.util import spec_from_file_location, module_from_spec
    catalog = (ROOT / "docs" / "FEATURE_CATALOG.md").read_text(encoding="utf-8")
    ledger = (ROOT / "docs" / "WORK_LEDGER.md").read_text(encoding="utf-8")
    feature_ids = set(re.findall(r"(?m)^\\| (F-\\d{3}) \\|", catalog))
    task_ids = set(re.findall(r"(?m)^- \\[.\\] \\*\\*([A-Z]+(?:-[A-Z]+)*-\\d+)", ledger))
    assert len(feature_ids) == 32
    assert len(task_ids) == 90
    assert len([x for x in re.findall(r"(?m)^- \\[x\\] \\*\\*([A-Z]+(?:-[A-Z]+)*-\\d+)", ledger)]) == 26
    for n in load()["nodes"]:
        impact = n.get("impact")
        assert impact is not None, n["id"]
        assert set(impact) == {
            "accepted_adrs", "feature_ids", "work_ledger_task_ids",
            "evidence_gates", "release_milestones"
        }
        assert set(impact["feature_ids"]) <= feature_ids, n["id"]
        assert set(impact["work_ledger_task_ids"]) <= task_ids, n["id"]
        assert all(x in {f"G{j}" for j in range(1, 9)} for x in impact["evidence_gates"])
    assert "ADR 0013" in next(x["impact"]["accepted_adrs"] for x in load()["nodes"] if x["id"] == "length")


def test_snapshot_refresh_tool_is_read_only_in_check_mode():
    import subprocess, sys
    script = ROOT / "tools" / "refresh_decision_atlas.py"
    r = subprocess.run([sys.executable, str(script), "--check"],
                       text=True, capture_output=True, timeout=15)
    assert r.returncode == 0, r.stderr + r.stdout
