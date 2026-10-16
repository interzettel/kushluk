# ADR 0014 — Morning intent is ephemeral editorial input

**Status:** Accepted

## Context

A personalised newspaper should not depend only on a durable interest profile. Some mornings the user has a temporary concern, question, event, mood, or topic that should shape that day's edition without permanently changing their profile.

A short spoken or typed briefing is a natural way to express this context.

## Decision

Kushluk may accept an optional **morning intent** before candidate ranking.

Morning intent can be entered by voice or text and is normalised into temporary editorial cues such as:
- topics to emphasise;
- topics to de-emphasise;
- questions the user wants answered;
- events or concerns that matter specifically today;
- desired reading density or tone for the current edition.

Morning intent affects candidate retrieval, ranking, synthesis, and cut decisions for the current edition only.

It does **not** become durable user-profile data unless the user explicitly chooses to save it as a lasting preference.

Morning intent must not bypass source verification, privacy boundaries, or required practical content such as calendar commitments.

## Rationale

This gives the user direct editorial agency without forcing preference maintenance or making the system infer durable traits from transient speech.

It also creates a useful interaction model: the user can briefly talk to the editor, then let Kushluk do the research and composition work.

## Consequences

- Voice input requires speech-to-text before editorial normalisation.
- The canonical request model needs an edition-scoped `morning_intent` field or equivalent.
- Ranking should record when an item was promoted or demoted because of morning intent.
- The archive may record the existence of an edition cue, but raw voice/audio should not be retained by default.
- Durable preference updates require a separate explicit action.

## Revisit conditions

Revisit if users consistently want morning intent remembered automatically, if speech privacy requirements change, or if the feature creates unstable ranking behaviour.
