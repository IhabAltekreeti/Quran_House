# Quran House — Development Phases

## Phase 0 — Foundation
**Goal:** establish the repository, project memory, working protocol, and development environment.

**Exit condition:** project environment is ready for implementation.

## Phase 1 — First Working Video
**Goal:** generate one valid 9:16 Quran video from a selected verse.

**Core path:** Quran content → Uthmani Hafs Arabic text → translation → recitation → background media → basic composition → valid MP4.

**Acceptance:** the complete pipeline produces a playable vertical video with the required content and basic visual layout.

## Phase 2 — Theme Engine
**Goal:** build reusable, configuration-driven visual themes without rewriting the core video pipeline.

Themes should control layout, typography, animation, colors, progress bar, branding, and other presentation details where practical.

## Phase 3 — Audio & Reciters
**Goal:** support multiple reciters and robust audio handling.

The system should be able to select, retrieve, validate, and synchronize different Quran recitations.

## Phase 4 — Intelligent Backgrounds
**Goal:** select background media that is relevant to the verse while remaining visually appropriate and respectful.

Planned direction: combine Quran context/semantic capabilities with media-provider search such as Pexels.

## Phase 5 — Quality Guard
**Goal:** automatically validate generated videos before approval/export.

Checks may include Quran content integrity, translation presence, audio/video duration, dimensions, text overflow, readability, required visual elements, and rendering integrity.

## Phase 6 — Batch Generation
**Goal:** reliably generate multiple Quran videos from a defined input set while preserving quality and isolation between outputs.

## Phase 7 — Automation
**Goal:** make the generation pipeline suitable for repeatable workflow automation.

Potential integrations include n8n and other workflow/orchestration tools, but automation must remain downstream of a stable generation engine.

## Phase 8 — V1 Release
**Goal:** publish a stable, documented, usable Quran House V1.

V1 is reached only after the preceding phases are completed and their acceptance criteria are demonstrated with evidence.

## Phase Rule

A phase is complete only when its acceptance criteria are demonstrated with evidence. Code existing is not sufficient evidence of completion.

The project should progress sequentially unless an explicit decision records why phases need to overlap.
