# LYRA Automation Roadmap

This roadmap began as the `ROADMAP.md` of the standalone
`lyra-ai-automation-center` repository and was folded into LYRA AI
STUDIO on 2026-11-19, completing the consolidation of the three
LYRA repositories into one codebase. The original repository
remains as the record of the plan; this document is the living
version, with each item mapped to what the studio actually has.

## Vision

A modular AI automation system that coordinates AI agents,
processes messages, and connects supported services through
official APIs — prioritizing free-tier services, reusable
components, security, and mobile-friendly management.

## Core principles

- Reuse existing projects instead of rebuilding from scratch.
- Keep components modular and independently maintainable.
- Prefer free services without requiring a payment card.
- Never commit API keys, passwords, access tokens, or private
  credentials.
- Use official APIs and respect each platform's terms and rate
  limits.
- Test each component before connecting it to production services.
- Require human approval for sensitive or high-impact actions.

## Architecture, mapped to the studio

| Automation Center layer | Studio equivalent | Status |
| --- | --- | --- |
| AI Core | Engine registry, engine adapters, Hermes bridge | Partial: adapters exist; only Voicebox generation is verified end to end |
| Automation Engine | — (triggers and workflows not built yet) | Planned |
| Integration Layer | Telegram controller (`bot.py`) | Done for Telegram; WhatsApp Business, Messenger, TikTok Shop, Shopee remain future, subject to official API access |
| Memory and Storage | — | Planned: store only what is required, with access controls and retention rules |
| Monitoring and Safety | Internal-token auth on protected endpoints, Telegram admin allowlist, test suite and CI | Partial: no failure tracking or duplicate-event protection yet |

The automation center's original Telegram bot skeleton
(`/start`, `/help`, canned replies) is fully superseded by the
studio's Telegram controller, which adds the admin allowlist,
backend status commands, Manual Create routing, and protected
Voicebox audio delivery.

## Implementation phases

- Phase 1 — Prepare the repository and document requirements.
  **Done**: all LYRA work now lives in this repository.
- Phase 2 — Audit reusable GitHub projects and their licenses.
  **Pending.**
- Phase 3 — Select a suitable free or low-cost runtime.
  **Partial**: Railway configuration exists (`railway.toml`);
  final runtime choice still open.
- Phase 4 — Build and test one Telegram integration.
  **Done**: controller built, covered by the test suite, and the
  Voicebox route verified against a live (mock) service.
- Phase 5 — Add AI processing and controlled automatic responses.
  **Partial**: Manual Create routes prompts by intent; only the
  audio route produces output today, and responses stay
  human-triggered.
- Phase 6 — Expand to additional officially supported platforms.
  **Pending** official API access for each platform.
- Phase 7 — Improve reliability, monitoring, and deployment.
  **Pending**: see Monitoring and Safety above.

## Constraints (unchanged from the original roadmap)

- Primary management device: Android phone.
- Windows 10: fallback when technically necessary.
- Budget: prioritize free services; no paid hosting or
  payment-card requirement unless explicitly approved.
- Availability: continuous 24/7 operation is a goal, not a
  guarantee of free-tier services.

## Security rules (unchanged)

- Never store secrets in source files; use environment variables
  or the hosting provider's secret manager.
- Do not publish private customer messages or personal
  information.
- Validate incoming webhooks and prevent duplicate event
  processing.
- Keep automatic actions limited until testing is complete.
