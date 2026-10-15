import pytest
import requests

from conftest import FakeResp, FakeSession, api_text
from quranhouse import content
from quranhouse.errors import IntegrityError


@pytest.mark.parametrize("args", [(0, 1, 1), (115, 1, 1), (94, 0, 1), (94, 3, 2), (94, "1", 2), (True, 1, 1)])
def test_invalid_identifiers(args):
    with pytest.raises(IntegrityError):
        content.validate_selection(*args)


def test_single_ayah_112_1_exact_text(fake):
    p = content.fetch_passage(112, 1, 1, session=fake)
    assert [v.verse_key for v in p.verses] == ["112:1"]
    assert p.verses[0].text_uthmani == api_text("112:1").strip()  # only outer whitespace stripped
    assert "\u0671" in p.verses[0].text_uthmani  # alef wasla preserved (no normalization)
    assert p.translation_name == "Saheeh International"


def test_surah_94_full_and_final_verses(fake):
    p = content.fetch_passage(94, 1, 8, session=fake)
    assert [v.verse_key for v in p.verses] == [f"94:{i}" for i in range(1, 9)]
    for v in p.verses:
        assert v.text_uthmani == api_text(v.verse_key).strip()
    p2 = content.fetch_passage(94, 7, 8, session=fake)
    assert [v.ayah for v in p2.verses] == [7, 8]
    assert p2.verses[1].text_uthmani == api_text("94:8")


def test_last_ayah_of_surah_93(fake):
    assert content.fetch_passage(93, 11, 11, session=fake).verses[0].verse_key == "93:11"


@pytest.mark.parametrize("sel", [(94, 8, 9), (94, 9, 9), (93, 11, 12)])
def test_past_end_and_cross_surah_rejected_before_fetching_verses(sel):
    s = FakeSession()
    with pytest.raises(IntegrityError, match="exceeds"):
        content.fetch_passage(*sel, session=s)
    assert not any("/verses/" in c for c in s.calls)


def _verse_override(key, mutate):
    s = FakeSession()
    r = s.responses[f"/verses/by_key/{key}"]
    mutate(r["json"]["verse"])
    return s


def test_api_returns_wrong_verse_key():
    s = _verse_override("94:8", lambda v: v.update(verse_key="94:7"))
    with pytest.raises(IntegrityError, match="expected 94:8"):
        content.fetch_passage(94, 7, 8, session=s)


def test_empty_arabic_text():
    s = _verse_override("94:8", lambda v: v.update(text_uthmani="  "))
    with pytest.raises(IntegrityError, match="empty Arabic"):
        content.fetch_passage(94, 8, 8, session=s)


def test_translation_from_wrong_resource_rejected():
    s = _verse_override("94:8", lambda v: v["translations"][0].update(resource_id=131))
    with pytest.raises(IntegrityError, match="translation 20"):
        content.fetch_passage(94, 8, 8, session=s)


def test_missing_translation_rejected():
    s = _verse_override("94:8", lambda v: v.update(translations=[]))
    with pytest.raises(IntegrityError):
        content.fetch_passage(94, 8, 8, session=s)


def test_unknown_translation_id_rejected(fake):
    with pytest.raises(IntegrityError, match="not listed"):
        content.fetch_passage(94, 8, 8, translation_id=999999, session=fake)


def test_duplicate_or_reordered_sequence_rejected(fake):
    sel = content.Selection(94, 7, 8)
    v7 = content.fetch_passage(94, 7, 7, session=fake).verses[0]
    v8 = content.fetch_passage(94, 8, 8, session=fake).verses[0]
    for seq in ([v7, v7], [v8, v7], [v7]):
        with pytest.raises(IntegrityError):
            content.assert_passage_integrity(sel, seq)


def test_http_error_empty_and_network_failures():
    for ov in (FakeResp(500, {}), FakeResp(200, None), FakeResp(200, {})):
        with pytest.raises(IntegrityError):
            content.fetch_passage(94, 8, 8, session=FakeSession({"/verses/by_key/94:8": ov}))

    def boom():
        raise requests.ConnectionError("down")
    with pytest.raises(IntegrityError, match="ConnectionError"):
        content.fetch_passage(94, 8, 8, session=FakeSession({"/chapters/94": boom}))


def test_translation_cleaning_preserves_translator_brackets():
    raw = 'Say, "He is Allāh, [who is] One,<sup foot_note=1>1</sup> ˹alone˺ <i>x</i>'
    assert content.clean_translation_text(raw) == 'Say, "He is Allāh, [who is] One, ˹alone˺ x'
