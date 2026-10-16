# Architecture

## Architectural intent

Kushluk separates **personal context**, **research/editorial intelligence**, and **publication/printing** so that privacy, reliability, and provider independence survive changes in vendors.

## High-level pipeline

```text
Trigger / Orchestrator
  -> Run Context + Optional Morning Intent
  -> Connectors / Personal Data Plane
  -> Candidate Normalisation
  -> Research / Verification
  -> Editorial Engine
  -> Media Asset Resolution
  -> Publication + Layout Manifest
  -> Deterministic Four-Page Renderer
  -> Layout / Asset Validator
  -> Print-Profile Imposition
  -> Print / Digital Delivery
  -> Edition + Run Archive
```

## Orchestration boundary

Kushluk exposes a stable run boundary that may be triggered by the CLI, an OS scheduler, n8n, Apple Shortcuts, or a future service. Orchestrators may schedule, pass edition-scoped intent, pause/reprint, and observe status; they must not own ranking rules, canonical schemas, layout geometry, or archive state.

The core run should be idempotent for a date/edition so retries do not silently generate duplicate print jobs.

## Personal data plane

The personal data plane is the user's durable state.

It may run:
- on a local computer;
- on a home server;
- on a user-controlled VPS/cloud account.

It stores or mediates:
- preferences;
- configured home/default location;
- calendars/tasks;
- source configuration;
- user-interest model;
- edition history;
- secrets/connector tokens through an appropriate secrets mechanism;
- local feedback signals.

By default, this state does not live on Kushluk-operated infrastructure.

## Public research plane

Public news, weather, RSS, websites, and other non-personal material may be fetched or processed using external services.

The research plane receives the minimum personal context required to do its job. Prefer generic research requests over uploading rich private profiles.

Example:

Good:
> Find the most material AI developments from the last 24 hours.

Avoid by default:
> Here is the user's full private behavioural history; decide what they like.

## Connectors

Connectors translate provider-specific data into canonical internal forms.

Expected connector families:
- calendar;
- tasks;
- weather;
- RSS/news;
- newsletter/email;
- X/social;
- Reddit/Hacker News;
- external AI briefings;
- print;
- digital delivery.

Providers are replaceable. Canonical models must not expose provider-specific assumptions upstream.

## User model

The user model is a first-class local component, independent of any LLM provider.

It may include:
- explicit interests;
- durable topic affinities;
- preferred languages and language-learning intent;
- reading-density preferences;
- source affinities;
- negative preferences;
- recent-topic fatigue;
- lightweight privacy-preserving feedback.

The model must be inspectable and deletable.

## Editorial engine

The editorial engine:
1. builds a candidate pool;
2. deduplicates and clusters;
3. verifies important factual claims;
4. scores candidates;
5. protects required practical content and serendipity;
6. decides what to cut;
7. emits a canonical publication model.

The renderer never performs editorial reasoning.

## Canonical publication model

The canonical edition should be representable as Markdown plus structured metadata, including four logical page identities and a layout manifest independent of the final printer profile.

Why:
- durable;
- human-readable;
- RAG/search friendly;
- easy to archive in Obsidian-like systems;
- provider/tool independent;
- convertible to HTML/PDF/e-reader formats.

Rendered HTML/PDF are derived products.

## Renderer and validator

Rendering should be deterministic.

Suggested initial stack:
- Python;
- Pydantic schemas;
- Jinja2 templates;
- CSS paged media;
- WeasyPrint for PDF;
- PDF/layout validation;
- CUPS/`lp` print adapter.

The validator enforces:
- four logical DIN A4 pages;
- page identity/order and page count;
- overflow;
- minimum readable typography;
- required blocks;
- image/asset suitability and effective print resolution;
- link/QR integrity where practical.

If validation fails, the editorial cut policy runs and rendering repeats.

## Media asset subsystem

The asset resolver manages source images/illustrations as typed assets with provenance, rights/usage state, attribution, dimensions, focal point, crop policy, and cache/archive identity. Layout slots consume these assets deterministically. Missing or unsuitable imagery must degrade to another asset or a text-led layout rather than blocking the edition.

## Print subsystem

The print layer receives four logical A4 pages and applies a physical profile. Initial profiles are A4 two-sheet duplex, A3 duplex half-fold booklet imposition (`4 | 1` / `2 | 3`), and single-sided A4 fallback.

The print adapter should:
- enumerate configured printer capabilities where possible;
- distinguish duplex-capable vs single-sided hardware;
- support Wi-Fi/network CUPS where reliable;
- preserve USB as a viable local fallback;
- surface printer offline / paper / job errors when the platform exposes them.

Do not assume printers can reliably infer paper stock or paper colour. Use named paper profiles instead.

## Delivery decision

A delivery-policy component decides among:
- print;
- email;
- later messaging;
- combinations.

Inputs may include:
- configured print location;
- travel/home state;
- printer availability;
- user pause state;
- explicit schedule overrides.

## Secrets

Secrets must never be committed.

Use:
- OS keychain/keyring where available;
- environment variables for development;
- local encrypted secret stores where appropriate.

## Deployment modes

### Local
Personal plane and publication pipeline run on the user's machine/home server.

### Self-hosted cloud
The user runs Kushluk in their own infrastructure.

### Managed cloud (future)
Kushluk operates infrastructure that processes user data. This is explicitly not equivalent to local-first mode and requires separate privacy, security, retention, and regulatory design.

## Observability

Default observability is local:
- structured logs;
- typed failures;
- generation timings;
- connector health;
- print job status.

No remote behavioural telemetry by default.
