#! /usr/bin/env python3
"""Music player display."""

# Copyright (C) 2020 J.Goutin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__version__ = "1.0.3"
__copyright__ = "Copyright 2020 J.Goutin"

from threading import Condition, Thread
from time import monotonic, sleep
from typing import Any

from serial import Serial, SerialException
from serial.tools.list_ports import comports
from unidecode import unidecode

# Track information displayed by row
ROW_INFO = ((("albumArtist", "artist"), "album"), ("trackNumber", "title"))

# Device commands
# Reference: Matrix Orbital OK202-25 Technical Manual v1.1
CHANGE_STARTUP_SCREEN = b"\xfe\x40"  # + Message text
BRIGHTNESS_ON = b"\xfe\x42"  # + duration in minutes (0 for infinite)
AUTO_LINE_WRAP_ON = b"\xfe\x43"
AUTO_LINE_WRAP_OFF = b"\xfe\x44"
BRIGHTNESS_OFF = b"\xfe\x46"
SET_CURSOR_POSITION = b"\xfe\x47"  # + column and row values (starting from 1)
GO_HOME = b"\xfe\x48"
AUTO_SCROLL_ON = b"\xfe\x51"
AUTO_SCROLL_OFF = b"\xfe\x52"
BLINKING_CURSOR_ON = b"\xfe\x53"
BLINKING_CURSOR_OFF = b"\xfe\x54"
CLEAR_SCREEN = b"\xfe\x58"
SET_AND_SAVE_BRIGHTNESS = b"\xfe\x98"  # + brightness value, from 0 to 255
SET_BRIGHTNESS = b"\xfe\x99"  # + brightness value
UNDERLINE_CURSOR_ON = b"\xfe\x4a"
UNDERLINE_CURSOR_OFF = b"\xfe\x4b"
MOVE_CURSOR_BACK = b"\xfe\x4c"
MOVE_CURSOR_FORWARD = b"\xfe\x4d"


class DisplayInterrupt(Exception):
    """Exception interrupting display."""


class Display(Thread):
    """Display device.

    Args:
        name: Display name as showed in serial port description.
        baud_rate: Baud rate of the serial communication.
        columns: Number of columns of the display.
        rows: Number of rows of the display.
        timeout: Display initialization timeout.
        brightness: Display brightness value, from 0 (dim) to 255 (bright).
        scroll_speed: Speed of the scrolling when displaying a line longer than the
            number of row. Value is the update frequency in Hz.
        vanish_time: Time to wait in seconds to vanish a displayed text.
            0 to never vanish.
        scroll_wait: Time to wait in second before scrolling a text longer than the
            number of rows.
        startup_indicator: If True, show something on screen on start to show that the
            program started successfully.
    """

    def __init__(
        self,
        name: str = "OK202-25-USB",
        baud_rate: int = 19200,
        columns: int = 20,
        rows: int = 2,
        timeout: int = 30,
        brightness: int = 255,
        scroll_speed: int = 10,
        vanish_time: float = 1.5,
        scroll_wait: float = 0.5,
        startup_indicator: bool = True,
    ) -> None:
        super().__init__()

        # Get device
        self._device_name = name
        self._device_baud_rate = baud_rate
        self._device_timeout = timeout
        self._device = self._get_device()
        self._scroll_speed = scroll_speed
        self._scroll_wait = scroll_wait
        self._columns = columns
        self._rows = rows
        self._vanish = vanish_time

        # Only the latest queued text matters: it replaces the pending one
        self._pending: bytes | None = None
        self._exit = False
        self._condition = Condition()

        # Initialize device
        self._write(
            b"".join(
                (
                    CLEAR_SCREEN,
                    CHANGE_STARTUP_SCREEN,
                    b" " * (rows * columns),
                    SET_AND_SAVE_BRIGHTNESS,
                    bytes((brightness,)),
                    BRIGHTNESS_ON,
                    b"\x00",
                    AUTO_SCROLL_OFF,
                    AUTO_LINE_WRAP_OFF,
                )
            )
        )
        if startup_indicator:
            for i in range(columns, 4, -2):
                self._print(
                    f".{(i - 2) * ' '}.".encode(), scroll_wait=0.025, vanish_time=0.025
                )
            self._print(b"|", vanish_time=0.025, scroll_wait=0.025)
            self._print(b"*", vanish_time=0.15, scroll_wait=0.10)

    def __enter__(self) -> "Display":
        self.start()
        return self

    def __exit__(self, *_: object) -> None:
        with self._condition:
            self._exit = True
            self._condition.notify_all()
        self.join()
        self._print(b"")
        self._device.close()

    def _write(self, data: bytes) -> int:
        """Write on device, reconnecting to it on failure.

        Args:
            data: Data.

        Returns:
            Written data size.
        """
        while True:
            try:
                return self._device.write(data)
            except SerialException:
                self._device = self._get_device()

    def queue_print(self, text: bytes) -> None:
        """Queue the text to print on the display, replacing any pending text.

        Each line of the text is displayed on a different row. If the number of lines
        is greater than the number of rows, extra lines are ignored.

        If line length is longer than the number of columns, the text is scrolled
        horizontally.

        If text is empty, only clear the screen.

        Args:
            text: Text to display.
        """
        with self._condition:
            self._pending = text
            self._condition.notify_all()

    def _find_port(self) -> str | None:
        """Find the serial port of the device.

        Returns:
            Port path. None if the device is not connected.
        """
        return next(
            (port for port, desc, _ in comports() if self._device_name in desc), None
        )

    def _get_device(self) -> Serial:
        """Get the device, waiting for it to be connected.

        Returns:
            Device serial object.

        Raises:
            SerialException: The port cannot be opened within the timeout.
        """
        while (port := self._find_port()) is None:
            sleep(0.25)

        deadline = monotonic() + self._device_timeout
        while True:
            try:
                return Serial(port=port, baudrate=self._device_baud_rate, timeout=1)
            except SerialException:
                if monotonic() >= deadline:
                    raise
                sleep(0.25)

    def _print(
        self,
        text: bytes,
        scroll_wait: float | None = None,
        vanish_time: float | None = None,
    ) -> None:
        """Print the text on the display.

        Print first text portion, or full centered text is short enough.
        Then print and scroll until the end of the text

        Args:
            text: Text to display.
            scroll_wait: Time to wait in second before scrolling a text longer than the
                number of rows.
            vanish_time: Time to wait in seconds to vanish a displayed text.
                0 to never vanish.

        Raises:
            DisplayInterrupt: A new text is pending.
        """
        if not text:
            self._write(CLEAR_SCREEN)
            return

        cols = self._columns
        row_texts = text.split(b"\n")[: self._rows]
        to_write = [CLEAR_SCREEN]
        for row, row_text in enumerate(row_texts):
            col = max(cols // 2 - len(row_text) // 2, 1)
            if col > 1 or row:
                to_write.extend((SET_CURSOR_POSITION, bytes((col, row + 1))))
            to_write.append(row_text[:cols])

        self._write(b"".join(to_write))
        self._sleep(self._scroll_wait if scroll_wait is None else scroll_wait)

        # Each step shifts the rows longer than the display by one more character
        steps = max(map(len, row_texts)) - cols
        if steps > 0:
            period = 1 / self._scroll_speed
            for step in range(1, steps + 1):
                self._sleep(period)
                self._write(
                    b"".join(
                        SET_CURSOR_POSITION
                        + bytes((1, row + 1))
                        + row_text[step : step + cols]
                        for row, row_text in enumerate(row_texts)
                        if len(row_text) - cols >= step
                    )
                )
            self._sleep(period)

        vanish_time = self._vanish if vanish_time is None else vanish_time
        if vanish_time:
            self._sleep(vanish_time)
            self._write(CLEAR_SCREEN)

    def _sleep(self, seconds: float) -> None:
        """Sleep, but interrupt if a new text is pending.

        Args:
            seconds: Number of seconds to sleeps.

        Raises:
            DisplayInterrupt: Risen if a text is pending or the display is exiting.
        """
        with self._condition:
            if self._condition.wait_for(self._must_interrupt, seconds):
                raise DisplayInterrupt

    def _must_interrupt(self) -> bool:
        """Tell if the current display must stop for a pending text or exit."""
        return self._pending is not None or self._exit

    def run(self) -> None:
        """Thread activity."""
        while True:
            with self._condition:
                self._condition.wait_for(self._must_interrupt)
                if self._exit:
                    return
                text, self._pending = self._pending, None
            try:
                self._print(text)
            except DisplayInterrupt:
                continue

    @property
    def device_name(self) -> str:
        """Device name.

        Returns:
            Device name.
        """
        return f"{self._device_name} (port={self._device.portstr})"


def get_xesam_property(
    metadata: dict[str, Any], names: str | tuple[str, ...]
) -> bytes | None:
    """Get Xesam property value.

    Value text is normalized to ASCII before return.

    Args:
        metadata: MPRIS Metadata.
        names: Property name from Xesam specification.
            If tuple, search for properties in the specified order and returns the
            first match.

    Returns:
        Value. None if no value found.
    """
    if isinstance(names, str):
        names = (names,)

    for name in names:
        try:
            value = metadata[f"xesam:{name}"]
        except KeyError:
            continue

        if isinstance(value, list):
            value = ", ".join(value)
        elif isinstance(value, int):
            return str(value).encode()
        return unidecode(value, replace_str="").encode("ascii", "ignore")
    return None


def get_display_text(metadata: dict[str, Any]) -> bytes:
    """Get the text to display for a track, one line by row of `ROW_INFO`.

    Args:
        metadata: MPRIS Metadata.

    Returns:
        Text, empty values and their separators are omitted.
    """
    return b"\n".join(
        b" | ".join(filter(None, (get_xesam_property(metadata, name) for name in row)))
        for row in ROW_INFO
    )


def main() -> None:
    """Show the track information of the first music player on the display."""
    # Optional dependency, only needed to run the program
    import gi

    gi.require_version("Playerctl", "2.0")
    from gi.repository import GLib, Playerctl

    try:
        player = None
        print("Getting music player...")
        while not player:
            try:
                player_name = Playerctl.list_players()[0]
                player = Playerctl.Player.new_from_name(player_name)
                print(f"Music player found: {player_name.name}")
            except IndexError:
                sleep(0.5)

        print("Getting display device...")
        with Display(brightness=1) as display:

            def on_metadata(
                _player: Playerctl.Player, metadata: dict[str, Any]
            ) -> None:
                """Print track information on track change."""
                display_text = get_display_text(metadata)
                if display_text.strip():
                    display.queue_print(display_text)

            print(f"Display device found: {display.device_name}")
            player.connect("metadata", on_metadata)
            GLib.MainLoop().run()

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
