# Bounded review prompt generator (Phase I/IV preparation)

This is a **non-operative, offline** prompt builder extracted and updated from draft [strategy PR #177](https://github.com/interzettel/kushluk/pull/177). It uses the **already merged** public source `site/decision-atlas/decision-atlas.json`, not the unmerged copy in `docs/strategy/`. The source JSON is a dated proposal snapshot, not automatically refreshed and not a founder decision.

To prepare **one identical source-facts packet** per model, from your dedicated Kushluk checkout:

```bash
python tools/prepare_decision_review.py --node length --reviewer 'ChatGPT Work' > /tmp/kushluk-length-chatgpt.md
python tools/prepare_decision_review.py --node length --reviewer 'Claude Code' > /tmp/kushluk-length-claude.md
python tools/prepare_decision_review.py --node length --reviewer 'Local DeepSeek' > /tmp/kushluk-length-deepseek.md
```

Other discussion nodes include `prompt`, `mail`, `supplements`, and `source-rights`. The script generates stdout only. It does **not** call ChatGPT, Claude or DeepSeek; read/write GitHub issues; change accepted ADRs; access inboxes/printers; use A2A; or transmit any source material. Reviewer names are **self-reported text**, never proof of authentic participation. The actual model must inspect its real repository HEAD and original sources before using the generated prompt, and the owner must authorize any external/public action separately.

For startup identity, permissions, and handover rules read [the three separate restart prompts](../../coordination/README.md), [the constitution](CONSTITUTION.md), and the [original facts-only source packet](../../coordination/rounds/2026-10-19-wave1/SOURCE_PACKET.md). Do not use this utility to fake an independent second review by ChatGPT. No changes to Phase I Agent Council's separate implementation.

**Verification:** `python -m pytest -q tests/test_prepare_decision_review.py`; GitHub CI checks on the exact PR head. Pulling this portable tool from PR #177 does not approve the rest of that strategic draft.
