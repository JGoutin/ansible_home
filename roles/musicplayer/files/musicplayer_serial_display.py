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

__version__ = "1.1.0"
__copyright__ = "Copyright 2020 J.Goutin"

import re
import sys
from argparse import ArgumentParser
from bisect import bisect_right
from collections import Counter, defaultdict
from collections.abc import Iterable, Sequence, Set
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from subprocess import SubprocessError, run
from threading import Condition, Thread
from time import monotonic, sleep
from typing import Any
from unicodedata import category, combining, normalize
from unicodedata import name as unicode_name

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

# Custom characters: volatile unless "Remember" (FE 93) is on, never send it: each
# non-volatile write wears the memory. A custom character is shown by its slot id;
# 0x08-0x0F mirror the slots and are not used.
#: Command defining a custom character, + slot id and 8 rows (bit 4 leftmost pixel).
DEFINE_CUSTOM_CHARACTER = b"\xfe\x4e"
#: Number of custom character slots, ids from 0.
CUSTOM_SLOTS = 8
#: Byte of the characters used natively, from the manual "English Japanese" table.
NATIVE_BYTES = {
    **{chr(byte): byte for byte in range(0x20, 0x7E) if byte != 0x5C},
    **{chr(0xFF61 + byte - 0xA1): byte for byte in range(0xA1, 0xE0)},
    **{"千": 0xFA, "万": 0xFB, "円": 0xFC},
    **{"¥": 0x5C, "→": 0x7E, "←": 0x7F, "°": 0xDF, "α": 0xE0, "ä": 0xE1, "β": 0xE2},
    **{"ε": 0xE3, "μ": 0xE4, "σ": 0xE5, "ρ": 0xE6, "√": 0xE8, "¢": 0xEC, "ñ": 0xEE},
    **{"ö": 0xEF, "θ": 0xF2, "∞": 0xF3, "Ω": 0xF4, "ü": 0xF5, "Σ": 0xF6, "π": 0xF7},
    **{"÷": 0xFD, "█": 0xFF},
}

#: Half-width form of katakana, Japanese punctuation and voicing marks.
HALF_WIDTH_FORMS = {
    **{normalize("NFKC", chr(code)): chr(code) for code in range(0xFF61, 0xFFA0)},
    **{chr(code): chr(code) for code in range(0xFF61, 0xFFA0)},
    **{"゛": "ﾞ", "゜": "ﾟ", "ヮ": "ﾜ", "ヰ": "ｲ", "ヱ": "ｴ", "ヵ": "ｶ", "ヶ": "ｹ"},
}
#: Katakana iteration marks: suffix added to the repeated kana.
ITERATION_MARKS = {"ヽ": "", "ヾ": "ﾞ"}
#: Words of the Unicode names of scripts whose native letters are never transliterated.
PLAIN_SCRIPTS = ("LATIN", "KATAKANA", "CJK")

#: kakasi command printing kanji as katakana readings (UTF-8 needs glibc-gconv-extra).
KAKASI_COMMAND: tuple[str, ...] | None = (
    "/usr/bin/kakasi",
    *("-i", "utf8", "-o", "utf8", "-JK"),
)
#: Seconds to wait for kakasi.
KAKASI_TIMEOUT = 2.0
#: Number of texts whose kanji readings are cached.
KAKASI_CACHE_SIZE = 16
#: Longest valid reading, in characters per character of the text read.
KAKASI_MAX_EXPANSION = 6
#: Regular expression class of the kanji: iteration mark and CJK ideographs.
_KANJI = "\u3005\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff"
#: Regular expression class of the Japanese characters: kana and kanji.
_JAPANESE = f"\u3041-\u309f\u30a1-\u30ff{_KANJI}"
#: Run of Japanese characters given to kakasi, native kanji excepted (kept native).
JAPANESE_RUN = re.compile(f"(?:(?![千万円])[{_JAPANESE}])+")
#: Kanji that need a reading, native ones excepted.
KANJI = re.compile(f"(?![千万円])[{_KANJI}]")
#: Valid kakasi reading of a run.
JAPANESE_READING = re.compile(f"[{_JAPANESE}]+")

#: Default glyph file, deployed by the role.
GLYPHS_PATH = Path("/usr/local/share/musicplayer_serial_display/glyphs.txt")
#: Replacements of transliterated characters that are not native.
FALLBACK_REPLACEMENTS = str.maketrans({"\\": "/", "~": "-"})
#: Fallback cost of a character close to its one-cell fallback (é to e).
CHEAP_FALLBACK_COST = 1
#: Fallback cost of a character whose fallback is empty, longer or another script.
EXPENSIVE_FALLBACK_COST = 4
#: Unicode categories shown as a space: controls and separators.
SPACE_CATEGORIES = frozenset(("Cc", "Zs", "Zl", "Zp"))
#: Unicode categories removed: format, surrogates and marks left after NFC.
REMOVED_CATEGORIES = frozenset(("Cf", "Cs", "Mn", "Me"))
#: Seconds each page of the character table test is shown.
CHARSET_TEST_PAGE_SECONDS = 4.0
#: Custom character of the character table test: a checkerboard.
TEST_GLYPH = bytes((0x15, 0x0A) * 4)

#: Display cell: a native character byte, or the rows of a custom character.
type Cell = int | bytes


class DisplayInterrupt(Exception):
    """Exception interrupting display."""


class SlotConflict(Exception):
    """More custom characters are visible at once than there are slots.

    Args:
        glyphs: Rows of the custom characters visible at once.
    """

    def __init__(self, glyphs: Set[bytes]) -> None:
        super().__init__()
        self.glyphs = glyphs


def define_custom_character(slot: int, rows: bytes) -> bytes:
    """Get the command defining a custom character.

    Args:
        slot: Slot id.
        rows: 8 pixel rows.

    Returns:
        Command.
    """
    return DEFINE_CUSTOM_CHARACTER + bytes((slot,)) + rows


def _is_latin(char: str) -> bool:
    """Tell if a character is of the Latin script, by its Unicode name.

    Args:
        char: Character.

    Returns:
        True if Latin.
    """
    return "LATIN" in unicode_name(char, "")


def _katakana(char: str) -> str:
    """Convert hiragana to katakana, full-width ASCII and ideographic space to ASCII.

    Args:
        char: Character.

    Returns:
        Converted character, or the character itself.
    """
    code = ord(char)
    if 0x3041 <= code <= 0x3096 or code in (0x309D, 0x309E):
        return chr(code + 0x60)
    if 0xFF01 <= code <= 0xFF5E:
        return chr(code - 0xFEE0)
    return " " if char == "\u3000" else char


def to_display_forms(text: str) -> str:
    """Convert Japanese text to the forms of the display table.

    Kana become half-width katakana, voiced ones followed by their voicing mark (ガ
    to ｶﾞ); kana without half-width form become the nearest one (ヶ to ｹ). An
    iteration mark repeats the previous kana. Full-width ASCII becomes ASCII.

    Args:
        text: NFC text.

    Returns:
        Text, other characters unchanged.
    """
    forms = []
    previous = ""
    for char in map(_katakana, text):
        if char in ITERATION_MARKS and previous:
            forms.append(previous + ITERATION_MARKS[char])
            continue
        parts = normalize("NFD", char)
        if all(part in HALF_WIDTH_FORMS for part in parts):
            form = "".join(HALF_WIDTH_FORMS[part] for part in parts)
            previous = form[0] if "LETTER" in unicode_name(form[0]) else ""
        else:
            form, previous = char, ""
        forms.append(form)
    return "".join(forms)


def parse_glyphs(lines: Iterable[str]) -> dict[int, bytes]:
    """Parse a glyph file (format in `tools/generate_display_glyphs.py`).

    Args:
        lines: File lines.

    Returns:
        8 pixel rows by code point.

    Raises:
        ValueError: Invalid line.
    """
    glyphs = {}
    for number, line in enumerate(lines, 1):
        if line.startswith("#") or not line.strip():
            continue
        try:
            code, rows = line.split()
            char = chr(int(code, 16))
            bitmap = bytes.fromhex(rows)
        except ValueError as error:
            raise ValueError(f"Invalid glyph line {number}: {line!r}") from error
        if len(bitmap) != 8 or max(bitmap) > 0x1F:
            raise ValueError(f"Invalid glyph rows on line {number}: {line!r}")
        glyphs[ord(char)] = bitmap
    return glyphs


@dataclass(frozen=True, slots=True)
class Glyphs:
    """Characters the display can show, natively or as custom characters."""

    #: Rows of the characters needing a custom character.
    bitmaps: dict[str, bytes]
    #: Byte of the characters shown natively, homoglyphs of native ones included.
    native: dict[str, int]

    @classmethod
    def from_rows(cls, rows: dict[int, bytes]) -> "Glyphs":
        """Build from glyph rows; a glyph drawn like a native character uses it.

        Args:
            rows: 8 pixel rows by code point.

        Returns:
            Glyphs.
        """
        native = dict(NATIVE_BYTES)
        native_by_rows = {
            rows[ord(char)]: byte
            for char, byte in NATIVE_BYTES.items()
            if ord(char) in rows
        }
        bitmaps = {}
        for code, bitmap in rows.items():
            if (char := chr(code)) in NATIVE_BYTES:
                continue
            if (byte := native_by_rows.get(bitmap)) is None:
                bitmaps[char] = bitmap
            else:
                native[char] = byte
        return cls(bitmaps=bitmaps, native=native)

    def _is_plain(self, char: str) -> bool:
        """Tell if a character stays native in a transliterated word.

        Args:
            char: Character.

        Returns:
            True for a native character but a letter of a script not in
            `PLAIN_SCRIPTS`.
        """
        return char in self.native and (
            char.isascii()
            or not char.isalpha()
            or any(script in unicode_name(char, "") for script in PLAIN_SCRIPTS)
        )

    def fallback(self, char: str) -> str:
        """Get the nearest native text of a character.

        Args:
            char: Character not shown natively.

        Returns:
            Native characters: the NFKD base characters if all plain (see
            `_is_plain`), else the `unidecode` transliteration filtered to native
            characters. May be empty.
        """
        base = "".join(part for part in normalize("NFKD", char) if not combining(part))
        if base and all(map(self._is_plain, base)):
            return base
        text = unidecode(char).translate(FALLBACK_REPLACEMENTS)
        return "".join(part for part in text if part in NATIVE_BYTES)

    def fallback_cost(self, char: str) -> int:
        """Get the readability cost of showing a character with its fallback.

        Args:
            char: Character not shown natively.

        Returns:
            `CHEAP_FALLBACK_COST` for a one-cell fallback of a Latin letter or a
            non-letter, else `EXPENSIVE_FALLBACK_COST`.
        """
        similar = category(char)[0] != "L" or _is_latin(char)
        if similar and len(self.fallback(char).strip()) == 1:
            return CHEAP_FALLBACK_COST
        return EXPENSIVE_FALLBACK_COST

    def transliterate(self, word: str) -> str:
        """Get the native text of a word.

        Native letters of other scripts than Latin are transliterated too (Έλληνας to
        Ellenas, not Ellenαs). Expansions of symbols and of characters of scripts
        without spaces (€ to EUR, 東 to Dong) are kept apart from adjacent letters and
        digits.

        Args:
            word: Word, without spaces.

        Returns:
            Native characters, spaces collapsed.
        """
        text = ""
        separate_previous = False
        for char in word:
            if self._is_plain(char):
                piece, separate = char, False
            else:
                piece = self.fallback(char)
                separate = len(piece.strip()) > 1 and (
                    category(char)[0] not in "LMN" or piece.endswith(" ")
                )
            if (
                (separate or separate_previous)
                and text[-1:].isalnum()
                and piece[:1].isalnum()
            ):
                text += " "
            text += piece
            separate_previous = separate if piece else separate_previous
        return " ".join(text.split())

    def encode_row(self, row: str, allowed: Set[str]) -> list[Cell]:
        """Encode a row to one cell per display column.

        A word is shown with custom characters only if all its characters are
        native or allowed, else it is transliterated as a whole.

        Args:
            row: Row text.
            allowed: Characters that may use a custom character (in `bitmaps`).

        Returns:
            Cells.
        """
        cells: list[Cell] = []
        for word in row.split(" "):
            if all(char in self.native or char in allowed for char in word):
                cells.extend(
                    self.native[char] if char in self.native else self.bitmaps[char]
                    for char in word
                )
            else:
                cells.extend(self.native[char] for char in self.transliterate(word))
            cells.append(0x20)
        return cells[:-1]


@dataclass(frozen=True, slots=True)
class Frame:
    """One write to the display."""

    #: Custom characters the write defines: rows by slot.
    definitions: dict[int, bytes]
    #: Bytes to write, the definitions included.
    data: bytes


def _windows(cell_rows: list[list[Cell]], columns: int) -> list[list[list[Cell]]]:
    """Get the visible cells of each row at each scroll step.

    Args:
        cell_rows: Cells by row.
        columns: Number of display columns.

    Returns:
        Visible cells by row, by step. Rows stop scrolling once their end is shown.
    """
    steps = max(0, max(map(len, cell_rows)) - columns)
    return [
        [row[min(step, max(0, len(row) - columns)) :][:columns] for row in cell_rows]
        for step in range(steps + 1)
    ]


def _eviction_rank(
    glyph: bytes | None, uses: dict[bytes, list[int]], step: int
) -> tuple[int, int]:
    """Rank a slot for redefinition: empty first, then unused, then used latest.

    Args:
        glyph: Rows the slot holds.
        uses: Steps where each glyph is visible.
        step: Current step.

    Returns:
        Sort key, lowest first.
    """
    if glyph is None:
        return 0, 0
    steps = uses.get(glyph, [])
    index = bisect_right(steps, step)
    return (2, -steps[index]) if index < len(steps) else (1, 0)


def _schedule(
    visible: list[list[bytes]], loaded: Sequence[bytes | None]
) -> list[dict[int, bytes]]:
    """Assign slots to the custom characters visible at each step.

    A slot is redefined only when its character is visible neither before nor after
    the step, so no shown cell changes shape. Slots needed again latest are reused
    first.

    Args:
        visible: Custom character rows visible at each step, in display order.
        loaded: Rows each slot holds before the screen.

    Returns:
        Slots to define at each step, rows by slot.

    Raises:
        SlotConflict: Not enough slots at a step.
    """
    uses: dict[bytes, list[int]] = defaultdict(list)
    for step, glyphs in enumerate(visible):
        for glyph in glyphs:
            uses[glyph].append(step)
    slots = list(loaded)
    schedule = []
    previous: list[bytes] = []
    for step, current in enumerate(visible):
        missing = [glyph for glyph in current if glyph not in slots]
        free = [
            slot
            for slot, glyph in enumerate(slots)
            if glyph not in previous and glyph not in current
        ]
        if len(missing) > len(free):
            raise SlotConflict({*previous, *current})
        free.sort(key=lambda slot: _eviction_rank(slots[slot], uses, step))
        definitions = dict(zip(free, missing, strict=False))
        for slot, glyph in definitions.items():
            slots[slot] = glyph
        schedule.append(definitions)
        previous = current
    return schedule


def _render(
    cell_rows: list[list[Cell]],
    windows: list[list[list[Cell]]],
    schedule: list[dict[int, bytes]],
    loaded: Sequence[bytes | None],
    columns: int,
) -> list[Frame]:
    """Build the writes of a screen.

    Args:
        cell_rows: Cells by row.
        windows: Visible cells by row, by step.
        schedule: Slots to define at each step.
        loaded: Rows each slot holds before the screen.
        columns: Number of display columns.

    Returns:
        Frames: the first clears the screen, defines its custom characters then
        shows the centred rows; the next ones rewrite the rows still scrolling.
    """
    slots = list(loaded)
    frames = []
    for step, (window, definitions) in enumerate(zip(windows, schedule, strict=True)):
        for slot, glyph in definitions.items():
            slots[slot] = glyph
        slot_of = {glyph: slot for slot, glyph in enumerate(slots)}
        parts = [CLEAR_SCREEN] if step == 0 else []
        parts.extend(define_custom_character(*item) for item in definitions.items())
        for row, (cells, shown) in enumerate(zip(cell_rows, window, strict=True)):
            text = bytes(slot_of[c] if isinstance(c, bytes) else c for c in shown)
            if step == 0:
                col = max(columns // 2 - len(cells) // 2, 1)
                if col > 1 or row or definitions:
                    parts.extend((SET_CURSOR_POSITION, bytes((col, row + 1))))
                parts.append(text)
            elif len(cells) - columns >= step:
                parts.extend((SET_CURSOR_POSITION, bytes((1, row + 1)), text))
        frames.append(Frame(definitions, b"".join(parts)))
    return frames


def plan_screen(
    rows: list[str],
    glyphs: Glyphs,
    loaded: Sequence[bytes | None],
    columns: int,
) -> list[Frame]:
    """Plan the writes showing a screen, scrolling rows longer than the display.

    Characters needing a custom character get one while visible. When slots run out,
    the character with the lowest fallback cost times frequency (latest first on
    ties) is transliterated, with the words containing it, until slots suffice.

    Args:
        rows: Text by row, NFC normalized.
        glyphs: Glyphs.
        loaded: Rows each slot holds before the screen.
        columns: Number of display columns.

    Returns:
        Frames, one per scroll step.
    """
    counts = Counter(char for row in rows for char in row if char in glyphs.bitmaps)
    first = {char: index for index, char in enumerate(counts)}
    allowed = set(counts)
    while True:
        cell_rows = [glyphs.encode_row(row, allowed) for row in rows]
        windows = _windows(cell_rows, columns)
        visible = [
            list(dict.fromkeys(c for r in w for c in r if isinstance(c, bytes)))
            for w in windows
        ]
        try:
            schedule = _schedule(visible, loaded)
        except SlotConflict as conflict:
            allowed.remove(
                min(
                    (c for c in allowed if glyphs.bitmaps[c] in conflict.glyphs),
                    key=lambda c: (glyphs.fallback_cost(c) * counts[c], -first[c]),
                )
            )
            continue
        return _render(cell_rows, windows, schedule, loaded, columns)


class KanjiReader:
    """Japanese readings of kanji, in katakana, from kakasi.

    Args:
        command: kakasi command, None to keep kanji unchanged.
    """

    def __init__(self, command: Sequence[str] | None) -> None:
        self._command = command
        self._warned = False
        self.read = lru_cache(maxsize=KAKASI_CACHE_SIZE)(self._read)

    def _read(self, text: str) -> str:
        """Replace the Japanese runs holding kanji by their reading.

        Only these runs are given to kakasi, which garbles other characters. A run
        keeps its text if its reading, once sanitized, is not only Japanese
        characters or is too long; the whole text is kept if kakasi fails.

        Args:
            text: NFC text.

        Returns:
            Text.
        """
        runs = [run for run in JAPANESE_RUN.finditer(text) if KANJI.search(run[0])]
        if not runs or self._command is None:
            return text
        readings = self._kakasi("\n".join(run[0] for run in runs))
        if readings is None or len(readings) != len(runs):
            return text
        parts = []
        end = 0
        for match, reading in zip(runs, map(sanitize, readings), strict=True):
            valid = JAPANESE_READING.fullmatch(reading) and (
                len(reading) <= KAKASI_MAX_EXPANSION * len(match[0])
            )
            parts.extend((text[end : match.start()], reading if valid else match[0]))
            end = match.end()
        return "".join(parts) + text[end:]

    def _kakasi(self, text: str) -> list[str] | None:
        """Run kakasi, warning once on stderr on failure.

        Args:
            text: Lines to read.

        Returns:
            Output lines, None on failure. A missing kakasi is not run again.
        """
        try:
            # Fixed argument list without shell, the text only goes to stdin
            result = run(  # noqa: S603
                self._command,
                input=text,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=KAKASI_TIMEOUT,
                check=True,
            )
        except (OSError, SubprocessError, UnicodeError) as error:
            if isinstance(error, FileNotFoundError):
                self._command = None
            if not self._warned:
                self._warned = True
                print(f"Kanji shown without reading: {error}", file=sys.stderr)
            return None
        return result.stdout.removesuffix("\n").split("\n")


def load_glyphs(path: Path = GLYPHS_PATH) -> Glyphs:
    """Load the glyph file, warning on stderr and using none if it is unusable.

    Args:
        path: Glyph file.

    Returns:
        Glyphs.
    """
    try:
        with path.open(encoding="ascii") as file:
            return Glyphs.from_rows(parse_glyphs(file))
    except (OSError, ValueError) as error:
        print(f"Custom characters disabled, transliterating: {error}", file=sys.stderr)
        return Glyphs.from_rows({})


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
        glyphs: Glyphs of the custom characters, default to the `GLYPHS_PATH` file.
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
        glyphs: Glyphs | None = None,
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
        self._brightness = brightness
        self._glyphs = load_glyphs() if glyphs is None else glyphs
        self._kanji = KanjiReader(KAKASI_COMMAND)
        # Rows of the custom character each slot holds on the device
        self._slots: list[bytes | None] = [None] * CUSTOM_SLOTS

        # Only the latest queued text matters: it replaces the pending one
        self._pending: str | None = None
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
                self._print(f".{(i - 2) * ' '}.", scroll_wait=0.025, vanish_time=0.025)
            self._print("|", vanish_time=0.025, scroll_wait=0.025)
            self._print("*", vanish_time=0.15, scroll_wait=0.10)

    def __enter__(self) -> "Display":
        self.start()
        return self

    def __exit__(self, *_: object) -> None:
        with self._condition:
            self._exit = True
            self._condition.notify_all()
        self.join()
        self._print("")
        self._device.close()

    def _write(self, data: bytes) -> int:
        """Write on device, reconnecting to it on failure.

        After a reconnection, the setup and the custom characters are sent again
        before the data. The saved brightness is set without saving it again.

        Args:
            data: Data.

        Returns:
            Written data size.
        """
        restore = b""
        while True:
            try:
                return self._device.write(restore + data) - len(restore)
            except SerialException:
                self._device = self._get_device()
                restore = b"".join(
                    (
                        SET_BRIGHTNESS,
                        bytes((self._brightness,)),
                        BRIGHTNESS_ON,
                        b"\x00",
                        AUTO_SCROLL_OFF,
                        AUTO_LINE_WRAP_OFF,
                        *(
                            define_custom_character(slot, rows)
                            for slot, rows in enumerate(self._slots)
                            if rows is not None
                        ),
                    )
                )

    def queue_print(self, text: str) -> None:
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

    def _show(self, frame: Frame) -> None:
        """Write a frame, recording the custom characters it defines.

        Args:
            frame: Frame.
        """
        for slot, rows in frame.definitions.items():
            self._slots[slot] = rows
        self._write(frame.data)

    def _print(
        self,
        text: str,
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

        text = self._kanji.read(normalize("NFC", text))
        rows = to_display_forms(text).split("\n")[: self._rows]
        first, *steps = plan_screen(rows, self._glyphs, self._slots, self._columns)
        self._show(first)
        self._sleep(self._scroll_wait if scroll_wait is None else scroll_wait)

        if steps:
            period = 1 / self._scroll_speed
            for frame in steps:
                self._sleep(period)
                self._show(frame)
            self._sleep(period)

        vanish_time = self._vanish if vanish_time is None else vanish_time
        if vanish_time:
            self._sleep(vanish_time)
            self._write(CLEAR_SCREEN)

    def charset_test(self, page_seconds: float = CHARSET_TEST_PAGE_SECONDS) -> None:
        """Show the native character table then a custom character, page by page.

        Each row shows its first code in hexadecimal then 16 codes, from 0x10; 0xFE,
        the command prefix, is shown as a space. The last page defines `TEST_GLYPH`
        in slot 0 and shows codes 0x00 and 0x08. Prints on stdout what each page
        shows.

        Args:
            page_seconds: Seconds each page is shown.
        """
        pages = [(0x10,), *((start, start + 16) for start in range(0x20, 0x100, 32))]
        table = {byte: char for char, byte in NATIVE_BYTES.items()}
        total = len(pages) + 1
        for page, firsts in enumerate(pages, 1):
            data = [CLEAR_SCREEN]
            print(f"Page {page}/{total}:")
            for row, first in enumerate(firsts, 1):
                codes = range(first, first + 16)
                data.extend(
                    (
                        SET_CURSOR_POSITION,
                        bytes((1, row)),
                        f"{first:02X} ".encode(),
                        bytes(0x20 if code == 0xFE else code for code in codes),
                    )
                )
                expected = (
                    ": unknown"
                    if first < 0x20
                    else " (· not used natively): "
                    + "".join(table.get(code, "·") for code in codes)
                )
                print(
                    f"  row {row}: '{first:02X} ' then codes 0x{first:02X}-"
                    f"0x{first + 15:02X}, expected{expected}"
                )
            self._write(b"".join(data))
            self._sleep(page_seconds)
        self._slots[0] = TEST_GLYPH
        self._write(
            b"".join(
                (
                    CLEAR_SCREEN,
                    define_custom_character(0, TEST_GLYPH),
                    SET_CURSOR_POSITION,
                    b"\x01\x01",
                    b"00:\x00 08:\x08",
                    SET_CURSOR_POSITION,
                    b"\x01\x02",
                    b"FE 4E custom char",
                )
            )
        )
        print(
            f"Page {total}/{total}:\n"
            "  row 1: '00:' then custom character 0, '08:' then code 0x08; each\n"
            "         is a checkerboard if the custom character command works\n"
            "         (0x08 only if codes 0x08-0x0F repeat the 8 custom characters)\n"
            "  row 2: 'FE 4E custom char'"
        )
        self._sleep(page_seconds)

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


def sanitize(text: str) -> str:
    """Normalize a metadata text for display.

    Args:
        text: Text.

    Returns:
        NFC text, controls and separators as single spaces, format characters and
        lone combining marks removed, without leading or trailing spaces.
    """
    kept = []
    for char in normalize("NFC", text):
        if (kind := category(char)) in SPACE_CATEGORIES:
            kept.append(" ")
        elif kind not in REMOVED_CATEGORIES:
            kept.append(char)
    return " ".join("".join(kept).split())


def get_xesam_property(
    metadata: dict[str, Any], names: str | tuple[str, ...]
) -> str | None:
    """Get Xesam property value.

    Value text is sanitized before return.

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
            return str(value)
        return sanitize(value)
    return None


def get_display_text(metadata: dict[str, Any]) -> str:
    """Get the text to display for a track, one line by row of `ROW_INFO`.

    Args:
        metadata: MPRIS Metadata.

    Returns:
        Text, empty values and their separators are omitted.
    """
    return "\n".join(
        " | ".join(filter(None, (get_xesam_property(metadata, name) for name in row)))
        for row in ROW_INFO
    )


def main(argv: list[str] | None = None) -> None:
    """Show the track information of the first music player on the display.

    Args:
        argv: Command line arguments, default to `sys.argv`.
    """
    parser = ArgumentParser(description=main.__doc__.splitlines()[0])
    parser.add_argument(
        "--charset-test",
        action="store_true",
        help="show the display character table and a custom character, then exit",
    )
    if parser.parse_args(argv).charset_test:
        print("Getting display device...")
        with Display(brightness=1, startup_indicator=False) as display:
            display.charset_test()
        return

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
