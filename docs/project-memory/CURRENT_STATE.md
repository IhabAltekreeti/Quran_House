# Current State

## Project
Quran House

## Status
Phase 1 complete — first working video demonstrated with live runtime evidence.

## Goal
Build a customizable Quran short-video generation system for creating polished vertical Quran videos and images. The system combines Quran content, verified recitation audio, translations, configurable visual themes/templates, suitable background media, branding, and automated quality checks.

## Development Principles
1. Build a small end-to-end working pipeline first.
2. Prefer visible, testable milestones over speculative infrastructure.
3. Keep architecture proportional to the current milestone.
4. Reuse lessons from previous projects, especially explicit tests, evidence, project memory, and bounded implementation steps.
5. Record meaningful decisions and progress in project memory.
6. Every meaningful implementation session should end with an updated project state and a commit.
7. Do not expand scope merely because a feature is technically interesting.
8. Preserve the ability to add new themes without rewriting the video-generation core.
9. Separate proven behavior from planned behavior.
10. The GitHub repository is the source of truth for code; memory documents project state and decisions.
11. Quran-specific identity and source claims must be verified from authoritative API/source data rather than inferred from IDs or filenames.

## Phase 1 — Completed
The first end-to-end path has been demonstrated for Surah Al-Ikhlas 112:1:

Quran content → Uthmani Arabic text → English translation → API-verified Mishari Rashid al-`Afasy Murattal recitation → Pexels portrait background → 1080x1920 composition → valid MP4.

Live runtime evidence:
- Cell 4: reciter identity verified through Quran.com API; ID 7 resolved to Mishari Rashid al-`Afasy; Murattal; audio downloaded and validated.
- Cell 5: Pexels portrait video retrieved and validated at 1080x1920 with FFprobe.
- Cell 6: final MP4 rendered and validated at 1080x1920, ~30 fps, H.264/AAC, with source/final duration delta within acceptance tolerance.
- Final demonstrated output: `output/quran_house_112_1.mp4`.

## Important Phase 1 Evidence
Cell 4 final observed output:
- Reciter Identity: PASS (API verified: Mishari Rashid al-`Afasy, Murattal)
- API Audio Lookup: PASS (200 OK)
- Audio Download: PASS (47.1 KB)
- API active duration: 2.30 s
- FFprobe duration: 2.98 s
- Duration consistency: PASS

Cell 5 observed output:
- Pexels API: PASS
- Candidate: ID 9011099, 1080x1920
- Download: PASS (9.21 MB)
- FFprobe: PASS (H.264, 1080x1920, 15.2 s, vertical)

Cell 6 final observed output:
- Payload Integrity: PASS
- Typography Overlay: PASS
- Video Resolution: PASS (1080x1920)
- Video FPS: PASS (~30 fps)
- Source Audio: 2.98 s
- Final Video: 2.97 s
- Final Audio: 2.92 s
- Duration Delta: PASS (0.01 s)
- Audio Codec: AAC
- Video Codec: H264
- Output: `quran_house_112_1.mp4`, 1.25 MB
- FFprobe Verification: PASS

## Current Milestone
Phase 1 — First Working Video — COMPLETE.

## Next Milestone
Phase 2 — Theme Engine.

Goal: build a reusable, configuration-driven visual theme system so presentation can change without rewriting the core video-generation pipeline. Planned theme controls include layout, typography, colors, animation, progress bar, branding, and other presentation details where practical.

## Scope Discipline
Phase 2 should begin only after the Phase 1 evidence is recorded. Do not redesign the entire pipeline yet. Preserve the proven Phase 1 core path while extracting reusable presentation concerns into a bounded theme layer.
