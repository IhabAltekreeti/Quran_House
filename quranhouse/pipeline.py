"""End-to-end generation. Fail-closed: any integrity failure aborts; a video is
only named as final (and manifest marked verified) when QC passes."""
import json
import os
import re
import shutil
import time

from . import audio as audio_mod, content, media, render, qc
from .errors import IntegrityError

SAFE = re.compile(r"^[A-Za-z0-9_.-]+$")


def make_run_dir(base, slug):
    base = os.path.abspath(base)
    run = f"{time.strftime('%Y%m%d-%H%M%S')}_{os.getpid()}_{slug}"
    if not SAFE.match(run):
        raise ValueError("unsafe run name")
    path = os.path.join(base, run)
    os.makedirs(path, exist_ok=False)  # unique per run -> concurrent jobs never collide
    return path


def generate_from_assets(passage, reciter_meta, segments, background, run_dir):
    """Render + QC given already-validated assets (also used by offline tests)."""
    content.assert_passage_integrity(passage.selection, passage.verses)
    if [s["verse_key"] for s in segments] != passage.selection.keys:
        raise IntegrityError("audio segments do not correspond 1:1 to selected verses")
    mixed, timings = audio_mod.concat_audio(segments, os.path.join(run_dir, "recitation.m4a"))
    total = timings[-1][2]
    overlays, masks = [], []
    for v in passage.verses:
        png, mask = render.build_overlay(v, passage.chapter_name_simple, reciter_meta["reciter_name"],
                                         os.path.join(run_dir, f"overlay_{v.surah}_{v.ayah}.png"))
        overlays.append(png)
        masks.append(mask)
    tmp_out = os.path.join(run_dir, "render.tmp.mp4")
    render.compose(background["path"], overlays, timings, mixed, total, tmp_out)
    report = qc.run_qc(tmp_out, total, timings, masks)
    name = f"quran_house_{passage.selection.slug}_r{reciter_meta['reciter_id']}"
    final = os.path.join(run_dir, name + (".mp4" if report["pass"] else ".UNVERIFIED.mp4"))
    os.replace(tmp_out, final)
    manifest = {
        "verified": report["pass"],
        "output": os.path.basename(final),
        "passage": passage.to_manifest(),
        "recitation": {**reciter_meta, "segments": [{k: s[k] for k in ("verse_key", "url", "bytes", "duration_sec")}
                                                    for s in segments]},
        "timings": timings,
        "background": {k: background[k] for k in ("width", "height", "duration_sec", "codec", "attribution")},
        "qc": report,
        "limitations": ["On-screen text is verified by pixel comparison against the shaped render of the "
                        "exact API string, not by OCR.",
                        "Recitation correspondence relies on Quran.com per-ayah audio metadata; the "
                        "audio content itself is not speech-recognized."],
    }
    with open(os.path.join(run_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    return final, manifest


def generate(surah, ayah_from, ayah_to, reciter_id=7, translation_id=20, output_dir="output",
             query=media.DEFAULT_QUERY):
    media.get_pexels_key()  # fail fast on missing credentials before any download
    passage = content.fetch_passage(surah, ayah_from, ayah_to, translation_id)
    run_dir = make_run_dir(output_dir, passage.selection.slug)
    try:
        meta, segments = audio_mod.fetch_recitation(passage, reciter_id, os.path.join(run_dir, "audio"))
        need = sum(s["duration_sec"] for s in segments)
        bg = media.fetch_background(need, os.path.join(run_dir, "bg"), query=query)
        return generate_from_assets(passage, meta, segments, bg, run_dir)
    except BaseException:
        shutil.rmtree(run_dir, ignore_errors=True)  # only this run's own unique directory
        raise
