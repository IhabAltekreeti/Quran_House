"""Quran text + translation retrieval with fail-closed validation.

Source of truth: Quran.com API v4 (text_uthmani + translation resource).
Text is never generated, normalized, or reordered here.
"""
import hashlib
import re
from dataclasses import dataclass, field, asdict

import requests

from .errors import IntegrityError

QURAN_API_BASE = "https://api.quran.com/api/v4"
TIMEOUT = (10, 20)
TOTAL_SURAHS = 114


@dataclass(frozen=True)
class Selection:
    surah: int
    ayah_from: int
    ayah_to: int

    @property
    def keys(self):
        return [f"{self.surah}:{a}" for a in range(self.ayah_from, self.ayah_to + 1)]

    @property
    def slug(self):
        return f"{self.surah}_{self.ayah_from}" + ("" if self.ayah_from == self.ayah_to else f"-{self.ayah_to}")


@dataclass
class Verse:
    verse_key: str
    surah: int
    ayah: int
    text_uthmani: str
    translation_raw: str
    translation_clean: str
    translation_resource_id: int
    text_sha256: str = ""

    def __post_init__(self):
        self.text_sha256 = hashlib.sha256(self.text_uthmani.encode("utf-8")).hexdigest()


@dataclass
class Passage:
    selection: Selection
    chapter_name_simple: str
    chapter_name_arabic: str
    verses_count: int
    translation_resource_id: int
    translation_name: str
    verses: list = field(default_factory=list)

    def to_manifest(self):
        d = asdict(self)
        d["source"] = QURAN_API_BASE
        return d


def _is_int(x):
    return isinstance(x, int) and not isinstance(x, bool)


def validate_selection(surah, ayah_from, ayah_to, verses_count=None) -> Selection:
    """Validate identifiers. Cross-surah ranges are rejected (one surah per video)."""
    if not all(_is_int(v) for v in (surah, ayah_from, ayah_to)):
        raise IntegrityError("surah/ayah identifiers must be integers")
    if not 1 <= surah <= TOTAL_SURAHS:
        raise IntegrityError(f"invalid surah {surah} (must be 1..{TOTAL_SURAHS})")
    if ayah_from < 1 or ayah_to < ayah_from:
        raise IntegrityError(f"invalid ayah range {ayah_from}-{ayah_to}")
    if verses_count is not None and ayah_to > verses_count:
        raise IntegrityError(
            f"ayah {ayah_to} exceeds surah {surah} length ({verses_count}); "
            "ranges spanning surahs are not supported")
    return Selection(surah, ayah_from, ayah_to)


def clean_translation_text(text: str) -> str:
    """Remove footnote markers and HTML only. Bracket/interpolation marks
    (e.g. [..] or ˹..˺) are part of the translator's text and are preserved."""
    text = re.sub(r"<sup[^>]*>.*?</sup>", "", text, flags=re.S)
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\s+", " ", text).strip()


def _get(session, path, params=None):
    try:
        r = session.get(f"{QURAN_API_BASE}{path}", params=params, timeout=TIMEOUT)
    except requests.RequestException as e:
        raise IntegrityError(f"Quran API request failed: {type(e).__name__}") from e
    if r.status_code != 200:
        raise IntegrityError(f"Quran API {path} returned HTTP {r.status_code}")
    try:
        return r.json()
    except ValueError as e:
        raise IntegrityError(f"Quran API {path} returned non-JSON") from e


def fetch_chapter(session, surah):
    ch = _get(session, f"/chapters/{surah}").get("chapter") or {}
    if ch.get("id") != surah or not _is_int(ch.get("verses_count")):
        raise IntegrityError(f"chapter metadata mismatch for surah {surah}")
    return ch


def fetch_translation_name(session, resource_id):
    items = _get(session, "/resources/translations").get("translations") or []
    for t in items:
        if t.get("id") == resource_id:
            return t.get("name") or ""
    raise IntegrityError(f"translation resource {resource_id} not listed by API")


def parse_verse(payload: dict, expected_key: str, translation_id: int) -> Verse:
    v = (payload or {}).get("verse") or {}
    if v.get("verse_key") != expected_key:
        raise IntegrityError(f"API returned verse {v.get('verse_key')!r}, expected {expected_key}")
    text = v.get("text_uthmani")
    if not isinstance(text, str) or not text.strip():
        raise IntegrityError(f"empty Arabic text for {expected_key}")
    trs = [t for t in v.get("translations") or [] if t.get("resource_id") == translation_id]
    if len(trs) != 1 or not (trs[0].get("text") or "").strip():
        raise IntegrityError(f"translation {translation_id} missing/ambiguous for {expected_key}")
    raw = trs[0]["text"]
    s, a = (int(x) for x in expected_key.split(":"))
    # Only surrounding whitespace is stripped; inner text is byte-preserved.
    return Verse(expected_key, s, a, text.strip(), raw, clean_translation_text(raw), translation_id)


def fetch_passage(surah, ayah_from, ayah_to, translation_id=20, session=None) -> Passage:
    session = session or requests.Session()
    validate_selection(surah, ayah_from, ayah_to)
    ch = fetch_chapter(session, surah)
    sel = validate_selection(surah, ayah_from, ayah_to, ch["verses_count"])
    tname = fetch_translation_name(session, translation_id)
    verses = []
    for key in sel.keys:
        payload = _get(session, f"/verses/by_key/{key}",
                       {"translations": str(translation_id), "fields": "text_uthmani", "words": "false"})
        verses.append(parse_verse(payload, key, translation_id))
    assert_passage_integrity(sel, verses)
    return Passage(sel, ch.get("name_simple", ""), ch.get("name_arabic", ""), ch["verses_count"],
                   translation_id, tname, verses)


def assert_passage_integrity(sel: Selection, verses):
    got = [v.verse_key for v in verses]
    if got != sel.keys:
        raise IntegrityError(f"verse sequence mismatch: expected {sel.keys}, got {got}")
    if len(set(got)) != len(got):
        raise IntegrityError("duplicate verses in passage")
