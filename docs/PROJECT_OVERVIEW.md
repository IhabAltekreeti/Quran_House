# Quran House — Project Overview

## 1. Purpose

Quran House is a customizable Quran short-video generation project. Its purpose is to generate polished vertical 9:16 videos from Quran verses by combining authoritative Quran content, translations, verified recitation audio, background media, reusable visual themes, branding, and quality validation.

The long-term product direction is a reliable content-generation pipeline that can produce many visually consistent but customizable Quran videos suitable for short-form video platforms.

## 2. Product Vision

The project is intentionally broader than a single fixed video template. The core system should make it possible to create multiple visual styles without rewriting the underlying generation pipeline.

The intended experience is:

Selected verse
→ Quran text + translation
→ Recitation
→ Theme / scene selection
→ Background media
→ Video composition
→ Quality validation
→ Final MP4

Future automation may allow repeated generation from a defined set of verses and workflow orchestration tools.

## 3. Core Components

### Content Layer
Retrieves and normalizes Quran verse text, translation, and related metadata.

Quran-specific identity and metadata claims must be verified against authoritative source/API data rather than inferred from hardcoded IDs or filenames.

### Theme Layer
Defines reusable visual presentation configurations. A theme may control layout, typography, colors, animation, progress indicators, branding, and other presentation details.

A theme must not dictate the entire rendering architecture.

### Media Layer
Obtains suitable background media from configured providers. Pexels is the initial planned/used provider.

### Audio Layer
Retrieves and validates Quran recitation audio and handles timing/synchronization requirements.

### Composition Layer
Combines Quran text, translation, background media, audio, branding, progress indication, and other visual elements into the final vertical video.

### Quality Guard
Validates generated output before approval. Planned checks include content integrity, translation presence, audio/video timing, dimensions, text overflow, readability, required visual elements, and rendering integrity.

### Export Layer
Produces the final user-facing MP4 artifact.

## 4. Initial MVP

The first milestone is deliberately small:

> Given a selected verse, generate one valid 9:16 Quran video containing the Arabic verse, a translation, recitation audio, a background, and the basic visual layout.

The project must prove the complete path before expanding the feature set.

## 5. Proven Phase 1 Result

Phase 1 has been marked complete with live runtime evidence for Surah Al-Ikhlas 112:1.

Proven path:

Quran content
→ Uthmani Arabic text
→ English translation
→ API-verified Mishari Rashid al-`Afasy Murattal recitation
→ Pexels portrait background
→ 1080x1920 composition
→ validated H.264/AAC MP4

Recorded evidence includes:

- Reciter ID 7 was verified through Quran.com API.
- Audio lookup returned HTTP 200 and the audio was downloaded successfully.
- Pexels candidate ID 9011099 was validated as 1080x1920 vertical H.264 media.
- Final composition was validated at 1080x1920 and approximately 30 FPS.
- Final video and audio durations were checked.
- Final output was recorded as `output/quran_house_112_1.mp4`.

The detailed evidence is maintained in `docs/PHASE_1_COMPLETION.md`.

## 6. Current State

Current milestone: **Phase 1 — First Working Video — COMPLETE**.

Next milestone: **Phase 2 — Theme Engine**.

The next implementation step should preserve the proven Phase 1 path while extracting reusable presentation concerns into a bounded, configuration-driven theme layer.

## 7. Planned Product Evolution

1. First working video — complete.
2. Reusable theme system.
3. Multiple reciters and robust audio handling.
4. Intelligent/semantic background selection.
5. AI-assisted theme selection.
6. Automated quality/guard system.
7. Batch generation.
8. Workflow automation.
9. Stable V1 release.

See `docs/PHASES.md` for phase goals and exit criteria.

## 8. Long-Term Visual Direction

The project is intended to support a visual system rather than one permanent template. Possible presentation elements include:

- Uthmani Arabic Quran typography.
- English translation beneath the verse.
- Background video selected for visual relevance and respectfulness.
- Subtle channel branding.
- A simple progress indicator whose presentation can vary by theme.
- Multiple typography, color, animation, and layout configurations.
- 9:16 vertical composition optimized for short-form video.

These are product directions; implementation must not be assumed merely because a feature appears in this document.

## 9. AI and Automation Direction

AI is a later-stage capability, not a prerequisite for the core generator.

Potential future uses include:

- understanding verse context,
- selecting a suitable visual theme,
- generating search keywords for background media,
- assisting quality inspection,
- detecting visual problems that deterministic checks cannot reliably detect.

Workflow automation may later use n8n or another orchestration system. Automation must remain downstream of a stable generation engine.

## 10. Quality Philosophy

A technically valid MP4 is not automatically a successful Quran House output.

The project treats visual output as a first-class success criterion. A video can pass codec, resolution, FPS, and duration checks while still being visually wrong.

Therefore future validation should distinguish between:

- deterministic technical validation,
- content/source integrity validation,
- visual quality validation.

## 11. Scope Discipline

The project follows these principles:

- Build the smallest useful thing first.
- Do not silently expand scope.
- Do not introduce infrastructure before the current milestone requires it.
- Prefer deterministic logic before AI.
- Do not replace working behavior merely for style.
- Add dependencies only with a stated purpose and trade-offs.
- Record meaningful architectural decisions.
- Regression-check meaningful changes.
- Never claim completion without evidence.
- If implementation evidence contradicts documentation, update the documentation.

## 12. Repository Truth

The GitHub repository is the source of truth for implementation and project state.

At the time this overview was created, the repository contains project documentation, memory, and format files but no implementation source tree or notebook. Therefore this document records the verified project direction and Phase 1 evidence documented in the repository; it does not claim that undocumented implementation code exists in this repository.

## 13. Development Model

The intended working model is:

- GPT: planning, technical reasoning, review, and evidence evaluation.
- User: transfers bounded implementation tasks and operates the runtime.
- Spark/other implementation agents: implement bounded tasks and return evidence.

Every meaningful implementation unit should end with an updated project state and a commit.
