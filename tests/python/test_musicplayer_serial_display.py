"""Tests of the serial display driver, with a fake serial port."""

import time

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


def test_get_display_text_joins_values_by_row_and_skips_empty_ones():
    metadata = {
        "xesam:artist": "Björk",
        "xesam:album": "Debut",
        "xesam:trackNumber": 3,
        "xesam:title": "Human Behaviour",
    }
    assert display_module.get_display_text(metadata) == (
        b"Bjork | Debut\n3 | Human Behaviour"
    )
    assert display_module.get_display_text({"xesam:title": "T"}) == b"\nT"


REAL_GET_DEVICE = Display._get_device


def test_get_device_waits_for_the_port_then_opens_it(monkeypatch, display):
    shown, _ = display
    ports = iter(
        [[], [("/dev/other", "Other", ""), ("/dev/ttyUSB0", "OK202-25-USB", "")]]
    )
    monkeypatch.setattr(display_module, "comports", lambda: next(ports))
    monkeypatch.setattr(display_module, "sleep", lambda _: None)
    monkeypatch.setattr(display_module, "Serial", lambda **kwargs: kwargs)
    assert REAL_GET_DEVICE(shown) == {
        "port": "/dev/ttyUSB0",
        "baudrate": 19200,
        "timeout": 1,
    }


def test_get_device_raises_when_the_port_cannot_be_opened_in_time(monkeypatch, display):
    shown, _ = display
    shown._device_timeout = 0
    monkeypatch.setattr(
        display_module, "comports", lambda: [("/dev/x", "OK202-25-USB", "")]
    )

    def serial(**_):
        raise display_module.SerialException

    monkeypatch.setattr(display_module, "Serial", serial)
    with pytest.raises(display_module.SerialException):
        REAL_GET_DEVICE(shown)


def test_new_text_interrupts_a_running_sleep(monkeypatch):
    monkeypatch.setattr(Display, "_get_device", lambda self: FakePort())
    shown = Display(startup_indicator=False)
    shown.queue_print(b"x")
    with pytest.raises(display_module.DisplayInterrupt):
        shown._sleep(5)


def test_thread_prints_the_latest_text_and_clears_on_exit(monkeypatch):
    port = FakePort()
    monkeypatch.setattr(Display, "_get_device", lambda self: port)
    with Display(
        startup_indicator=False, columns=10, vanish_time=0, scroll_wait=0
    ) as d:
        d.queue_print(b"hello")
        for _ in range(200):
            if len(port.writes) > 1:
                break
            time.sleep(0.01)
    assert CLEAR + CURSOR + b"\x03\x01hello" in port.writes
    assert port.writes[-1] == CLEAR
