"""Pexels background retrieval. API key from env only; never logged."""
import os

import requests

from .errors import MediaError
from .net import download
from .probe import ffprobe, stream, duration

PEXELS_SEARCH = "https://api.pexels.com/videos/search"
PEXELS_HOSTS = ("pexels.com",)
MAX_VIDEO_BYTES = 150 * 1024 * 1024
DEFAULT_QUERY = "peaceful nature clouds sky"


def get_pexels_key():
    key = os.environ.get("PEXELS_API_KEY")
    if not key:
        try:
            from google.colab import userdata  # type: ignore
            key = userdata.get("PEXELS_API_KEY")
        except Exception:
            key = None
    if not key:
        raise MediaError("PEXELS_API_KEY is not configured")
    return key


def choose_candidate(videos, min_duration):
    """Prefer portrait files with enough duration; shorter clips are allowed and looped."""
    best = None
    for v in videos:
        for f in sorted(v.get("video_files") or [], key=lambda x: x.get("height") or 0, reverse=True):
            w, h, link = f.get("width") or 0, f.get("height") or 0, f.get("link")
            if h > w and link and (f.get("file_type") in (None, "video/mp4")) and h <= 1920:
                score = (v.get("duration", 0) >= min_duration, h)
                if best is None or score > best[0]:
                    best = (score, v, f)
                break
    if not best:
        raise MediaError("no portrait MP4 candidate in Pexels results")
    return best[1], best[2]


def fetch_background(min_duration, work_dir, query=DEFAULT_QUERY, session=None):
    session = session or requests.Session()
    key = get_pexels_key()
    try:
        r = session.get(PEXELS_SEARCH, headers={"Authorization": key},
                        params={"query": query, "orientation": "portrait", "size": "medium", "per_page": 15},
                        timeout=(10, 20))
    except requests.RequestException as e:
        raise MediaError(f"Pexels request failed: {type(e).__name__}") from e
    if r.status_code != 200:
        raise MediaError(f"Pexels search HTTP {r.status_code}")
    v, f = choose_candidate(r.json().get("videos") or [], min_duration)
    os.makedirs(work_dir, exist_ok=True)
    dest = os.path.join(work_dir, f"pexels_{int(v['id'])}.mp4")
    download(f["link"], dest, PEXELS_HOSTS, MAX_VIDEO_BYTES, ("video/",), session)
    return validate_background(dest, {"provider": "pexels", "video_id": v["id"], "page_url": v.get("url"),
                                      "author": (v.get("user") or {}).get("name"),
                                      "author_url": (v.get("user") or {}).get("url")})


def validate_background(path, attribution=None):
    info = ffprobe(path)
    vs = stream(info, "video")
    if not vs:
        raise MediaError("background has no video stream")
    d = duration(info, "video")
    if d <= 0:
        raise MediaError("background has no duration")
    return {"path": path, "width": int(vs["width"]), "height": int(vs["height"]),
            "duration_sec": d, "codec": vs.get("codec_name"), "attribution": attribution or {}}
