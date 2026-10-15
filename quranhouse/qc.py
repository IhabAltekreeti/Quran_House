"""Quality control on the actual rendered artifact (not just file existence)."""
import os
import re
import subprocess
import tempfile

from PIL import Image, ImageStat

from .probe import ffprobe, stream, duration
from .render import W, H, FPS


def extract_frame(path, t, timeout=60):
    fd, png = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    try:
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{max(t, 0):.3f}", "-i", path,
                        "-frames:v", "1", png], check=True, capture_output=True, timeout=timeout)
        return Image.open(png).convert("L").copy()
    finally:
        os.remove(png)


def black_intervals(path, timeout=300):
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", path, "-vf", "blackdetect=d=0.5:pix_th=0.08",
                        "-an", "-f", "null", "-"], capture_output=True, timeout=timeout)
    return re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", r.stderr.decode(errors="replace"))


def _mean_in(img, mask):
    st = ImageStat.Stat(img, mask)
    return st.mean[0] if st.count[0] else 0.0


def text_presence(frame, masks, idx):
    """Arabic text pixels are opaque white: the expected ayah's glyph mask must be bright,
    and brighter than every other ayah's mask (pixels unique to the other ayah)."""
    from PIL import ImageChops
    own = _mean_in(frame, masks[idx])
    others = []
    for j, m in enumerate(masks):
        if j != idx:
            uniq = ImageChops.subtract(m, masks[idx])
            if uniq.getbbox():
                others.append(_mean_in(frame, uniq))
    return own, (max(others) if others else None)


def run_qc(path, expected_audio_dur, timings, masks):
    checks = {}

    def rec(name, ok, detail):
        checks[name] = {"pass": bool(ok), "detail": detail}

    rec("file_nonempty", os.path.isfile(path) and os.path.getsize(path) > 0,
        os.path.getsize(path) if os.path.isfile(path) else 0)
    info = ffprobe(path)
    vs, as_ = stream(info, "video"), stream(info, "audio")
    rec("video_stream", vs is not None and vs.get("codec_name") == "h264", (vs or {}).get("codec_name"))
    rec("audio_stream", as_ is not None and as_.get("codec_name") == "aac", (as_ or {}).get("codec_name"))
    rec("resolution", vs and (vs["width"], vs["height"]) == (W, H), vs and f"{vs['width']}x{vs['height']}")
    n, d = (vs or {}).get("avg_frame_rate", "0/1").split("/")
    fps = float(n) / float(d) if float(d) else 0
    rec("fps", abs(fps - FPS) < 0.5, round(fps, 3))
    vd, ad = duration(info, "video"), duration(info, "audio")
    rec("audio_not_truncated", ad >= expected_audio_dur - 0.15, f"audio {ad:.2f}s vs source {expected_audio_dur:.2f}s")
    rec("av_sync_duration", abs(vd - ad) <= 0.15, f"video {vd:.2f}s audio {ad:.2f}s")
    blk = black_intervals(path)
    rec("no_black_segments", not blk, blk)
    ayah_checks = []
    for i, (key, s, e) in enumerate(timings):
        for label, t in (("start", s + 0.15), ("mid", (s + e) / 2), ("end", e - 0.15)):
            t = min(max(t, s), max(e - 0.05, s))
            own, other = text_presence(extract_frame(path, t), masks, i)
            ok = own >= 200 and (other is None or own - other >= 25)
            ayah_checks.append({"verse_key": key, "at": label, "t": round(t, 2),
                                "own_mask_luma": round(own, 1),
                                "max_other_mask_luma": None if other is None else round(other, 1), "pass": ok})
    rec("correct_ayah_on_screen", all(a["pass"] for a in ayah_checks), ayah_checks)
    return {"pass": all(c["pass"] for c in checks.values()), "checks": checks}
