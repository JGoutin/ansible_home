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

__version__ = "1.0.2"
__copyright__ = "Copyright 2020 J.Goutin"

from queue import Queue
from threading import Thread
from time import time, sleep
from typing import Any
from serial import Serial, SerialException
from serial.tools.list_ports import comports
from unidecode import unidecode

# Track information displayed by row
ROW_INFO = ((("albumArtist", "artist"), "album"), ("trackNumber", "title"))

# Device commands
# Reference: Matrix Orbital OK202-25 Technical Manual v1.1
CHANGE_STARTUP_SCREEN = b"\xFE\x40"  # + Message text
BRIGHTNESS_ON = b"\xFE\x42"  # + duration in minutes (0 for infinite)
AUTO_LINE_WRAP_ON = b"\xFE\x43"
AUTO_LINE_WRAP_OFF = b"\xFE\x44"
BRIGHTNESS_OFF = b"\xFE\x46"
SET_CURSOR_POSITION = b"\xFE\x47"  # + column and row values (starting from 1)
GO_HOME = b"\xFE\x48"
AUTO_SCROLL_ON = b"\xFE\x51"
AUTO_SCROLL_OFF = b"\xFE\x52"
BLINKING_CURSOR_ON = b"\xFE\x53"
BLINKING_CURSOR_OFF = b"\xFE\x54"
CLEAR_SCREEN = b"\xFE\x58"
SET_AND_SAVE_BRIGHTNESS = b"\xFE\x98"  # + brightness value, from 0 to 255
SET_BRIGHTNESS = b"\xFE\x99"  # + brightness value
UNDERLINE_CURSOR_ON = b"\xFE\x4A"
UNDERLINE_CURSOR_OFF = b"\xFE\x4B"
MOVE_CURSOR_BACK = b"\xFE\x4C"
MOVE_CURSOR_FORWARD = b"\xFE\x4D"


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

    __slots__ = (
        "_device",
        "_scroll_speed",
        "_vanish",
        "_scroll_wait",
        "_columns",
        "_rows",
        "_printing",
        "_queue",
        "_exit",
        "_device_name",
        "_device_baud_rate",
        "_device_timeout",
    )

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
        Thread.__init__(self)

        # Get device
        self._printing = False
        self._device_name = name
        self._device_baud_rate = baud_rate
        self._device_timeout = timeout
        self._device = self._get_device()
        self._scroll_speed = scroll_speed
        self._scroll_wait = scroll_wait
        self._columns = columns
        self._rows = rows
        self._vanish = vanish_time
        self._queue = Queue()
        self._exit = False

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

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self._exit = True
        self.queue_print(b"")  # To ensure not waiting on "Queue.get"
        self.join()
        self._print(b"")
        self._device.close()

    def _write(self, data: bytes) -> int:
        """Write on device.

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
        """Queue the text to print on the display.

        Each line of the text is displayed on a different row. If the number of lines
        is greater than the number of rows, extra lines are ignored.

        If line length is longer than the number of columns, the text is scrolled
        horizontally.

        If text is empty, only clear the screen.

        Args:
            text: Text to display.
        """
        self._queue.put(text)

    def _get_device(self) -> Serial:
        """Get the device.

        Returns:
            Device serial object.
        """
        while True:
            for port, desc, _ in comports():
                if self._device_name in desc:
                    break
            else:
                sleep(0.25)
                continue
            break

        t0 = time()
        while True:
            try:
                return Serial(port=port, baudrate=self._device_baud_rate, timeout=1)
            except SerialException:
                if time() - t0 < self._device_timeout:
                    sleep(0.25)
                    continue
                raise

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
        """
        if not text:
            self._write(CLEAR_SCREEN)
            return

        cols = self._columns
        rows = self._rows
        to_write = [CLEAR_SCREEN]

        row_texts = text.split(b"\n")
        for row, row_text in enumerate(row_texts):
            if row >= rows:
                break
            col = max(cols // 2 - len(row_text) // 2, 1)
            if col > 1 or row:
                to_write.append(SET_CURSOR_POSITION)
                to_write.append(bytes((col, row + 1)))
            to_write.append(row_text[:cols])

        self._write(b"".join(to_write))
        self._sleep(self._scroll_wait if scroll_wait is None else scroll_wait)

        if any(len(row_text) > cols for row_text in row_texts):
            period = 1 / self._scroll_speed
            while True:
                self._sleep(period)
                to_write = []
                for row, row_text in enumerate(row_texts):
                    if row >= rows:
                        break
                    elif len(row_text) <= cols:
                        continue
                    row_texts[row] = row_text = row_text[1:]
                    to_write.extend(
                        (SET_CURSOR_POSITION, bytes((1, row + 1)), row_text[:cols])
                    )
                if not to_write:
                    break
                self._write(b"".join(to_write))

        vanish_time = self._vanish if vanish_time is None else vanish_time
        if vanish_time:
            self._sleep(vanish_time)
            self._write(CLEAR_SCREEN)

    def _sleep(self, seconds: float) -> None:
        """Sleep, but interrupt if new elements in the queue.

        Args:
            seconds: Number of seconds to sleeps.

        Raises:
            DisplayInterrupt: Risen if queue is not empty.
        """
        t0 = time()
        empty = self._queue.empty
        sleep_seconds = min(0.1, seconds)
        while time() - t0 < seconds:
            if not empty() or self._exit:
                raise DisplayInterrupt()
            sleep(sleep_seconds)

    def run(self) -> None:
        """Thread activity."""
        while not self._exit:
            try:
                self._print(self._queue.get())
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
            break
        except KeyError:
            continue
    else:
        return None

    if isinstance(value, list):
        value = ", ".join(value)
    elif isinstance(value, int):
        return str(value).encode()

    return unidecode(value, replace_str="").encode("ascii", "ignore")


if __name__ == "__main__":
    import gi

    gi.require_version("Playerctl", "2.0")
    from gi.repository import Playerctl, GLib

    try:
        player = None
        print("Getting music player...")
        while not player:
            try:
                player_name = Playerctl.list_players()[0]
                player = Playerctl.Player.new_from_name(player_name)
                print(f"Music player found: {player_name.name}")
            except IndexError:
                sleep(0.1)

        print("Getting display device...")
        with Display(brightness=1) as display:

            def on_metadata(player: Playerctl.Player, metadata: dict[str, Any]) -> None:
                """Print track information on track change.

                Args:
                    player: Player instance.
                    metadata: MPRIS metadata
                """
                display_text = b"\n".join(
                    (
                        b" | ".join((value for value in row if value))
                        for row in (
                            (get_xesam_property(metadata, name) for name in row_info)
                            for row_info in ROW_INFO
                        )
                    )
                )
                if display_text.strip():
                    display.queue_print(display_text)

            print(f"Display device found: {display.device_name}")
            player.connect("metadata", on_metadata)
            GLib.MainLoop().run()

    except KeyboardInterrupt:
        pass
