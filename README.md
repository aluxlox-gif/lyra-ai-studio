# LYRA AI STUDIO

Unified AI Image, Video, and Voice Production Platform.

## Offline-first & Android

LYRA is being built **offline-first**: the web app is an installable
PWA whose shell and basic features (dashboard, engine list,
settings) open without internet, showing the last synced engine
data while offline. API keys and service URLs are entered later,
on-device, on the app's **Pengaturan** (Settings) page — they are
stored only in the device's localStorage. Full guide, including
running the whole stack on a phone with Termux:
[docs/android.md](docs/android.md).

## Telegram Controller and Manual Create

The Telegram bot runs as a **separate process** from the FastAPI backend.
It calls the LYRA API; it does not host AI engines itself.

### Commands and menu

- `/start` — main menu
- `/help` — command help
- `/status` — backend and engine summary
- `/engines` — engine registry
- `/voice` — Voicebox connectivity check
- `/info` — application information
- `🔨 MANUAL CREATE` — enter a free-form content instruction

Manual Create currently recognizes image, video, and audio intent from words
in the prompt. The audio route calls the protected Voicebox generation API and
returns its audio bytes to Telegram. Image and video prompts are recognized,
but their generator providers are not implemented or configured yet; the bot
will say so rather than pretend a file was created.

### Configure and run

1. Install dependencies: `pip install -r requirements.txt`
2. Set `TELEGRAM_BOT_TOKEN` to the token from BotFather.
3. Set `ADMIN_IDS` to your Telegram numeric user ID. Multiple IDs may be
   comma-separated. The bot refuses to start if this allowlist is empty.
4. Set `LYRA_API_BASE_URL` to the deployed FastAPI base URL.
5. Configure the same strong random value as `LYRA_TELEGRAM_API_TOKEN`
   in both the FastAPI backend and Telegram controller environments.
6. Configure `VOICEBOX_BASE_URL` so the FastAPI backend can reach Voicebox,
   and set `VOICEBOX_DEFAULT_PROFILE_ID` to an existing Voicebox profile ID.
7. Start the controller: `python bot.py`

The backend exposes `POST /api/engines/voicebox/generate`. It requires the
`X-Lyra-Internal-Token` header and a configured Voicebox profile. The endpoint
returns the generated audio as a file response. Do not commit real bot tokens,
API tokens, profile credentials, or other secrets.

Keep the FastAPI backend, Voicebox service, and Telegram long-polling
controller as separate processes/services unless your deployment architecture
explicitly provides private network access between them.

## Engine status and next work

- Voicebox: adapter has a speech-generation method, verified end to
  end against a mock service. A free drop-in fallback backed by
  edge-tts lives in `services/voicebox_fallback/` (same API, same
  default port) for use as a backup or starter engine.
- Image Studio: generator provider not yet implemented.
- Video Studio: generator provider not yet implemented.
- OpenMontage: provider integration not yet implemented.
- Hermes: adapter and bridge are retained but not used by Manual Create yet.
- Story Engine: folded in from the former lyra-story-engine repository.
  Pipeline scaffold, registry entry, and design notes
  (`docs/story-engine.md`) are in place; stage providers are not
  implemented yet.
- Automation: the LYRA AI Automation Center roadmap now lives in
  `docs/automation-roadmap.md`, mapped to what the studio has
  actually built. Its Telegram bot skeleton is superseded by this
  repository's controller; the Automation Engine, Memory/Storage,
  and Monitoring layers are still planned.

The image/video providers must be selected and configured before those prompt
types can return actual media files in Telegram. Hermes remains deferred until
the base Telegram workflows are verified.

## Cinematic Production Foundation (Phase 1)

The first production foundation is available under `/api/production`:

- `GET /api/production/health` — reports implemented capabilities and explicitly reports that background workers are not enabled yet.
- `POST /api/production/projects` — creates a persisted production project.
- `GET /api/production/projects/{project_id}` — retrieves a project.

Project endpoints require the `X-Lyra-Production-Token` header, configured with `LYRA_PRODUCTION_API_TOKEN`. SQLite is used by default at `data/production.sqlite3` locally. Vercel falls back to `/tmp/lyra-production.sqlite3` to avoid writes into the read-only deployment bundle, but `/tmp` is ephemeral. Set `LYRA_PRODUCTION_DB_PATH` to a persistent mounted path on a host that supports durable volumes before relying on stored projects.

This phase establishes project contracts and persistence only. It does not yet generate scripts, images, narration, or video, and it does not run background jobs. Existing Voicebox, Hermes, Telegram, and frontend flows remain separate and unchanged.

See [docs/production-engine.md](docs/production-engine.md) for the implementation boundary and next phases.
