# Current State

## Project
Quran House

## Status
Pre-development / project initialization.

## Goal
Build a customizable Quran short-video generation system for creating polished vertical Quran videos and images. The system is intended to combine Quran content, recitation audio, translations, configurable visual themes/templates, suitable background media, branding, and automated quality checks.

## Initial Product Direction
The first working milestone should produce one complete 9:16 Quran video from a selected verse using a simple template. The project should then evolve through small validated milestones rather than starting with a large architecture.

Planned capabilities include:
- Quran verse and translation retrieval.
- Multiple reciters/audio sources.
- Background media selection, initially including Pexels or another suitable source.
- Reusable visual theme/template system.
- Arabic Quran text with translation.
- Progress indicator and channel branding.
- Optional semantic/AI-assisted theme and background selection.
- Automated quality/guard checks.
- Batch generation and workflow automation as later milestones.

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

## Current Milestone
Repository and project operating system initialization. No application implementation has started yet.

## Next Step
Define the first bounded implementation milestone and inspect/recover useful parts of the previous Quran Video Maker project before writing the new generation pipeline.
