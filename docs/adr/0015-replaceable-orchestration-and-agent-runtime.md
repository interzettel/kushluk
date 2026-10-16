# ADR 0015 — Orchestration and agent runtime are replaceable

**Status:** Accepted

## Context

Kushluk may be started and coordinated by many different systems: n8n, Activepieces, Windmill, Temporal, a local scheduler, Hermes Agent, OpenClaw, ChatGPT, Apple Shortcuts, or future tools.

None of those should become the product architecture. The newspaper must continue to work if the orchestration layer or agent runtime is replaced.

The same principle applies to design integrations. Canva and Adobe/InDesign can be useful authoring or template adapters, but Kushluk must not require a specific hosted design product to generate the daily edition.

## Decision

Kushluk owns a provider-independent **core edition engine**. External orchestrators and agents call that engine through stable contracts rather than containing the editorial or layout logic themselves.

The core boundary should expose operations equivalent to:
- `generate_edition`;
- `preview_edition`;
- `render_edition`;
- `print_edition`;
- `deliver_edition`;
- `edition_status`;
- connector/source health and diagnostics.

These contracts may be surfaced through CLI, local HTTP API, MCP tools, or equivalent adapters. The canonical request/response models remain owned by Kushluk.

### Responsibility split

**Workflow/orchestration layer**
- schedules runs;
- reacts to triggers;
- coordinates retries and notifications;
- supplies explicit run context such as morning intent;
- calls Kushluk core operations;
- does not own editorial ranking, layout geometry, or publication state.

**Agent runtime**
- may interpret natural-language intent;
- may choose which Kushluk operation to call;
- may gather optional context through approved connectors;
- must not become the sole repository of durable product logic.

**Kushluk core**
- normalises sources;
- performs editorial ranking, clustering, verification and cuts;
- creates the canonical publication model;
- resolves assets into a provider-independent asset manifest;
- applies deterministic layout templates;
- validates geometry and overflow;
- produces logical pages and print-ready output;
- archives the edition and run state.

**Design-tool adapters**
- may export or autofill approved Canva/InDesign templates;
- may support human design iteration or alternate production workflows;
- are optional adapters, not required dependencies of the daily core loop.

## Layout and image placement

Daily placement is deterministic after editorial decisions are final.

The publication model should reference image candidates and an explicit asset manifest containing, where applicable:
- source/reference;
- local or retrievable asset identifier;
- credit/attribution;
- aspect ratio and intrinsic dimensions;
- focal point or crop hint;
- usage/copyright state;
- alt text;
- target slot role.

The layout engine, not the orchestrator or free-form agent, places assets into named template slots using deterministic fit/crop rules. An agent may select or rank image candidates, but it does not freely redesign the page at print time.

## Rationale

This keeps Kushluk open, self-hostable and portable while allowing users to choose their preferred automation or agent stack.

It also avoids coupling production reliability to the current capabilities, pricing, quotas or API surface of one orchestration or design vendor.

## Consequences

- n8n is an optional orchestrator, not a core dependency.
- Hermes, OpenClaw, ChatGPT and similar systems can act as alternative agent front ends if they can call the same Kushluk contracts.
- Apple Shortcuts may trigger the same API/CLI path for personal automations.
- Canva/InDesign integrations remain useful for template authoring, autofill, review and export, but the baseline edition must still render without them.
- New orchestration or design integrations should be implemented as adapters rather than by moving core logic into vendor-specific workflows.
- MCP is a useful interoperability surface, not the only one.

## Revisit conditions

Revisit if one external runtime becomes intentionally mandatory for the product, if the core contracts prove too narrow for real workflows, or if a future publication engine can provide deterministic layout guarantees more reliably than the current renderer while preserving provider independence.