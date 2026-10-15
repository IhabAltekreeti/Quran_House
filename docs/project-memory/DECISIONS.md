# Decisions


## 2026-10-15: Library + CLI alongside the Phase 1 notebook
The notebook is left unchanged as the Phase 1 record. A `quranhouse/` package
reimplements the same pipeline with fail-closed checks so it can be unit-tested.
Arabic rendering requires libraqm and the Amiri Quran font (SIL OFL 1.1), downloaded at setup by `python -m quranhouse.fonts` from a pinned google/fonts commit with a SHA-256 check (not committed as a binary).
Videos spanning two surahs are not supported.
