"""Typography overlays and FFmpeg composition.

Arabic is rendered with Pillow's RAQM layout (HarfBuzz shaping + FriBiDi RTL)
using a Quran-capable font. If shaping is unavailable or a glyph is missing,
rendering FAILS rather than producing broken Quranic text.
"""
import os
import subprocess

from PIL import Image, ImageDraw, ImageFont, features

from .errors import RenderError

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
ARABIC_FONT = os.path.join(HERE, "..", "assets", "fonts", "AmiriQuran-Regular.ttf")
LATIN_FONTS = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
               "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"]
MARGIN_X = 80                      # safe horizontal margin
AR_BOX = (MARGIN_X, 470, W - MARGIN_X, 1180)
TR_BOX = (MARGIN_X, 1220, W - MARGIN_X, 1600)


def require_shaping():
    if not features.check("raqm"):
        raise RenderError("Pillow was built without libraqm: Arabic cannot be shaped/RTL-ordered. "
                          "Install libraqm (apt-get install libraqm0) and reinstall Pillow.")


def _font_path(path):
    if not os.path.isfile(path):
        raise RenderError(f"font not found: {path} (run: python -m quranhouse.fonts)")
    return path


def latin_font_path():
    for p in LATIN_FONTS:
        if os.path.isfile(p):
            return p
    raise RenderError("no Latin font found (install fonts-dejavu-core)")


def assert_glyph_coverage(text, font_path):
    """Every non-space code point must exist in the font (no tofu / .notdef)."""
    from fontTools.ttLib import TTFont
    cmap = TTFont(font_path, lazy=True).getBestCmap()
    missing = sorted({c for c in text if not c.isspace() and ord(c) not in cmap})
    if missing:
        raise RenderError("font %s lacks glyphs: %s" % (os.path.basename(font_path),
                                                        ", ".join("U+%04X" % ord(c) for c in missing)))


def _font(path, size):
    return ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.RAQM)


def wrap_words(text, font, max_w, direction):
    """Greedy word wrap. Words are never split or altered; joining lines with
    single spaces reproduces the whitespace-normalized source exactly."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        cand = w if not cur else cur + " " + w
        if font.getlength(cand, direction=direction) <= max_w or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_text(text, font_path, box, start, minimum, direction, line_gap):
    x0, y0, x1, y1 = box
    for size in range(start, minimum - 1, -2):
        f = _font(font_path, size)
        lines = wrap_words(text, f, x1 - x0, direction)
        if any(f.getlength(l, direction=direction) > x1 - x0 for l in lines):
            continue
        lh = int(size * line_gap)
        if lh * len(lines) <= y1 - y0:
            return f, lines, lh
    raise RenderError(f"text does not fit at minimum size {minimum}px; split the passage into shorter clips")


def draw_block(draw, f, lines, lh, box, direction, fill, lang=None):
    x0, y0, x1, y1 = box
    top = y0 + ((y1 - y0) - lh * len(lines)) // 2
    for i, line in enumerate(lines):
        draw.text(((x0 + x1) // 2, top + lh * i + lh // 2), line, font=f, fill=fill, anchor="mm",
                  direction=direction, language=lang)


def build_overlay(verse, chapter_name, reciter_name, out_png):
    """Return (png_path, arabic_text_mask) for QC frame verification."""
    require_shaping()
    ar_path, la_path = _font_path(ARABIC_FONT), latin_font_path()
    assert_glyph_coverage(verse.text_uthmani, ar_path)
    assert_glyph_coverage(verse.translation_clean, la_path)
    ar_f, ar_lines, ar_lh = fit_text(verse.text_uthmani, ar_path, AR_BOX, 96, 44, "rtl", 1.9)
    if " ".join(ar_lines) != " ".join(verse.text_uthmani.split()):
        raise RenderError("internal: wrapped Arabic differs from source")
    tr_f, tr_lines, tr_lh = fit_text(verse.translation_clean, la_path, TR_BOX, 46, 28, "ltr", 1.35)

    img = Image.new("RGBA", (W, H), (0, 0, 0, int(255 * 0.42)))
    d = ImageDraw.Draw(img)
    hdr = _font(la_path, 36)
    d.text((W // 2, 300), f"{chapter_name} — {verse.verse_key}", font=hdr, fill=(235, 235, 235, 240), anchor="mm")
    mask = Image.new("L", (W, H), 0)
    draw_block(ImageDraw.Draw(mask), ar_f, ar_lines, ar_lh, AR_BOX, "rtl", 255, "ar")
    draw_block(d, ar_f, ar_lines, ar_lh, AR_BOX, "rtl", (255, 255, 255, 255), "ar")
    draw_block(d, tr_f, tr_lines, tr_lh, TR_BOX, "ltr", (225, 225, 225, 240))
    d.text((W // 2, 1680), reciter_name, font=_font(la_path, 28), fill=(200, 200, 200, 200), anchor="mm")
    d.text((W // 2, 1740), "Q U R A N   H O U S E", font=_font(la_path, 26), fill=(180, 180, 180, 180), anchor="mm")
    img.save(out_png)
    return out_png, mask


def compose(bg_path, overlays, timings, audio_path, total_dur, out_path, timeout=900):
    """overlays[i] shown during timings[i]; background looped if shorter than audio."""
    cmd = ["ffmpeg", "-y", "-v", "error", "-stream_loop", "-1", "-i", bg_path]
    for o in overlays:
        cmd += ["-i", o]
    cmd += ["-i", audio_path]
    parts = [f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},setsar=1[b0]"]
    last = "b0"
    for i, (_, start, end) in enumerate(timings):
        end_expr = f"{end:.3f}" if i < len(timings) - 1 else f"{total_dur + 1:.3f}"
        parts.append(f"[{last}][{i + 1}:v]overlay=0:0:enable='between(t,{start:.3f},{end_expr})'[b{i + 1}]")
        last = f"b{i + 1}"
    cmd += ["-filter_complex", ";".join(parts), "-map", f"[{last}]", "-map", f"{len(overlays) + 1}:a",
            "-t", f"{total_dur:.3f}", "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out_path]
    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=timeout)
    except subprocess.CalledProcessError as e:
        raise RenderError("ffmpeg failed: " + e.stderr.decode(errors="replace")[-800:]) from e
    except subprocess.TimeoutExpired as e:
        raise RenderError(f"ffmpeg exceeded {timeout}s") from e
    return out_path
