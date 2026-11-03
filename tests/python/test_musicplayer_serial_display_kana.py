"""Tests of the serial display Japanese text, shown with the built-in katakana."""

import pytest
from serial_display_fakes import (
    CLEAR,
    CURSOR,
    DEFINE,
    display_module,
    make_display,
)

pytestmark = pytest.mark.usefixtures("synthetic_glyphs")


def first_write(monkeypatch, text, columns=40):
    shown, port = make_display(monkeypatch, columns)
    shown._print(text, vanish_time=0)
    return port.writes[0]


@pytest.mark.parametrize(
    ("char", "byte"),
    [("｡", 0xA1), ("･", 0xA5), ("ｦ", 0xA6), ("ｧ", 0xA7), ("ｰ", 0xB0), ("ｱ", 0xB1)]
    + [("ﾝ", 0xDD), ("ﾞ", 0xDE), ("ﾟ", 0xDF), ("°", 0xDF)]
    + [("千", 0xFA), ("万", 0xFB), ("円", 0xFC)],
)
def test_half_width_katakana_and_some_kanji_are_native(char, byte):
    assert display_module.NATIVE_BYTES[char] == byte


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("ガパヴ", "ｶﾞﾊﾟｳﾞ"),
        ("ヷヸ", "ﾜﾞｲﾞ"),
        ("ァッャ", "ｧｯｬ"),
        ("ヮヰヱヵヶ", "ﾜｲｴｶｹ"),
        ("ひらがな", "ﾋﾗｶﾞﾅ"),
        ("ゔぁゕ", "ｳﾞｧｶ"),
        ("ラーメン・スープ", "ﾗｰﾒﾝ･ｽｰﾌﾟ"),
        ("「。、」", "｢｡､｣"),
        ("゛゜", "ﾞﾟ"),
        ("ココヽ いすゞ ガヽ", "ｺｺｺ ｲｽｽﾞ ｶﾞｶ"),
        ("ヽゞ", "ヽヾ"),
        ("ＡＢＣ　１！～", "ABC 1!~"),
        ("東京 é ｶ", "東京 é ｶ"),
    ],
)
def test_japanese_forms_convert_to_the_display_forms(text, expected):
    assert display_module.to_display_forms(text) == expected


def test_voiced_kana_take_two_cells_before_centring(monkeypatch):
    assert first_write(monkeypatch, "ガ", columns=10) == (
        CLEAR + CURSOR + b"\x04\x01" + b"\xb6\xde"
    )


def test_a_japanese_title_uses_no_custom_character(monkeypatch):
    data = first_write(monkeypatch, "ポケットモンスター | ひらがなのうた\n1 | 千円")
    assert DEFINE not in data
    assert b"\xce\xdf\xb9\xaf\xc4" in data  # ﾎﾟｹｯﾄ
    assert b"\xfa\xfc" in data


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("東京タワー", b"Dong Jing \xc0\xdc\xb0"),
        ("タワー東", b"\xc0\xdc\xb0 Dong"),
        ("林檎の唄", b"Lin Qin \xc9 Bai"),
    ],
)
def test_kanji_fall_back_without_transliterating_the_kana(monkeypatch, text, expected):
    assert first_write(monkeypatch, text).endswith(expected)


def test_charset_test_tells_the_expected_kana(monkeypatch, capsys):
    shown, _ = make_display(monkeypatch, 20)
    shown.charset_test(page_seconds=0)
    out = capsys.readouterr().out
    assert "0xC0-0xCF, expected (· not used natively): ﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏ" in out
    assert "0xD0-0xDF, expected (· not used natively): ﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝﾞ°" in out
    assert "0xF0-0xFF, expected (· not used natively): ··θ∞ΩüΣπ··千万円÷·█" in out
