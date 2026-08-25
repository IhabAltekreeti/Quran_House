# Quran House — Planned Architecture

> Planning document only. This is not a frozen architecture.

## Initial Pipeline

```text
Quran Content
     ↓
Content / Verse Layer
     ↓
Theme & Scene Selection
     ↓
Media Provider
     ↓
Recitation / Audio
     ↓
Video Composition
     ↓
Quality Guard
     ↓
MP4 Export
```

## Responsibility Boundaries

- **Content Layer:** retrieve and normalize verse, translation, and metadata.
- **Theme Layer:** define reusable visual layouts and theme configuration.
- **Media Layer:** obtain suitable background media from configured providers.
- **Audio Layer:** obtain and validate recitation audio.
- **Composition Layer:** render the final vertical video.
- **Quality Guard:** validate content, dimensions, timing, rendering, and required visual elements.
- **Export Layer:** produce the final user-facing video artifact.

## Architecture Rules

1. Keep components small and replaceable.
2. Do not introduce infrastructure before the current milestone requires it.
3. Do not allow one theme to dictate the entire rendering architecture.
4. Keep provider integrations behind clear boundaries where practical.
5. Prefer deterministic logic before adding AI.
6. Any architectural change that affects multiple components must be recorded in `docs/project-memory/DECISIONS.md`.

## Important Note

The architecture will be revised when implementation evidence proves that the current plan is insufficient. Planning documents must never be treated as proof that an implementation exists.
