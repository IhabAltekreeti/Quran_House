import os

import pytest

from conftest import FakeResp, FakeSession, needs_ffmpeg, synth_audio
from quranhouse import audio, media, net
from quranhouse.errors import IntegrityError, MediaError


def test_reciter_verified_from_api_and_style_from_meta(fake):
    m = audio.verify_reciter(fake, 7)
    assert m["reciter_name"] == "Mishari Rashid al-`Afasy" and m["style"] == "Murattal"


def test_style_never_fabricated_when_meta_unavailable():
    s = FakeSession({"/quran/recitations/7": FakeResp(503, {})})
    assert audio.verify_reciter(s, 7)["style"] is None


def test_unknown_reciter_rejected(fake):
    with pytest.raises(IntegrityError):
        audio.verify_reciter(fake, 99999)


def test_audio_lookup_must_match_verse_key():
    s = FakeSession({"/recitations/7/by_ayah/94:8": FakeResp(200, {"audio_files": [
        {"verse_key": "94:7", "url": "Alafasy/mp3/094007.mp3"}]})})
    with pytest.raises(IntegrityError, match="0 matching"):
        audio.lookup_ayah_audio(s, 7, "94:8")


def test_audio_url_resolution(fake):
    assert audio.lookup_ayah_audio(fake, 7, "94:8") == "https://verses.quran.com/Alafasy/mp3/094008.mp3"
    assert audio.resolve_audio_url("//mirrors.quranicaudio.com/x.mp3") == "https://mirrors.quranicaudio.com/x.mp3"
    with pytest.raises(IntegrityError):
        audio.resolve_audio_url("")


class DL:
    def __init__(self, resp):
        self.resp = resp

    def get(self, *a, **k):
        return self.resp


@pytest.mark.parametrize("url", ["http://verses.quran.com/a.mp3", "https://evil.example/a.mp3",
                                 "https://verses.quran.com.evil.example/a.mp3", "https://169.254.169.254/x"])
def test_download_rejects_unsafe_urls(tmp_path, url):
    with pytest.raises(MediaError):
        net.download(url, str(tmp_path / "a"), audio.AUDIO_HOSTS, 10**6, ("audio/",), DL(None))


def _dl(tmp_path, resp, max_bytes=10**6):
    return net.download("https://verses.quran.com/a.mp3", str(tmp_path / "a.mp3"), audio.AUDIO_HOSTS,
                        max_bytes, ("audio/",), DL(resp))


def test_download_rejects_redirect_to_other_host(tmp_path):
    with pytest.raises(MediaError, match="non-allowlisted"):
        _dl(tmp_path, FakeResp(200, headers={"Content-Type": "audio/mpeg"}, body=b"x", url="https://evil.example/a"))


def test_download_rejects_html_error_page_saved_as_audio(tmp_path):
    with pytest.raises(MediaError, match="content-type"):
        _dl(tmp_path, FakeResp(200, headers={"Content-Type": "text/html"}, body=b"<html>",
                               url="https://verses.quran.com/a.mp3"))
    assert not os.path.exists(tmp_path / "a.mp3")


def test_download_rejects_empty_and_oversize(tmp_path):
    ok_url = "https://verses.quran.com/a.mp3"
    with pytest.raises(MediaError, match="empty"):
        _dl(tmp_path, FakeResp(200, headers={"Content-Type": "audio/mpeg"}, body=b"", url=ok_url))
    with pytest.raises(MediaError, match="exceeded"):
        _dl(tmp_path, FakeResp(200, headers={"Content-Type": "audio/mpeg"}, body=b"x" * 2000, url=ok_url), 1000)
    assert not os.listdir(tmp_path)  # no partial files left behind


@needs_ffmpeg
def test_corrupted_audio_file_rejected(tmp_path):
    bad = tmp_path / "bad.mp3"
    bad.write_bytes(b"<html>404</html>")
    with pytest.raises(MediaError):
        audio.validate_audio_file(str(bad))
    good = tmp_path / "good.mp3"
    synth_audio(str(good), 1.0, 440)
    assert 0.9 < audio.validate_audio_file(str(good)) < 1.2


def test_pexels_key_missing(monkeypatch):
    monkeypatch.delenv("PEXELS_API_KEY", raising=False)
    with pytest.raises(MediaError, match="not configured"):
        media.get_pexels_key()


def test_pexels_candidate_selection_prefers_long_portrait_and_rejects_landscape():
    vids = [{"id": 1, "duration": 2, "video_files": [{"width": 1080, "height": 1920, "link": "https://videos.pexels.com/1"}]},
            {"id": 2, "duration": 30, "video_files": [{"width": 1920, "height": 1080, "link": "https://videos.pexels.com/2"},
                                                      {"width": 720, "height": 1280, "link": "https://videos.pexels.com/3"}]}]
    v, f = media.choose_candidate(vids, 10)
    assert v["id"] == 2 and f["height"] == 1280
    with pytest.raises(MediaError):
        media.choose_candidate([vids[1] | {"video_files": vids[1]["video_files"][:1]}], 10)
