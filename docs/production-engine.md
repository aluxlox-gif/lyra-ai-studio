# LYRA AI Studio — Cinematic Production Engine

## Phase 1 status: foundation only

This phase adds a small, provider-neutral production domain without replacing the existing engine registry, Voicebox adapter, Hermes bridge, Telegram controller, or PWA.

### Implemented

- Pydantic request/response contracts for production projects.
- SQLite schema for projects and future production jobs.
- Project create/read persistence methods.
- Protected project endpoints using `X-Lyra-Production-Token`.
- Health endpoint that reports the actual capability boundary.
- Isolated tests for project persistence.

### Explicitly not implemented yet

- Script generation, premise design, hook generation, or retention scoring.
- Character/scene bible generation or reference-image consistency.
- Image or generative-video provider adapters.
- Voice generation through the production pipeline (existing Voicebox endpoint is retained).
- FFmpeg rendering, subtitles, or final film assembly.
- Background workers, retries, cancellation, or job execution.
- PWA and Telegram production workflows.

The health response reports `worker_enabled: false` so a queued job cannot be mistaken for a running generation task.

## API

All project endpoints require the `X-Lyra-Production-Token` header.

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/production/health` | Capability and worker status |
| POST | `/api/production/projects` | Create a project |
| GET | `/api/production/projects/{project_id}` | Read a project |

Example project payload:

```json
{
  "title": "Episode 01",
  "description": "A short illustrated mystery",
  "language": "id",
  "aspect_ratio": "9:16",
  "visual_style": "cinematic illustration",
  "target_duration_seconds": 90,
  "metadata": {"genre": "mystery"}
}
```

## Storage and deployment boundary

SQLite uses Python's standard library; no database server or paid API is required. The default database path is `data/production.sqlite3` for local runs. On Vercel, the fallback path is `/tmp/lyra-production.sqlite3` so app import does not attempt to write into the read-only deployment bundle; `/tmp` is ephemeral and is not durable storage. Production deployment must configure a persistent volume/path before relying on stored projects. Do not assume serverless local disk is durable.

The token is a server-side secret. Do not place it in frontend JavaScript, a public PWA bundle, Telegram messages, or a committed real environment file. A later client integration must use a suitable authenticated backend/session flow rather than exposing this shared token.

## Next phases

1. Phase 0 completion: pin and verify upstream source revisions, licenses, and model/asset terms before copying any implementation.
2. Phase 2: Story Intelligence contracts and deterministic validation, followed by configurable local/provider adapters.
3. Phase 3: Character Bible, location Bible, storyboard, shot list, and continuity validation.
4. Phase 4: optional image provider adapter (ComfyUI/local endpoint first; no assumption of phone-side GPU capability).
5. Phase 5: narration adapter using the retained Voicebox integration and explicit Edge-TTS fallback status.
6. Phase 6: FFmpeg-based illustrated-video assembly, camera-motion templates, captions, and audio mixing.
7. Phase 7: optional generative-video providers.
8. Phase 8: authenticated PWA and Telegram orchestration, observability, and release tests.

Each provider must declare availability, requirements, license, network use, and cost. No provider may be represented as free or offline unless its actual execution path supports that claim.
