"""Tests of the serial display driver, with a fake serial port."""

import threading
import time

import pytest
from serial_display_fakes import (
    CLEAR,
    CURSOR,
    Display,
    SETUP,
    FakePort,
    display_module,
)

pytestmark = pytest.mark.usefixtures("isolated_display")


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
    shown._print("abcd\nxy", vanish_time=0)
    # Row 1: column 10 // 2 - 4 // 2 = 3. Row 2: column 4.
    assert port.writes == [CLEAR + CURSOR + b"\x03\x01abcd" + CURSOR + b"\x04\x02xy"]


def test_text_filling_the_row_has_no_cursor_move_on_first_row(display):
    shown, port = display
    shown._print("0123456789", vanish_time=0)
    assert port.writes == [CLEAR + b"0123456789"]


def test_extra_rows_are_ignored(display):
    shown, port = display
    shown._print("a\nb\nc", vanish_time=0)
    assert b"c" not in port.writes[0]


def test_long_line_scrolls_one_character_at_a_time(display):
    shown, port = display
    shown._print("0123456789AB", vanish_time=0)
    assert port.writes == [
        CLEAR + b"0123456789",
        CURSOR + b"\x01\x01" + b"123456789A",
        CURSOR + b"\x01\x01" + b"23456789AB",
    ]


def test_only_long_rows_scroll(display):
    shown, port = display
    shown._print("0123456789A\nhi", vanish_time=0)
    assert all(b"hi" not in write for write in port.writes[1:])
    assert all(write.startswith(CURSOR + b"\x01\x01") for write in port.writes[1:])


def test_vanish_clears_the_screen(display):
    shown, port = display
    shown._print("hi", vanish_time=1)
    assert port.writes[-1] == CLEAR


def test_empty_text_only_clears(display):
    shown, port = display
    shown._print("")
    assert port.writes == [CLEAR]


def test_write_reconnects_after_serial_error(monkeypatch, display):
    shown, port = display
    new_port = FakePort()

    def broken(data):
        raise display_module.SerialException

    port.write = broken
    monkeypatch.setattr(Display, "_get_device", lambda self: new_port)
    assert shown._write(b"x") == 1
    assert new_port.writes == [SETUP + b"x"]


@pytest.mark.parametrize(
    ("metadata", "names", "expected"),
    [
        ({"xesam:title": "Café"}, "title", "Café"),
        ({"xesam:artist": ["A", "B"]}, "artist", "A, B"),
        ({"xesam:trackNumber": 5}, "trackNumber", "5"),
        ({"xesam:artist": "x"}, ("albumArtist", "artist"), "x"),
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
        "Björk | Debut\n3 | Human Behaviour"
    )
    assert display_module.get_display_text({"xesam:title": "T"}) == "\nT"


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
    raised = []

    def sleeper():
        try:
            shown._sleep(5)
        except display_module.DisplayInterrupt:
            raised.append(time.monotonic())

    thread = threading.Thread(target=sleeper)
    start = time.monotonic()
    thread.start()
    time.sleep(0.05)
    shown.queue_print("x")
    thread.join(5)
    assert raised
    assert raised[0] - start < 0.5


def test_burst_of_texts_only_prints_the_latest(monkeypatch):
    entered, release = threading.Event(), threading.Event()

    class BlockingPort(FakePort):
        def write(self, data):
            if b"first" in data:
                entered.set()
                release.wait(5)
            return super().write(data)

    port = BlockingPort()
    monkeypatch.setattr(Display, "_get_device", lambda self: port)
    with Display(startup_indicator=False, vanish_time=0, scroll_wait=0) as shown:
        shown.queue_print("first")
        assert entered.wait(5)
        shown.queue_print("A")
        shown.queue_print("B")
        release.set()
        for _ in range(200):
            if any(b"B" in write for write in port.writes):
                break
            time.sleep(0.01)
    assert any(b"B" in write for write in port.writes)
    assert not any(write.endswith(b"A") for write in port.writes)


def test_thread_prints_the_latest_text_and_clears_on_exit(monkeypatch):
    port = FakePort()
    monkeypatch.setattr(Display, "_get_device", lambda self: port)
    with Display(
        startup_indicator=False, columns=10, vanish_time=0, scroll_wait=0
    ) as d:
        d.queue_print("hello")
        for _ in range(200):
            if len(port.writes) > 1:
                break
            time.sleep(0.01)
    assert CLEAR + CURSOR + b"\x03\x01hello" in port.writes
    assert port.writes[-1] == CLEAR
