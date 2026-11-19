# LYRA AI STUDIO

Unified AI Image, Video, and Voice Production Platform.

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

- Voicebox: adapter has a speech-generation method; live service, profile,
  and response format still need runtime verification.
- Image Studio: generator provider not yet implemented.
- Video Studio: generator provider not yet implemented.
- OpenMontage: provider integration not yet implemented.
- Hermes: adapter and bridge are retained but not used by Manual Create yet.

The image/video providers must be selected and configured before those prompt
types can return actual media files in Telegram. Hermes remains deferred until
the base Telegram workflows are verified.
