"""Fetch the pinned Amiri Quran font (SIL OFL 1.1) and verify its SHA-256.

Usage: python -m quranhouse.fonts
"""
import hashlib
import os
import sys

import requests

COMMIT = "2e4388d444fb67f7e20cc75a72d1f3addfd18d31"  # google/fonts
URL = f"https://raw.githubusercontent.com/google/fonts/{COMMIT}/ofl/amiriquran/AmiriQuran-Regular.ttf"
SHA256 = "e2a47644762d16bdfb6d33e0d8db8c6ff30beae84150ef5a705316bbd829455c"
DEST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "fonts", "AmiriQuran-Regular.ttf")


def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def ensure_font():
    if os.path.isfile(DEST) and sha256(DEST) == SHA256:
        return DEST
    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    r = requests.get(URL, timeout=(10, 60))
    r.raise_for_status()
    if hashlib.sha256(r.content).hexdigest() != SHA256:
        raise RuntimeError("Amiri Quran font checksum mismatch; refusing to use it")
    with open(DEST, "wb") as f:
        f.write(r.content)
    return DEST


if __name__ == "__main__":
    print(ensure_font())
    sys.exit(0)
