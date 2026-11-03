# LYRA AI STUDIO

Unified AI Image, Video, and Voice Production Platform.

## Telegram Controller (initial integration)

The Telegram bot runs as a **separate process** from the FastAPI backend.
It calls the existing LYRA API; it does not run image/video/voice engines.

### Commands

- `/start` — main menu
- `/help` — command help
- `/status` — backend and engine summary
- `/engines` — engine registry
- `/voice` — Voicebox connectivity check
- `/info` — application information

The bot currently exposes read-only status and health checks. Image Studio,
Video Studio, OpenMontage, project storage, job execution, and speech generation
are not activated by this controller yet.

### Configure and run

1. Install dependencies: `pip install -r requirements.txt`
2. Set `TELEGRAM_BOT_TOKEN` to the token from BotFather.
3. Set `ADMIN_IDS` to your Telegram numeric user ID. Multiple IDs may be
   comma-separated. The bot refuses to start if this allowlist is empty.
4. Set `LYRA_API_BASE_URL` to the deployed FastAPI base URL.
5. Start the controller: `python bot.py`

Do not commit real bot tokens or other secrets. Configure them as environment
variables in the hosting service. Keep the FastAPI backend and Telegram
long-polling controller as separate services.

## Hermes

The Hermes adapter and bridge are retained in this branch but are not used by
the initial Telegram controller. Hermes integration will be activated only
after the base Telegram commands are tested.
