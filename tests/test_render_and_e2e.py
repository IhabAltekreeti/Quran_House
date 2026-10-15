import json
import os

import pytest

from conftest import FakeSession, needs_ffmpeg, synth_audio, synth_background
from quranhouse import content, pipeline, qc, render
from quranhouse.errors import IntegrityError, RenderError

DEJAVU = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def _passage(s, a, b):
    return content.fetch_passage(s, a, b, session=FakeSession())


@pytest.mark.skipif(not os.path.exists(DEJAVU), reason="DejaVu not installed")
def test_regression_P0_original_font_cannot_render_alef_wasla():
    """The Phase 1 renderer used DejaVuSans for Arabic; it lacks U+0671 present in 112:1."""
    with pytest.raises(RenderError, match="U\\+0671"):
        render.assert_glyph_coverage(_passage(112, 1, 1).verses[0].text_uthmani, DEJAVU)


@pytest.mark.parametrize("key", ["112:1", "94:7", "94:8", "2:282"])
def test_quran_font_covers_all_codepoints(key):
    s, a = map(int, key.split(":"))
    render.assert_glyph_coverage(_passage(s, a, a).verses[0].text_uthmani, render.ARABIC_FONT)


def test_shaping_required(monkeypatch):
    monkeypatch.setattr(render.features, "check", lambda name: False)
    with pytest.raises(RenderError, match="libraqm"):
        render.require_shaping()


def test_wrap_preserves_every_word_in_order():
    t = _passage(94, 1, 1).verses[0].text_uthmani
    f = render._font(render.ARABIC_FONT, 96)
    lines = render.wrap_words(t, f, 300, "rtl")
    assert len(lines) > 1 and " ".join(lines) == " ".join(t.split())


def test_overlong_verse_fails_closed_instead_of_clipping(tmp_path):
    v = _passage(2, 282, 282).verses[0]
    with pytest.raises(RenderError, match="does not fit"):
        render.build_overlay(v, "Al-Baqarah", "x", str(tmp_path / "o.png"))


def _assets(tmp_path, passage, durations, bg_seconds):
    segs = []
    for i, (v, d) in enumerate(zip(passage.verses, durations)):
        p = str(tmp_path / f"a{i}.mp3")
        synth_audio(p, d, 300 + 100 * i)
        segs.append({"verse_key": v.verse_key, "url": "synthetic://offline-test", "path": p, "bytes": os.path.getsize(p),
                     "duration_sec": render_dur(p)})
    bg = str(tmp_path / "bg.mp4")
    synth_background(bg, bg_seconds)
    from quranhouse.media import validate_background
    return segs, validate_background(bg, {"provider": "synthetic"})


def render_dur(p):
    from quranhouse.audio import validate_audio_file
    return validate_audio_file(p)


META = {"reciter_id": 7, "reciter_name": "SYNTHETIC TEST TONE", "style": None}


@needs_ffmpeg
def test_e2e_offline_94_7_8_verified_with_looped_short_background(tmp_path):
    p = _passage(94, 7, 8)
    segs, bg = _assets(tmp_path, p, [2.5, 2.0], bg_seconds=1.5)  # bg shorter than audio -> must loop
    run = pipeline.make_run_dir(str(tmp_path / "out"), p.selection.slug)
    final, man = pipeline.generate_from_assets(p, META, segs, bg, run)
    assert man["verified"] is True, json.dumps(man["qc"], ensure_ascii=False)[:2000]
    assert final.endswith("quran_house_94_7-8_r7.mp4") and os.path.getsize(final) > 0
    m = json.load(open(os.path.join(run, "manifest.json"), encoding="utf-8"))
    assert [v["text_uthmani"] for v in m["passage"]["verses"]] == [v.text_uthmani for v in p.verses]
    keys = [c["verse_key"] for c in m["qc"]["checks"]["correct_ayah_on_screen"]["detail"]]
    assert keys == ["94:7"] * 3 + ["94:8"] * 3


@needs_ffmpeg
def test_qc_detects_wrong_ayah_on_screen(tmp_path):
    p = _passage(94, 7, 8)
    segs, bg = _assets(tmp_path, p, [2.0, 2.0], bg_seconds=5)
    from quranhouse.audio import concat_audio
    mixed, timings = concat_audio(segs, str(tmp_path / "mix.m4a"))
    ovs, masks = zip(*[render.build_overlay(v, "Ash-Sharh", "x", str(tmp_path / f"o{i}.png"))
                       for i, v in enumerate(p.verses)])
    out = str(tmp_path / "swapped.mp4")
    render.compose(bg["path"], list(reversed(ovs)), timings, mixed, timings[-1][2], out)  # deliberately wrong
    rep = qc.run_qc(out, timings[-1][2], timings, list(masks))
    assert rep["pass"] is False and rep["checks"]["correct_ayah_on_screen"]["pass"] is False


@needs_ffmpeg
def test_audio_verse_mismatch_aborts(tmp_path):
    p = _passage(94, 7, 8)
    segs, bg = _assets(tmp_path, p, [1.0, 1.0], 3)
    with pytest.raises(IntegrityError, match="1:1"):
        pipeline.generate_from_assets(p, META, list(reversed(segs)), bg, str(tmp_path))


@needs_ffmpeg
def test_qc_detects_truncated_audio(tmp_path):
    p = _passage(112, 1, 1)
    segs, bg = _assets(tmp_path, p, [3.0], 4)
    from quranhouse.audio import concat_audio
    mixed, timings = concat_audio(segs, str(tmp_path / "mix.m4a"))
    png, mask = render.build_overlay(p.verses[0], "Al-Ikhlas", "x", str(tmp_path / "o.png"))
    out = str(tmp_path / "short.mp4")
    render.compose(bg["path"], [png], [("112:1", 0, 1.5)], mixed, 1.5, out)  # cut early
    rep = qc.run_qc(out, timings[-1][2], [("112:1", 0, 1.5)], [mask])
    assert rep["checks"]["audio_not_truncated"]["pass"] is False


def test_run_dirs_are_unique(tmp_path):
    a = pipeline.make_run_dir(str(tmp_path), "94_7-8")
    with pytest.raises(FileExistsError):
        os.makedirs(a, exist_ok=False)


def test_missing_pexels_key_aborts_before_any_download(tmp_path, monkeypatch):
    monkeypatch.delenv("PEXELS_API_KEY", raising=False)
    called = []
    monkeypatch.setattr(content, "fetch_passage", lambda *a, **k: called.append(1))
    from quranhouse.errors import MediaError
    with pytest.raises(MediaError):
        pipeline.generate(94, 7, 8, output_dir=str(tmp_path))
    assert not called and not os.listdir(tmp_path)
