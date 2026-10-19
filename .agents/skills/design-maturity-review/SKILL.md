---
name: design-maturity-review
description: 'Critique, audit, evaluate, or compare the maturity and quality of any designed object: websites, apps, software interfaces and architectures, furniture, buildings, spaces, identities, typography, artifacts, services, systems, and experimental or generative work. Use when asked why a design feels raw, unresolved, polished, coherent, expressive, generic, unfinished, or mature; produce evidence-grounded, domain-aware judgments and concrete revisions without imposing a minimalist aesthetic.'
license: MIT
metadata:
  version: '1.0.0'
---

# Design Maturity Review

Review design as **the resolution of relationships, purposes, consequences, and expressive intentions**, not as a surface-polish competition. An expressive, asymmetric, complex, rough, or experimental object can be mature. A spotless, conventional object can be unresolved.

**Core distinction:** Eliminate *unresolved decisions*, not necessarily irregularity. Evaluate **resolution** (how deliberately the design works) separately from **character** (whether its expression is distinctive and appropriate).

## When to use

Activate for a review, diagnosis, comparison, maturity assessment, design critique, design direction, or an explanation of why a work does or does not feel finished. Applicable to visual, interactive, physical, spatial, organizational, code-based, and hybrid designs. A review is **not authorization to redesign, modify files, deploy, or publish**; do those only if requested.

## Review method

### 1. Establish the design's actual job

Identify, as far as evidence allows:

- **Object / boundary:** What exactly is being reviewed (artifact, component, system, experience, implementation, concept)?
- **Intent / audience:** What is it trying to enable, communicate, or make possible? For whom? Include people affected but not intended as direct users.
- **Stage:** Sketch, experimental study, prototype, implementation, production, established/aging object. An unresolved sketch is not a failed finished product.
- **Context / constraints:** Physical and digital environments; accessibility; regulations; budget, material, time, technical, environmental, operational constraints.
- **Decision criterion:** What does success mean here? Utility, expression, trust, navigation, maintainability, longevity, emotion, or another goal?

Use the provided brief and evidence first. If intent is absent, state a **working assumption**, offer the most plausible alternative interpretation, and keep the evaluation conditional. Ask only for missing information that genuinely blocks a useful review; otherwise proceed with stated limits. Do not invent an audience, design brief, test outcome, building performance, or engineering requirement.

### 2. Establish evidence, not vibes

Inspect relevant supplied artifacts, then available live/source evidence if permitted and useful. Seek the *smallest additional evidence* likely to change the judgment. Review at **three scales** where relevant:

1. **Detail:** micro-interactions, joins, typography, tolerance, naming, APIs, transitions, feedback, material finishing.
2. **Whole:** hierarchy, anatomy, proportions, spatial sequence, workflows, assembly, component relationships.
3. **System in context:** surrounding product/service/ecology, deployment, environment, other users, maintenance, time.

For any meaningful claim, distinguish:

- **Observed** — directly supported by inspected image, artifact, measured data, tested behavior, or cited source.
- **Inferred** — plausible interpretation; explain what observation supports it and what would falsify it.
- **Preference** — an aesthetic or strategic choice contingent on taste/brief; never masquerade as universal fact.
- **Unknown / untested** — cannot be concluded from the material; specify how to test, rather than treating as failure.
- **Not applicable** — dimension demonstrably irrelevant to this object.

Link observations to specific regions, states, lines, routes, views, photos, drawings, components, or metrics when available. A rendering is not evidence of build quality; a screenshot is not evidence of usability; a code diff is not proof of real-world reliability. Never invent tests or claim a conformance audit that was not performed.

For detailed expectations and evidence by medium, read [references/domain-lenses.md](references/domain-lenses.md). For evidence handling and review confidence, read [references/evidence-protocol.md](references/evidence-protocol.md).

### 3. Test with two opposing intellectual lenses

Run both; neither is allowed to dominate by default.

**Discipline / resolution lens** (inspired by Vignelli, Rams, Rand, Ive):
- Do form, construction, interaction, and meaning reinforce a coherent idea?
- Is anything present merely because it is fashionable, easy, or ornamental?
- Where do optical, spatial, behavioral, or structural relationships break down?
- Are details, edge cases, transitions, and real use carefully considered?
- Does the design honestly communicate what it can and cannot do?

**Character / experimentation lens** (inspired by Scher and Carson):
- Which deviations, tensions, irregularities, and surprises are expressive **assets**?
- Has refinement made it conventional, generic, sterile, or overcontrolled?
- Does the work have a particular voice? Is that voice appropriate to its context?
- Could an apparently awkward element be a deliberate generator of meaning?
- If we remove the 'imperfection,' do we also remove what makes the work memorable?

**Adjudicate tension.** Do not apply Rams's restraint to erase an intentional Carson-like expressive device. Do not use Scher's celebration of risk to excuse an avoidable accessibility failure or dangerous construction detail. When both options are defensible, describe the trade-off and who benefits or loses.

### 4. Evaluate seven dimensions, contextually

Use these universal **questions**, not a universal aesthetic prescription. Mark each **Strong / Mixed / Weak / Unknown / N/A** unless the user requests a quantified rubric.

1. **Purpose and appropriateness** — Does it serve the actual task, audience, and environment? Does the form suit the intended meaning?
2. **Understanding and use** — Is it legible, learnable, usable, and navigable where those qualities matter? Are state, feedback, and cause/effect intelligible?
3. **Systemic coherence** — Do parts, flows, proportions, concepts, and constraints reinforce one another? Are variations governed by intelligible rules?
4. **Craft and transitions** — Are critical junctions and details resolved: alignments, physical joins, interfaces, visual rhythm, material-to-form relationships, error states, component boundaries?
5. **Expressive conviction** — Does it have a distinctive, purposeful point of view? Are novelty, tension, and restraint chosen, rather than accidental?
6. **Robustness across contexts and time** — Does it adapt to scale, edge cases, change, repair, maintenance, and real conditions appropriate to its type and stage?
7. **Responsibility and consequences** — Does it address relevant access, safety, privacy, cultural/social impact, inclusion, ecological footprint, and lifecycle costs?

A dimension can be important but **unobservable**. Record that; never fill the evidence gap with a flattering or punitive score. See [references/rubric.md](references/rubric.md) for operational anchors and optional scoring.

### 5. Diagnose *why*, before prescribing *what*

For each material weakness, identify:

- **Symptom** — the precise point of friction / incoherence and where it was observed.
- **Underlying relationship** — e.g., hierarchy competes with reading order; joint conflicts with material behavior; abstraction leaks into API ergonomics; architectural procession conflicts with accessibility.
- **Consequence** — who is affected, how often, what risk or lost opportunity, and confidence.
- **Likely cause** — if identifiable, explicitly marked as inference.
- **Counter-explanation** — could the issue be intentional, context-dependent, or caused by incomplete evidence?

Use a causal ladder: visible detail -> broken relationship -> failure of purpose or expression. Avoid advice like 'make it pop,' 'add whitespace,' 'simplify,' or 'make it premium' without a concrete mechanism.

### 6. Preserve, improve, validate

First name **what must be protected**: a strong structure, expressive irregularity, material honesty, efficient workflow, conceptual clarity, etc. Then prioritize **up to three interventions** with:

- targeted change (specific enough to implement or prototype);
- expected improvement and why;
- what may be lost / trade-off;
- a **verification test** (comparison at two scales, user task, physical mockup, instrumented test, load test, site walkthrough, etc.).

Distinguish **blockers** (safety, legal, accessibility, fundamental function, security, severe operational failure) from **craft deficits** and **strategic/style choices**. Never let attractive expression compensate for a verified critical harm. Conversely, do not mislabel subjective style disagreement as a defect.

For ambiguous directions, offer two credible alternatives when they entail genuinely different priorities, rather than a single style-biased correction. Review the consequences of your recommendations; a purported refinement must not destroy the primary design idea.

### 7. Deliver the review

Default concise structure (adapt to the user's requested depth and evidence):

1. **Verdict and scope:** One clear sentence on current resolution/character, with reviewed stage and confidence. Avoid empty compliments.
2. **Worth preserving:** 1–3 evidence-based strengths, including meaningful expressive decisions.
3. **Where it feels unresolved:** 1–3 prioritized specific issues; cite/locate evidence; indicate observed vs inferred and severity.
4. **Next design moves:** Ranked interventions with intended effect, trade-off, and acceptance test.
5. **Unknowns / limits:** Only the important ones that would materially revise the assessment.

For a fast review, use a few cohesive paragraphs. For detailed audits, use a matrix with `dimension | judgment | evidence | confidence`, then interventions. If the user explicitly asks for a numerical maturity score, apply the optional scoring rules in [references/rubric.md](references/rubric.md). **Never invent a 'maturity percentage' from aesthetics alone.**

### 8. Check the critique itself

Before finalizing, ask:

- Have I confused **cleanliness**, **familiarity**, **expensiveness**, **novelty**, or **personal taste** with maturity?
- Did I inspect relationships at detail / whole / context, rather than isolated attractive components?
- Did I assess functionality without access to relevant behavior, or construction without field evidence?
- Did I overfit principles from one discipline to another?
- Am I defending a distinctive choice that harms people, or eliminating a distinctive choice without reason?
- Is each recommended action falsifiable by an appropriate test?
- Would a design critic with opposing aesthetics recognize my observations as fair?

## Additional references (load only when useful)

- [references/rubric.md](references/rubric.md) — anchors, calibrated scoring, severity, disagreement handling.
- [references/domain-lenses.md](references/domain-lenses.md) — checks for digital interfaces, software, products, architecture, identities, services, data/generative work.
- [references/evidence-protocol.md](references/evidence-protocol.md) — evidence thresholds, multimodal limits, audits, standards, and test suggestions.
- [references/intellectual-roots.md](references/intellectual-roots.md) — source-grounded synthesis of Vignelli, Rams, Rand, Scher, Carson, Ive, Norman; no invented quotations.
- [references/examples.md](references/examples.md) — contrasting hypothetical review examples and anti-patterns.

## Non-goals

Do not claim the work is 'objectively beautiful.' Do not award universal grades based on resemblance to celebrated designers, expensive production, or current trends. Do not imply professional certification (structural, fire safety, medical, ergonomic, cyber, legal, accessibility) without specialist methods and substantiated testing. Do not turn an evaluation request into unapproved edits.