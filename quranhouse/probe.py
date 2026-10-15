import json
import subprocess

from .errors import MediaError

FFPROBE_TIMEOUT = 60


def ffprobe(path: str) -> dict:
    cmd = ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", path]
    try:
        out = subprocess.run(cmd, capture_output=True, timeout=FFPROBE_TIMEOUT, check=True).stdout
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        raise MediaError(f"ffprobe failed for {path}: {type(e).__name__}") from e
    return json.loads(out)


def stream(info: dict, kind: str):
    return next((s for s in info.get("streams", []) if s.get("codec_type") == kind), None)


def duration(info: dict, kind: str = None) -> float:
    s = stream(info, kind) if kind else None
    d = (s or {}).get("duration") or info.get("format", {}).get("duration")
    return float(d or 0.0)
