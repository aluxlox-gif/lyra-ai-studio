# LYRA AI STUDIO

Unified AI workspace for image, video, and voice workflows.

## Self-hosted LYRA VOICEBOX CLOUD integration

LYRA AI STUDIO connects to the separately hosted Voicebox backend through its REST API. It does not use a third-party Voicebox URL or assume that Voicebox runs on the same host.

Configure these environment variables in the LYRA AI STUDIO deployment:

```env
VOICEBOX_BASE_URL=
VOICEBOX_API_KEY=
VOICEBOX_API_KEY_HEADER=X-API-Key
VOICEBOX_DEFAULT_PROFILE_ID=
VOICEBOX_TIMEOUT=30
```

- Keep `VOICEBOX_BASE_URL` empty until the user's own Voicebox backend is deployed and reachable.
- Set it to the base URL of that backend, without a trailing slash.
- The adapter sends `VOICEBOX_API_KEY` using the configured header (default: `X-API-Key`) when a key is provided.
- `VOICEBOX_DEFAULT_PROFILE_ID` must be an ID returned by the user's own Voicebox `GET /profiles` endpoint.
- Never commit real secrets. Use the hosting provider's environment-variable settings.

### Expected Voicebox API contract

| Method | Voicebox endpoint | Purpose |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/profiles` | List voice profiles |
| POST | `/generate` | Generate audio bytes |

The generate request body is JSON:

```json
{
  "text": "Teks yang akan diucapkan",
  "profile_id": "ID_PROFIL_DARI_VOICEBOX",
  "language": "id"
}
```

The `POST /generate` response must contain actual audio bytes, not a JSON placeholder.

### LYRA AI STUDIO endpoints

| Method | LYRA endpoint | Purpose |
|---|---|---|
| GET | `/api/engines/voicebox/health` | Voicebox connection status |
| GET | `/api/voice/profiles` | Proxy voice profiles |
| POST | `/api/voice/generate` | Proxy audio generation |
| GET | `/api/v1/health` | App health and dependency status |

If Voicebox has not been deployed yet, leave `VOICEBOX_BASE_URL` empty. The adapter reports `not_configured` instead of silently targeting localhost.

## Development

Install dependencies and run:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Run tests:

```bash
pytest -q
```
