# Quran House — Development Phases

This document is the compact phase roadmap for Quran House. A phase is complete only when its acceptance criteria are demonstrated with evidence.

## Phase 0 — Foundation
**Status:** COMPLETE

### Goal
Establish the repository, project memory, working protocol, and development environment.

### Exit Criteria
- Repository and project documentation established.
- Project memory structure established.
- Working/change rules documented.
- Development environment ready for implementation.

---

## Phase 1 — First Working Video
**Status:** COMPLETE

### Goal
Generate one valid 9:16 Quran video from a selected verse.

### Core Path
Quran content → Uthmani Hafs Arabic text → translation → recitation → background media → basic composition → valid MP4.

### Acceptance Criteria
- Complete pipeline runs end-to-end.
- Arabic verse is included.
- Translation is included.
- Recitation audio is present and validated.
- Background media is present and validated.
- Output is a playable vertical video.
- Resolution, FPS, codecs, and duration are validated.
- Quran-specific metadata/identity is verified against authoritative source data.

### Evidence
Surah Al-Ikhlas 112:1 produced a validated 1080x1920 H.264/AAC MP4. Reciter ID 7 was verified through Quran.com API as Mishari Rashid al-`Afasy, Murattal. Pexels candidate ID 9011099 was validated at 1080x1920. Final composition and stream-level properties were validated with FFprobe.

Detailed evidence: `docs/PHASE_1_COMPLETION.md`.

---

## Phase 2 — Theme Engine
**Status:** NEXT

### Goal
Build reusable, configuration-driven visual themes without rewriting the core video-generation pipeline.

### Theme Responsibilities
Themes should control, where practical:

- layout,
- typography,
- colors,
- animation,
- progress bar,
- branding,
- other presentation details.

### Acceptance Criteria
- At least two distinct themes can be rendered.
- Theme selection does not require rewriting the core content/audio/media pipeline.
- Theme configuration is isolated from provider integrations.
- Existing Phase 1 generation remains regression-safe.
- Visual output is inspected, not only technically validated.

### Scope Rule
Do not redesign the entire generator. Extract only the presentation concerns needed for reusable themes.

---

## Phase 3 — Audio & Reciters
**Status:** PLANNED

### Goal
Support multiple reciters and robust audio handling.

### Acceptance Criteria
- Multiple verified reciters can be selected.
- Reciter identity comes from authoritative source metadata.
- Audio retrieval failures are handled explicitly.
- Duration and synchronization are validated.
- Existing video generation remains stable.

---

## Phase 4 — Intelligent Backgrounds
**Status:** PLANNED

### Goal
Select background media that is relevant to the verse while remaining visually appropriate and respectful.

### Planned Direction
Combine Quran context/semantic information with media-provider search such as Pexels.

### Acceptance Criteria
- Background search can use verse-related context.
- Results are validated for format, resolution, orientation, and usability.
- The system has a fallback when suitable media is unavailable.
- Selection remains bounded and predictable.

---

## Phase 5 — Quality Guard
**Status:** PLANNED

### Goal
Automatically validate generated videos before approval/export.

### Potential Checks
- Quran content integrity.
- Translation presence.
- Recitation identity/source integrity.
- Audio/video duration.
- Dimensions and orientation.
- Text overflow.
- Readability.
- Required visual elements.
- Rendering integrity.
- Codec/container validity.

### Important Principle
Technical PASS is not equivalent to visual PASS. Visual inspection/validation must be treated as a first-class quality layer.

---

## Phase 6 — Batch Generation
**Status:** PLANNED

### Goal
Reliably generate multiple Quran videos from a defined input set while preserving quality and isolation between outputs.

### Acceptance Criteria
- Multiple verses can be processed in one run.
- One failed item does not silently corrupt other outputs.
- Outputs have deterministic, traceable identities.
- Quality validation runs per output.

---

## Phase 7 — Automation
**Status:** PLANNED

### Goal
Make the generation pipeline suitable for repeatable workflow automation.

### Potential Integrations
- n8n
- Other workflow/orchestration systems

### Scope Rule
Automation is downstream of a stable generation engine. Do not automate an unstable pipeline.

---

## Phase 8 — V1 Release
**Status:** PLANNED

### Goal
Publish a stable, documented, usable Quran House V1.

### V1 Requirements
- Preceding phases completed or explicitly scoped with documented decisions.
- End-to-end generation reliable.
- Theme system stable.
- Recitation handling robust.
- Background selection usable.
- Quality validation demonstrated.
- Batch generation reliable if included in V1 scope.
- Automation documented if included in V1 scope.
- Repository documentation reflects actual implementation.
- Release evidence is reproducible.

---

## Phase Progression Rule

The project progresses sequentially unless an explicit decision records why phases need to overlap.

**Code existing is not sufficient evidence of completion.**

A phase becomes COMPLETE only when its acceptance criteria are demonstrated with evidence.
