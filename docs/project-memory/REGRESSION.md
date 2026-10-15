# Regression


## 2026-10-15
- `python -m pytest -q tests`: 61 passed, 1 skipped (offline fixtures + synthetic media); `QH_LIVE=1`: 62 passed.
- Live run 94:7-8, reciter 7, translation 20, synthetic background: verified=true, 1080x1920, 30 fps, 8.42 s, per-ayah on-screen check passed at start/mid/end of each ayah.
- Incident: the first upload of `tests/fixtures/quran_api_snapshot.json` was altered in transit (shadda/haraka reordered in 7 verses, 4 code points lost in 2:282). Detected by byte-diff before merge; fixture is now ASCII-escaped and guarded by `tests/test_fixture_integrity.py` (live SHA-256 hashes).
