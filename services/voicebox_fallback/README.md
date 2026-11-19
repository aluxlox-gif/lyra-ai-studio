# Voicebox Fallback Service

A drop-in replacement / backup for a Voicebox server, for use
with LYRA AI STUDIO. It speaks the same API the studio's
VoiceboxAdapter already uses, but synthesizes speech with
[edge-tts](https://pypi.org/project/edge-tts/) (free Microsoft
Edge neural voices) instead of Voicebox voice profiles.

## Run it

```bash
cd services/voicebox_fallback
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 17493
```

Port 17493 is the studio's default `VOICEBOX_BASE_URL`
(`http://127.0.0.1:17493`), so if this service runs on the same
machine as the LYRA backend, no URL change is needed at all.

## Point LYRA at it

```env
VOICEBOX_BASE_URL=http://127.0.0.1:17493
VOICEBOX_DEFAULT_PROFILE_ID=id-gadis
```

Profiles:

| Profile id | Voice | Language |
| --- | --- | --- |
| `id-gadis` | id-ID-GadisNeural (female) | Indonesian |
| `id-ardi` | id-ID-ArdiNeural (male) | Indonesian |
| `en-aria` | en-US-AriaNeural (female) | English (US) |
| `en-guy` | en-US-GuyNeural (male) | English (US) |

A full edge-tts voice name (e.g. `id-ID-GadisNeural`) also works
as `profile_id`. An unknown profile id — for example a real
Voicebox profile id, when this service runs purely as a backup —
falls back to the default voice for the requested language, so
generation keeps working instead of failing.

If the host reaches the internet through an HTTP proxy, set
`EDGE_TTS_PROXY` (e.g. `http://host:3128`) before starting the
service; otherwise it connects directly.

## Honest limits

- This is a stand-in, not a Voicebox clone: voices are Microsoft
  neural voices, not your custom Voicebox profiles.
- Synthesis needs internet access to Microsoft's speech service;
  it is a free, unofficial service with no uptime guarantee.
- Best used as a backup for when the real Voicebox is down, or
  as a starter engine until Voicebox is deployed.
