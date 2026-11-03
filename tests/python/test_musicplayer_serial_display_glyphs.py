"""Tests of the serial display custom characters and transliteration."""

import pytest
from serial_display_fakes import (
    CLEAR,
    CURSOR,
    DEFINE,
    GLYPHS_FILE,
    LATIN,
    LOAD_GLYPHS,
    SETUP,
    SYNTHETIC,
    Display,
    FakePort,
    Glyphs,
    display_module,
    make_display,
    rows_of,
)

pytestmark = pytest.mark.usefixtures("synthetic_glyphs")


class Screen:
    """Display emulator checking the bytes the driver sends after setup."""

    def __init__(self, columns, rows=2):
        self.columns = columns
        self.slots = [None] * 8
        self.cells = {}
        self.cursor = (1, 1)
        self.native = set(display_module.NATIVE_BYTES.values())

    def feed(self, data):
        index = 0
        while index < len(data):
            if data[index] == 0xFE:
                index = self._command(data, index)
                continue
            byte = data[index]
            assert byte in self.native or (byte < 8 and self.slots[byte]), hex(byte)
            self.cells[self.cursor] = byte
            self.cursor = (self.cursor[0] + 1, self.cursor[1])
            index += 1

    def _command(self, data, index):
        command = data[index + 1]
        if command == 0x58:
            self.cells.clear()
            self.cursor = (1, 1)
            return index + 2
        if command == 0x47:
            self.cursor = (data[index + 2], data[index + 3])
            return index + 4
        assert command == 0x4E, hex(command)
        slot = data[index + 2]
        assert slot < 8
        # A visible cell must never change shape
        assert slot not in self.visible()
        self.slots[slot] = data[index + 3 : index + 11]
        return index + 11

    def visible(self):
        return {byte for (col, _), byte in self.cells.items() if col <= self.columns}

    def row(self, number):
        """Visible row, custom characters as their rows."""
        return [
            self.slots[byte] if byte < 8 else byte
            for (col, row), byte in sorted(self.cells.items())
            if row == number and col <= self.columns
        ]


def show(monkeypatch, text, columns=60, glyphs=SYNTHETIC):
    """Print a text on an emulated display, returning the screen and the writes."""
    shown, port = make_display(monkeypatch, columns, glyphs)
    shown._print(text, vanish_time=0)
    screen = Screen(columns)
    for write in port.writes:
        screen.feed(write)
    return screen, port.writes


def definitions(writes):
    return sum(write.count(DEFINE) for write in writes)


def glyph(char):
    return SYNTHETIC.bitmaps[char]


def test_cafe_defines_one_slot_after_the_clear(display):
    shown, port = display
    shown._print("Café", vanish_time=0)
    assert port.writes == [
        CLEAR + DEFINE + b"\x00" + glyph("é") + CURSOR + b"\x03\x01" + b"Caf\x00"
    ]


def test_a_loaded_glyph_is_not_redefined(display):
    shown, port = display
    shown._print("Café", vanish_time=0)
    shown._print("é!", vanish_time=0)
    assert port.writes[1] == CLEAR + CURSOR + b"\x04\x01" + b"\x00!"


def test_decomposed_text_is_normalized_before_display(display):
    shown, port = display
    shown._print("Cafe\u0301", vanish_time=0)
    assert port.writes[0].endswith(b"Caf\x00")


def test_native_symbols_use_the_display_table(display):
    shown, port = display
    shown._print("ü°→", vanish_time=0)
    assert port.writes == [CLEAR + CURSOR + b"\x04\x01" + b"\xf5\xdf\x7e"]


@pytest.mark.parametrize("char", ["\\", "~"])
def test_backslash_and_tilde_use_custom_characters(monkeypatch, char):
    screen, writes = show(monkeypatch, f"a{char}b")
    assert screen.row(1) == [ord("a"), glyph(char), ord("b")]


def test_nine_glyphs_get_eight_slots_and_the_least_frequent_falls_back(monkeypatch):
    text = " ".join(char * 2 for char in LATIN[:8]) + " " + LATIN[8]
    screen, writes = show(monkeypatch, text)
    assert definitions(writes) == 8
    assert screen.row(1)[-1] == ord("e")


def test_frequency_ties_drop_the_latest_character(monkeypatch):
    screen, writes = show(monkeypatch, " ".join(LATIN[:9]))
    assert definitions(writes) == 8
    assert screen.row(1)[0] == glyph(LATIN[0])
    assert screen.row(1)[-1] == ord("e")


def test_expensive_fallback_has_priority_over_frequency(monkeypatch):
    # "♪" has no fallback: it keeps its slot though less frequent than the others
    text = " ".join(char * 2 for char in LATIN[:8]) + " ♪"
    screen, writes = show(monkeypatch, text)
    assert screen.row(1)[-1] == glyph("♪")
    assert screen.row(1)[-4:-1] == [ord("e"), ord("e"), 0x20]


def test_a_word_is_never_mixed_glyphs_and_transliteration(monkeypatch):
    # "è" is the least frequent: its word falls back whole, "é" keeps its glyph
    text = "éè " + " ".join(char * 2 for char in "àáâãåêë") + " é"
    screen, writes = show(monkeypatch, text)
    assert screen.row(1)[:3] == [ord("e"), ord("e"), 0x20]
    assert screen.row(1)[-1] == glyph("é")


def test_scrolling_text_uses_more_glyphs_than_slots(monkeypatch):
    shown, port = make_display(monkeypatch, columns=10)
    shown._print(" ".join(LATIN), vanish_time=0)
    screen = Screen(10)
    for write in port.writes:
        screen.feed(write)
    sent = b"".join(port.writes)
    assert definitions(port.writes) == len(LATIN)
    assert not any(letter in sent for letter in b"aeiou")


def test_scroll_steps_fit_the_serial_bandwidth(monkeypatch):
    # 19200 baud 8N1 is 1920 bytes/s, 192 bytes per step at 10 Hz
    shown, port = make_display(monkeypatch, columns=20)
    shown._print(f"{' '.join(LATIN)}\n{''.join(reversed(LATIN))}", vanish_time=0)
    assert len(port.writes) > 2
    assert max(map(len, port.writes[1:])) <= 192


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Straße", b"Strasse"),
        ("5€ €5", b"5 EUR EUR 5"),
        ("Love東京", b"Love Dong Jing"),
        ("ﬁn", b"fin"),
        ("Đorđe", b"Dorde"),
        ("½", b"1/2"),
        ("a♫b", b"ab"),
    ],
)
def test_transliteration_keeps_words_apart(text, expected):
    plain = Glyphs.from_rows({})
    assert bytes(plain.encode_row(text, set())) == expected


def test_transliterated_words_keep_only_latin_native_letters():
    glyphs = LOAD_GLYPHS(GLYPHS_FILE)
    row = glyphs.encode_row("Έλληνας Лебедь Grüße 20°", set())
    assert bytes(row) == b"Ellenas Lebed' Gr\xf5sse 20\xdf"


def test_homoglyphs_of_native_characters_are_native():
    glyphs = Glyphs.from_rows({0x41: rows_of(1), 0x410: rows_of(1), 0xE9: rows_of(2)})
    assert glyphs.native["А"] == 0x41
    assert set(glyphs.bitmaps) == {"é"}


def test_no_command_prefix_or_control_byte_is_ever_sent_as_text(monkeypatch):
    glyphs = LOAD_GLYPHS(GLYPHS_FILE)
    shown, port = make_display(monkeypatch, columns=20, glyphs=glyphs)
    codes = [
        *range(0, 0x3400, 7),
        *range(0x3000, 0x3100),
        *range(0x4E00, 0x5000, 5),
        *range(0xFF00, 0xFFF0),
        *range(0x1F300, 0x1F700, 13),
        *(0xFE, 0x5C, 0x7E),
    ]
    # One emulator for all screens: custom characters stay loaded between screens
    screen = Screen(20)
    for start in range(0, len(codes), 30):
        port.writes.clear()
        shown._print("".join(map(chr, codes[start : start + 30])), vanish_time=0)
        for write in port.writes:
            screen.feed(write)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("a\r\nb\tc\fd", "a b c d"),
        ("  a\x00\x7f\x85b  ", "a b"),
        ("a\u200bb\u2028c", "ab c"),
        ("e\u0301 \u0301", "é"),
    ],
)
def test_sanitize_turns_controls_into_single_spaces(text, expected):
    assert display_module.sanitize(text) == expected


def test_metadata_control_characters_become_spaces():
    metadata = {"xesam:title": "Line\none", "xesam:artist": ["A\tB"]}
    assert display_module.get_display_text(metadata) == "A B\nLine one"


def test_reconnect_resends_setup_and_custom_characters(monkeypatch, display):
    shown, port = display
    shown._print("é", vanish_time=0)
    new_port = FakePort()

    def broken(data):
        raise display_module.SerialException

    port.write = broken
    monkeypatch.setattr(Display, "_get_device", lambda self: new_port)
    shown._write(b"x")
    assert new_port.writes == [SETUP + DEFINE + b"\x00" + glyph("é") + b"x"]


def test_startup_indicator_shows_then_clears(monkeypatch):
    port = FakePort()
    monkeypatch.setattr(Display, "_get_device", lambda self: port)
    monkeypatch.setattr(Display, "_sleep", lambda self, seconds: None)
    Display(columns=10)
    assert CLEAR + CURSOR + b"\x05\x01*" in port.writes
    assert port.writes[-1] == CLEAR


def test_glyph_file_parses_and_covers_latin_letters():
    glyphs = LOAD_GLYPHS(GLYPHS_FILE)
    assert len(glyphs.bitmaps) > 1000
    assert {"é", "\\", "~", "♪"} <= set(glyphs.bitmaps)
    assert glyphs.native["А"] == ord("A")


def test_missing_glyph_file_disables_custom_characters(tmp_path, capsys):
    glyphs = LOAD_GLYPHS(tmp_path / "missing.txt")
    assert glyphs.bitmaps == {}
    assert "transliterating" in capsys.readouterr().err


@pytest.mark.parametrize(
    "line", ["00E9", "00E9 00", "00E9 2000000000000000", "110000 0000000000000000"]
)
def test_invalid_glyph_line_is_rejected(line):
    with pytest.raises(ValueError, match="line 2"):
        display_module.parse_glyphs(["# header", line])


def test_charset_test_shows_every_code_but_the_command_prefix(display, capsys):
    shown, port = display
    shown.charset_test(page_seconds=0)
    pages = port.writes
    assert len(pages) == 8
    shown_codes = b"".join(page[2:] for page in pages[:-1])
    assert all(code in shown_codes for code in range(0x20, 0x100) if code != 0xFE)
    assert b"\xfe" not in shown_codes.replace(CURSOR, b"")
    assert pages[-1].startswith(CLEAR + DEFINE + b"\x00" + display_module.TEST_GLYPH)
    assert b"00:\x00 08:\x08" in pages[-1]
    out = capsys.readouterr().out
    assert "Page 8/8" in out
    assert "codes 0xE0-0xEF, expected (· not used natively): αäβεμσρ·√···¢·ñö" in out


def test_main_runs_the_charset_test(monkeypatch, capsys):
    port = FakePort()
    monkeypatch.setattr(Display, "_get_device", lambda self: port)
    monkeypatch.setattr(display_module, "CHARSET_TEST_PAGE_SECONDS", 0)
    monkeypatch.setattr(Display.charset_test, "__defaults__", (0,))
    display_module.main(["--charset-test"])
    assert "Page 8/8" in capsys.readouterr().out
    assert port.writes[-1] == CLEAR
