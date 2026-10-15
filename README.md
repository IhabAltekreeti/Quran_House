# Quran House

Vertical (1080x1920) Quran short-video generator: Quran.com text + translation,
Quran.com per-ayah recitation, Pexels background, FFmpeg composition, and
quality control on the rendered file.

- `Quran_House.ipynb` / `quran_house.py`: Phase 1 notebook (historical record, unchanged).
- `quranhouse/`: importable library + CLI with fail-closed integrity checks.

## Setup (verified on Python 3.13, FFmpeg 6+, Pillow 11.3 with libraqm)

```bash
sudo apt-get install -y ffmpeg libraqm0 fonts-dejavu-core   # Debian/Ubuntu/Colab
pip install -r requirements.txt
python -m quranhouse.fonts      # downloads pinned Amiri Quran font (SIL OFL 1.1), SHA-256 verified
python -c "from PIL import features; assert features.check('raqm'), 'Pillow lacks libraqm'"
export PEXELS_API_KEY=...        # or Colab secret PEXELS_API_KEY; never commit it
```

## Generate

```bash
python -m quranhouse --surah 94 --from 7 --to 8 --reciter 7 --translation 20
```

Output: `output/<timestamp>_<pid>_<surah>_<range>/`
- `quran_house_<range>_r<reciter>.mp4`: only if QC passed
- `quran_house_<range>_r<reciter>.UNVERIFIED.mp4`: QC failed (do not publish)
- `manifest.json`: sources, exact texts + SHA-256, audio URLs, timings, Pexels attribution, QC report

Exit codes: `0` verified, `2` aborted (integrity/media/render error), `3` rendered but QC failed.

## Tests

```bash
python -m pytest -q tests
```
Tests use recorded Quran.com responses (`tests/fixtures/quran_api_snapshot.json`,
captured from the live API) and synthetic tones/backgrounds. They prove the
validation logic, not the availability of the live services.

## Integrity rules enforced
- Text only from Quran.com `text_uthmani`; never generated, normalized or reordered.
- Returned `verse_key` and translation `resource_id` must match the request.
- Ranges are single-surah; out-of-range ayahs abort before any download.
- Arabic must be shaped (libraqm) with a font covering every code point (Amiri Quran, SIL OFL 1.1, https://github.com/aliftype/amiri).
- Text that cannot fit at the minimum size aborts rather than clipping.
- Each ayah's audio is matched by `verse_key`; downloads are https and host-allowlisted,
  with size and content-type limits.

## Troubleshooting
- `Pillow was built without libraqm`: install `libraqm0`, then `pip install --force-reinstall --no-binary :all: pillow` if needed.
- `does not fit`: select fewer/shorter ayahs (e.g. 2:282 is too long for one screen).
- `PEXELS_API_KEY is not configured`: set the env var or Colab secret.
