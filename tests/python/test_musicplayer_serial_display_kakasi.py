"""Tests of the Japanese kanji readings from kakasi, with a fake kakasi."""

import shutil
from subprocess import CompletedProcess, TimeoutExpired

import pytest
from serial_display_fakes import DEFINE, display_module, make_display

pytestmark = pytest.mark.usefixtures("isolated_display")

KanjiReader = display_module.KanjiReader
COMMAND = display_module.KAKASI_COMMAND


class FakeKakasi:
    """Fake `subprocess.run` of kakasi, answering lines from a mapping."""

    def __init__(self, readings, error=None):
        self.readings = readings
        self.error = error
        self.calls = []

    def __call__(self, args, **kwargs):
        self.calls.append((args, kwargs))
        if self.error:
            raise self.error
        lines = kwargs["input"].split("\n")
        output = "\n".join(self.readings.get(line, line) for line in lines)
        return CompletedProcess(args, 0, stdout=output, stderr="")


@pytest.fixture
def kakasi(monkeypatch):
    def install(readings=None, error=None):
        fake = FakeKakasi(readings or {}, error)
        monkeypatch.setattr(display_module, "run", fake)
        return fake

    return install


def test_kanji_runs_are_read_in_one_call_with_their_kana(kakasi):
    fake = kakasi({"東京タワー": "トウキョウタワー", "夜に駆ける": "ヨルにカケる"})
    reader = KanjiReader(COMMAND)
    text = "東京タワー | Live\n1 | 夜に駆ける ひらがな"
    assert reader.read(text) == "トウキョウタワー | Live\n1 | ヨルにカケる ひらがな"
    ((args, kwargs),) = fake.calls
    assert list(args) == list(COMMAND)
    assert kwargs["input"] == "東京タワー\n夜に駆ける"
    assert kwargs["timeout"] > 0
    assert "shell" not in kwargs


def test_text_without_kanji_does_not_run_kakasi(kakasi):
    fake = kakasi()
    assert KanjiReader(COMMAND).read("ひらがな カタカナ 千円 Café") == (
        "ひらがな カタカナ 千円 Café"
    )
    assert fake.calls == []


def test_native_kanji_stay_out_of_the_runs(kakasi):
    fake = kakasi({"三": "サン"})
    assert KanjiReader(COMMAND).read("三千円") == "サン千円"
    assert fake.calls[0][1]["input"] == "三"


def test_readings_are_cached_per_text(kakasi):
    fake = kakasi({"東京": "トウキョウ"})
    reader = KanjiReader(COMMAND)
    assert reader.read("東京") == reader.read("東京") == "トウキョウ"
    assert len(fake.calls) == 1


@pytest.mark.parametrize(
    "error", [TimeoutExpired("kakasi", 2), OSError("failed"), UnicodeError("bad")]
)
def test_kakasi_failure_keeps_the_text_and_warns_once(kakasi, capsys, error):
    kakasi(error=error)
    reader = KanjiReader(COMMAND)
    assert reader.read("東京") == "東京"
    assert reader.read("京都") == "京都"
    assert len(capsys.readouterr().err.splitlines()) == 1


def test_missing_kakasi_is_not_run_again(kakasi, capsys):
    fake = kakasi(error=FileNotFoundError("kakasi"))
    reader = KanjiReader(COMMAND)
    assert reader.read("東京") == "東京"
    assert reader.read("京都") == "京都"
    assert len(fake.calls) == 1
    assert "kakasi" in capsys.readouterr().err


def test_disabled_reader_keeps_the_text(kakasi):
    fake = kakasi()
    assert KanjiReader(None).read("東京") == "東京"
    assert fake.calls == []


@pytest.mark.parametrize(
    "reading", ["トウ�", "トウ\tキョウ", "Tokyo", "トウ\x1bキョウ", "", "ト" * 40]
)
def test_invalid_readings_keep_their_run(kakasi, reading):
    kakasi({"東京": reading, "京都": "キョウト"})
    assert KanjiReader(COMMAND).read("東京 京都") == "東京 キョウト"


def test_output_with_another_line_count_keeps_the_text(kakasi):
    kakasi({"東京": "トウ\nキョウ"})
    assert KanjiReader(COMMAND).read("東京 京都") == "東京 京都"


def test_display_shows_kanji_readings_in_katakana(monkeypatch, kakasi):
    kakasi({"東京タワー": "トウキョウタワー"})
    monkeypatch.setattr(display_module, "KAKASI_COMMAND", COMMAND)
    shown, port = make_display(monkeypatch, 20)
    shown._print("東京タワー", vanish_time=0)
    assert DEFINE not in port.writes[0]
    assert port.writes[0].endswith(b"\xc4\xb3\xb7\xae\xb3\xc0\xdc\xb0")  # ﾄｳｷｮｳﾀﾜｰ


@pytest.mark.skipif(shutil.which("kakasi") is None, reason="kakasi not installed")
def test_real_kakasi_reads_kanji():
    reader = KanjiReader(COMMAND)
    assert reader.read("東京タワー | 夜に駆ける") == "トウキョウタワー | ヨルにカケる"
