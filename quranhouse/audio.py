"""Per-ayah recitation retrieval (Quran.com API), validated and concatenated."""
import os
import subprocess

import requests

from .content import QURAN_API_BASE, TIMEOUT
from .errors import IntegrityError, MediaError
from .net import download
from .probe import ffprobe, stream, duration

AUDIO_HOSTS = ("verses.quran.com", "quranicaudio.com", "everyayah.com")
MAX_AUDIO_BYTES = 20 * 1024 * 1024


def verify_reciter(session, reciter_id):
    """Return API metadata for the recitation. Nothing is assumed or defaulted."""
    r = session.get(f"{QURAN_API_BASE}/resources/recitations", params={"language": "en"}, timeout=TIMEOUT)
    if r.status_code != 200:
        raise IntegrityError(f"recitations list HTTP {r.status_code}")
    for rec in r.json().get("recitations") or []:
        if rec.get("id") == reciter_id and rec.get("reciter_name"):
            style = rec.get("style")
            if not style:  # list endpoint may omit style; ask the meta endpoint, never default
                m = session.get(f"{QURAN_API_BASE}/quran/recitations/{reciter_id}",
                                params={"verse_key": "1:1"}, timeout=TIMEOUT)
                if m.status_code == 200:
                    style = (m.json().get("meta") or {}).get("recitation_style")
            return {"reciter_id": reciter_id, "reciter_name": rec["reciter_name"],
                    "style": style or None}
    raise IntegrityError(f"recitation id {reciter_id} not found in API")


def resolve_audio_url(rel):
    if not isinstance(rel, str) or not rel:
        raise IntegrityError("API returned no audio URL")
    if rel.startswith("//"):
        return "https:" + rel
    if rel.startswith("http"):
        return rel
    return "https://verses.quran.com/" + rel.lstrip("/")


def lookup_ayah_audio(session, reciter_id, verse_key):
    r = session.get(f"{QURAN_API_BASE}/recitations/{reciter_id}/by_ayah/{verse_key}", timeout=TIMEOUT)
    if r.status_code != 200:
        raise IntegrityError(f"audio lookup {verse_key} HTTP {r.status_code}")
    files = r.json().get("audio_files") or []
    match = [f for f in files if f.get("verse_key") == verse_key]
    if len(match) != 1:
        raise IntegrityError(f"audio lookup for {verse_key} returned {len(match)} matching files")
    return resolve_audio_url(match[0].get("url"))


def validate_audio_file(path):
    info = ffprobe(path)
    if not stream(info, "audio"):
        raise MediaError(f"{os.path.basename(path)} has no audio stream")
    d = duration(info, "audio")
    if d <= 0.2:
        raise MediaError(f"{os.path.basename(path)} duration {d:.2f}s is implausible")
    return d


def fetch_recitation(passage, reciter_id, work_dir, session=None):
    session = session or requests.Session()
    meta = verify_reciter(session, reciter_id)
    os.makedirs(work_dir, exist_ok=True)
    segments = []
    for v in passage.verses:
        url = lookup_ayah_audio(session, reciter_id, v.verse_key)
        dest = os.path.join(work_dir, f"r{reciter_id}_{v.surah:03d}{v.ayah:03d}.mp3")
        size = download(url, dest, AUDIO_HOSTS, MAX_AUDIO_BYTES, ("audio/", "application/octet-stream"), session)
        segments.append({"verse_key": v.verse_key, "url": url, "path": dest, "bytes": size,
                         "duration_sec": validate_audio_file(dest)})
    return meta, segments


def concat_audio(segments, out_path, timeout=300):
    """Decode-and-concat into one AAC track; returns (path, [start,end] per ayah) from real durations."""
    lst = out_path + ".txt"
    with open(lst, "w", encoding="utf-8") as f:
        for s in segments:
            f.write("file '%s'\n" % os.path.abspath(s["path"]).replace("'", "'\\''"))
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst,
           "-c:a", "aac", "-b:a", "192k", out_path]
    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=timeout)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        raise MediaError(f"audio concat failed: {type(e).__name__}") from e
    finally:
        os.remove(lst)
    t, timings = 0.0, []
    for s in segments:
        timings.append((s["verse_key"], t, t + s["duration_sec"]))
        t += s["duration_sec"]
    total = validate_audio_file(out_path)
    if abs(total - t) > 0.3:
        raise MediaError(f"concatenated audio {total:.2f}s != sum of ayahs {t:.2f}s")
    return out_path, timings
