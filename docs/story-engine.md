# Story Engine

Automated cinematic 2D illustrated film production using specialized
AI agents.

The Story Engine began as the standalone `lyra-story-engine`
repository and was folded into LYRA AI STUDIO on 2026-11-19 so the
LYRA engines live in one codebase. The original repository remains
as the concept record; new development happens here.

## Concept

A story idea enters the pipeline and a short illustrated film comes
out. Specialized agents handle one production stage each, and every
stage runs on an existing LYRA engine instead of a separate stack:

| Stage | What it does | Runs on |
| --- | --- | --- |
| Story Development | Premise, outline, and screenplay drafting | Hermes Agent |
| Storyboard | Scene breakdown and shot planning | Hermes Agent |
| Illustration | 2D illustrated frames for each shot | Image Studio |
| Narration | Voice-over for dialogue and narration | Voice Studio / Voicebox |
| Film Assembly | Scene sequencing, timing, and export | Video Studio / OpenMontage |

## Status

- Adapter scaffold: `app/engines/adapters/story_engine.py`
  (`StoryEngineAdapter`, engine id `story`).
- Registry: listed in `get_engine_status()` as `planned`,
  `connected: False`.
- Stage providers: none implemented yet. The adapter reports every
  stage as `pending` and does not pretend to produce a film.

## Next steps

1. Define the stage data contract (script format, shot list, asset
   references) shared by all five stages.
2. Implement Story Development on the Hermes bridge, since it only
   needs text in and text out.
3. Wire Narration to the Voicebox generation endpoint, the one
   engine route already verified end to end.
4. Choose the Image Studio provider; Illustration and Assembly stay
   blocked until image and video generation exist.
