"""Tests of the serial display driver, with a fake serial port."""

import pytest
from conftest import load_script

display_module = load_script("musicplayer/files/musicplayer_serial_display.py")
Display = display_module.Display
CLEAR = display_module.CLEAR_SCREEN
CURSOR = display_module.SET_CURSOR_POSITION


class FakePort:
    portstr = "/dev/ttyFAKE"

    def __init__(self):
        self.writes = []

    def write(self, data):
        self.writes.append(data)
        return len(data)

    def close(self):
        pass


@pytest.fixture
def display(monkeypatch):
    port = FakePort()
    monkeypatch.setattr(Display, "_get_device", lambda self: port)
    monkeypatch.setattr(Display, "_sleep", lambda self, seconds: None)
    shown = Display(startup_indicator=False, columns=10, rows=2, scroll_speed=10)
    port.writes.clear()
    return shown, port


def test_init_sequence(monkeypatch):
    port = FakePort()
    monkeypatch.setattr(Display, "_get_device", lambda self: port)
    Display(startup_indicator=False, columns=20, rows=2, brightness=7)
    assert port.writes == [
        CLEAR
        + b"\xfe\x40"
        + b" " * 40
        + b"\xfe\x98\x07"
        + b"\xfe\x42\x00"
        + b"\xfe\x52"
        + b"\xfe\x44"
    ]


def test_short_text_is_centered_per_row(display):
    shown, port = display
    shown._print(b"abcd\nxy", vanish_time=0)
    # Row 1: column 10 // 2 - 4 // 2 = 3. Row 2: column 4.
    assert port.writes == [CLEAR + CURSOR + b"\x03\x01abcd" + CURSOR + b"\x04\x02xy"]


def test_text_filling_the_row_has_no_cursor_move_on_first_row(display):
    shown, port = display
    shown._print(b"0123456789", vanish_time=0)
    assert port.writes == [CLEAR + b"0123456789"]


def test_extra_rows_are_ignored(display):
    shown, port = display
    shown._print(b"a\nb\nc", vanish_time=0)
    assert b"c" not in port.writes[0]


def test_long_line_scrolls_one_character_at_a_time(display):
    shown, port = display
    shown._print(b"0123456789AB", vanish_time=0)
    assert port.writes == [
        CLEAR + b"0123456789",
        CURSOR + b"\x01\x01" + b"123456789A",
        CURSOR + b"\x01\x01" + b"23456789AB",
    ]


def test_only_long_rows_scroll(display):
    shown, port = display
    shown._print(b"0123456789A\nhi", vanish_time=0)
    assert all(b"hi" not in write for write in port.writes[1:])
    assert all(write.startswith(CURSOR + b"\x01\x01") for write in port.writes[1:])


def test_vanish_clears_the_screen(display):
    shown, port = display
    shown._print(b"hi", vanish_time=1)
    assert port.writes[-1] == CLEAR


def test_empty_text_only_clears(display):
    shown, port = display
    shown._print(b"")
    assert port.writes == [CLEAR]


def test_write_reconnects_after_serial_error(monkeypatch, display):
    shown, port = display
    new_port = FakePort()

    def broken(data):
        raise display_module.SerialException

    port.write = broken
    monkeypatch.setattr(Display, "_get_device", lambda self: new_port)
    shown._write(b"x")
    assert new_port.writes == [b"x"]


@pytest.mark.parametrize(
    ("metadata", "names", "expected"),
    [
        ({"xesam:title": "Café"}, "title", b"Cafe"),
        ({"xesam:artist": ["A", "B"]}, "artist", b"A, B"),
        ({"xesam:trackNumber": 5}, "trackNumber", b"5"),
        ({"xesam:artist": "x"}, ("albumArtist", "artist"), b"x"),
        ({}, "title", None),
    ],
)
def test_get_xesam_property(metadata, names, expected):
    assert display_module.get_xesam_property(metadata, names) == expected
