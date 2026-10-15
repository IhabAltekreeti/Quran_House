"""Guards the recorded fixture itself: each Arabic text must match the SHA-256 of the
live Quran.com API response computed on 2026-10-15. Protects against silent edits
(e.g. Unicode normalization reordering shadda/harakat) when files are copied."""
import hashlib
import os

import pytest

from conftest import SNAP

LIVE_SHA256 = {
    "94:1": "191e5006f28279296730ad692567abbf71709a9bbc9fc6c416672fb698b0420e",
    "94:2": "d26a4cc8405aadaec45a088ade0ea58f951386ae176a1f7c689ea874959925b5",
    "94:3": "d8b2577f565ca6889f412d9a4e657eade59b1f1865796ce6e9c39c75a69307c0",
    "94:4": "973ecfffab7bd05c60863e8d3a6fbc80326bfe2ee22554e69bdd4d52e8734f43",
    "94:5": "46d6e18e05512d5f0fcb4c35e4af2aaece5db115e0a1a3681510ceeb6f09724e",
    "94:6": "abb0d076396621c83d5a91f74e71dd0383df4816b428d44abfb0da0a9e998aab",
    "94:7": "314042bf70acfe9777cb39f66afd041025c435f21e5f2a959063a1d0b0350720",
    "94:8": "93e29c35c3f391e93e2c6d2552fd18edfa8fe15845ed9f19e8b9328d84196104",
    "112:1": "1980321245fd0f9fc4bfc88018988bd489f6e75c9a3e2a27c62025c254be8cbb",
    "93:11": "8d2728d96282b15a3a4dff8e4fc4f9a13af4d3fe8258e8022aae354d2ef1cb78",
    "2:282": "4be616c8efe4a5dd79034487b171637907bcf03b3772ac15e07c5d1e33842b89",
}


def test_fixture_is_ascii_escaped():
    path = os.path.join(os.path.dirname(__file__), "fixtures", "quran_api_snapshot.json")
    with open(path, "rb") as f:
        assert f.read().isascii(), "store fixture with ensure_ascii=True to prevent normalization"


@pytest.mark.parametrize("key", sorted(LIVE_SHA256))
def test_fixture_arabic_matches_live_hash(key):
    text = SNAP["responses"][f"/verses/by_key/{key}"]["json"]["verse"]["text_uthmani"]
    assert hashlib.sha256(text.encode("utf-8")).hexdigest() == LIVE_SHA256[key]


@pytest.mark.skipif(not os.environ.get("QH_LIVE"), reason="set QH_LIVE=1 to compare with live API")
def test_fixture_still_matches_live_api():
    from quranhouse import content
    for key in LIVE_SHA256:
        s, a = map(int, key.split(":"))
        v = content.fetch_passage(s, a, a)
        assert v.verses[0].text_uthmani == SNAP["responses"][f"/verses/by_key/{key}"]["json"]["verse"]["text_uthmani"].strip()
