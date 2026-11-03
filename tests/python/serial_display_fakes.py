"""Fakes and fixtures of the serial display driver tests (a pytest plugin)."""

import pytest
from conftest import REPOSITORY, load_script

display_module = load_script("musicplayer/files/musicplayer_serial_display.py")
Display = display_module.Display
CLEAR = display_module.CLEAR_SCREEN
CURSOR = display_module.SET_CURSOR_POSITION
DEFINE = display_module.DEFINE_CUSTOM_CHARACTER
LOAD_GLYPHS = display_module.load_glyphs
Glyphs = display_module.Glyphs
GLYPHS_FILE = (
    REPOSITORY / "roles/musicplayer/files/musicplayer_serial_display_glyphs.txt"
)
#: Setup resent after a reconnection, for the default brightness.
SETUP = b"\xfe\x99\xff" + b"\xfe\x42\x00" + b"\xfe\x52" + b"\xfe\x44"
#: Characters needing a custom character in the synthetic glyphs, all Latin.
LATIN = "àáâãåèéêëìíîòóôõ"


def rows_of(index):
    """Distinct synthetic rows, unlike any native glyph."""
    return bytes((0x1F, index, 0, 0, 0, 0, 0, 0x1F))


#: Synthetic glyphs: one per `LATIN` character, a symbol, backslash and tilde.
SYNTHETIC = Glyphs.from_rows(
    {ord(char): rows_of(index) for index, char in enumerate(LATIN + "♪\\~")}
)


class FakePort:
    """Serial port recording the writes."""

    portstr = "/dev/ttyFAKE"

    def __init__(self):
        self.writes = []

    def write(self, data):
        self.writes.append(data)
        return len(data)

    def close(self):
        pass


@pytest.fixture
def synthetic_glyphs(monkeypatch):
    """Use the synthetic glyphs by default instead of the deployed file."""
    monkeypatch.setattr(display_module, "load_glyphs", lambda: SYNTHETIC)


@pytest.fixture
def display(monkeypatch):
    port = FakePort()
    monkeypatch.setattr(Display, "_get_device", lambda self: port)
    monkeypatch.setattr(Display, "_sleep", lambda self, seconds: None)
    shown = Display(startup_indicator=False, columns=10, rows=2, scroll_speed=10)
    port.writes.clear()
    return shown, port


def make_display(monkeypatch, columns, glyphs=SYNTHETIC):
    """Display on a fake port, without startup indicator nor sleeps."""
    port = FakePort()
    monkeypatch.setattr(Display, "_get_device", lambda self: port)
    monkeypatch.setattr(Display, "_sleep", lambda self, seconds: None)
    shown = Display(startup_indicator=False, columns=columns, glyphs=glyphs)
    port.writes.clear()
    return shown, port
