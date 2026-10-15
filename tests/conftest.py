import copy
import json
import os
import shutil
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from quranhouse.fonts import ensure_font  # noqa: E402
ensure_font()
SNAP = json.load(open(os.path.join(ROOT, "tests", "fixtures", "quran_api_snapshot.json"), encoding="utf-8"))
BASE = SNAP["_source"]


class FakeResp:
    def __init__(self, status, payload=None, headers=None, body=b"", url=""):
        self.status_code, self._p, self.headers, self._body, self.url = status, payload, headers or {}, body, url

    def json(self):
        if self._p is None:
            raise ValueError("no json")
        return self._p

    def iter_content(self, n):
        for i in range(0, len(self._body), n):
            yield self._body[i:i + n]

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class FakeSession:
    """Serves recorded Quran.com responses (captured from the live API). Mutations allow
    simulating malformed/missing data. This is a MOCK: it proves parsing/validation logic,
    not that the live API works."""

    def __init__(self, overrides=None):
        self.responses = copy.deepcopy(SNAP["responses"])
        self.overrides = overrides or {}
        self.calls = []

    def get(self, url, params=None, timeout=None, **kw):
        self.calls.append(url)
        path = url.replace(BASE, "")
        if path in self.overrides:
            o = self.overrides[path]
            return o() if callable(o) else o
        if path not in self.responses:
            return FakeResp(404, {"status": 404, "error": "not in fixture"})
        r = self.responses[path]
        return FakeResp(r["status"], r["json"])


@pytest.fixture
def fake():
    return FakeSession()


def api_text(key):
    return SNAP["responses"][f"/verses/by_key/{key}"]["json"]["verse"]["text_uthmani"]


needs_ffmpeg = pytest.mark.skipif(not shutil.which("ffmpeg"), reason="ffmpeg not installed")


def synth_audio(path, seconds, freq):
    """SYNTHETIC tone standing in for recitation in offline tests (not Quranic audio)."""
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"sine=frequency={freq}:duration={seconds}",
                    "-c:a", "libmp3lame", "-b:a", "64k", path], check=True)


def synth_background(path, seconds):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i",
                    f"gradients=s=540x960:d={seconds}:speed=0.05:c0=0x203040:c1=0x405060",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", path], check=True)
