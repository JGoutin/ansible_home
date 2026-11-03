#! /usr/bin/env python3
r"""Generate the serial display custom character glyphs from an X11 PCF bitmap font.

Writes on stdout the glyph file read by `musicplayer_serial_display`: a header line
starting with `#` (source package, font name and the font COPYRIGHT and NOTICE
properties), then one line per code point: the code point in hexadecimal, a space and
the 8 pixel rows of the 5x8 cell as 16 hexadecimal digits (one byte per row, top to
bottom, low 5 bits used, bit 4 is the leftmost column).

Each glyph is placed in the cell by the font metrics: its baseline is at the font
ascent (from the accelerators table) rows from the top of the cell, its origin at the
left of the cell; pixels outside the 5x8 cell are clipped.

Regenerate the committed file from the Fedora signed package (no mount, the script is
piped in), from the repository root:

    podman run --rm -i registry.fedoraproject.org/fedora:45 sh -c '
      dnf -q -y install xorg-x11-fonts-misc python3 </dev/null >/dev/null &&
      python3 - --source "$(rpm -q xorg-x11-fonts-misc)" \
        /usr/share/X11/fonts/misc/5x8.pcf.gz' \
      < tools/generate_display_glyphs.py \
      > roles/musicplayer/files/musicplayer_serial_display_glyphs.txt

PCF format references: libXfont2 `src/bitmap/pcfread.c` and `include/X11/fonts/pcf.h`
(the reference reader), and FontForge's "The X11 PCF bitmap font file format"
(`pcf-format.html`). Layout used here:

- File header: magic `\x01fcp`, table count (int32 little-endian), then per table:
  type, format, size and offset (4 x int32 little-endian).
- Each table starts with its format (int32 little-endian). Format bits: 0-1 glyph row
  padding (1 << n bytes), 2 most significant byte first, 3 most significant bit
  first, 4-5 scan unit (1 << n bytes); `0x100` in the metrics table means
  compressed metrics. Integers after the format use the table byte order.
- Properties: count, then per property name offset (int32), is-string flag (int8)
  and value (int32), padding to 4 bytes, string pool size (int32) and the
  NUL-terminated string pool; string values are pool offsets.
- Accelerators (BDF accelerators preferred, same layout): 8 x uint8 flags and
  padding, then font ascent and descent (int32 each), then other bounds.
- Metrics: compressed: count (int16), 5 x uint8 minus 0x80 per glyph; otherwise count
  (int32), 6 x int16 per glyph: left and right side bearings, width, ascent, descent,
  attributes.
- Bitmaps: glyph count (int32), glyph offsets (int32 each), 4 bitmap sizes (int32 per
  padding), bitmap data. A glyph has `ascent + descent` rows of
  `right - left bearing` pixels.
- BDF encodings: min and max byte 2, min and max byte 1, default character (int16
  each), then one glyph index (uint16, 0xFFFF for none) per code
  `byte1 * 256 + byte2`.
"""

import gzip
import struct
from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path

#: PCF table types.
PCF_PROPERTIES = 1 << 0
PCF_ACCELERATORS = 1 << 1
PCF_METRICS = 1 << 2
PCF_BITMAPS = 1 << 3
PCF_BDF_ENCODINGS = 1 << 5
PCF_BDF_ACCELERATORS = 1 << 8

#: PCF format bit: compressed metrics.
PCF_COMPRESSED_METRICS = 0x100

#: Display custom character cell size in pixels.
CELL_COLUMNS = 5
CELL_ROWS = 8

#: Code points of control characters, never displayed.
CONTROL_CODES = frozenset((*range(0x20), *range(0x7F, 0xA0)))


@dataclass(frozen=True, slots=True)
class Metric:
    """Glyph metrics, in pixels relative to the origin on the baseline."""

    left: int
    right: int
    ascent: int
    descent: int


@dataclass(frozen=True, slots=True)
class Font:
    """Content of a PCF font used to build the glyphs."""

    properties: dict[str, int | str]
    ascent: int
    metrics: list[Metric]
    bitmaps: list[bytes]
    encodings: dict[int, int]


class Table:
    """Reader of one PCF table, in the table byte order.

    Args:
        data: Font file content.
        offset: Table offset in the file.
    """

    def __init__(self, data: bytes, offset: int) -> None:
        self.data = data
        (self.format,) = struct.unpack_from("<i", data, offset)
        self.order = ">" if self.format & 4 else "<"
        self.offset = offset + 4

    def read(self, codes: str) -> tuple[int, ...]:
        """Read values and move after them.

        Args:
            codes: `struct` format codes, without byte order.

        Returns:
            Values.
        """
        layout = self.order + codes
        values = struct.unpack_from(layout, self.data, self.offset)
        self.offset += struct.calcsize(layout)
        return values

    def bytes(self, size: int, offset: int | None = None) -> bytes:
        """Read raw bytes.

        Args:
            size: Number of bytes.
            offset: Absolute offset, default to the current one (then move after).

        Returns:
            Bytes.
        """
        if offset is None:
            offset, self.offset = self.offset, self.offset + size
        return self.data[offset : offset + size]


def _tables(data: bytes) -> dict[int, Table]:
    """Find the PCF tables.

    Args:
        data: Font file content.

    Returns:
        Table reader by table type.

    Raises:
        ValueError: Not a PCF font.
    """
    if data[:4] != b"\x01fcp":
        raise ValueError("Not a PCF font")
    (count,) = struct.unpack_from("<i", data, 4)
    entries = (struct.unpack_from("<4i", data, 8 + 16 * i) for i in range(count))
    return {kind: Table(data, offset) for kind, _, _, offset in entries}


def _properties(table: Table) -> dict[str, int | str]:
    """Read the properties table.

    Args:
        table: Properties table.

    Returns:
        Property values by name.
    """
    (count,) = table.read("i")
    entries = [table.read("ibi") for _ in range(count)]
    table.offset += -count % 4
    (size,) = table.read("i")
    pool = table.bytes(size)

    def string(offset: int) -> str:
        return pool[offset : pool.index(b"\0", offset)].decode("latin-1")

    return {
        string(name): string(value) if is_string else value
        for name, is_string, value in entries
    }


def _ascent(table: Table) -> int:
    """Read the font ascent from an accelerators table.

    Args:
        table: Accelerators or BDF accelerators table.

    Returns:
        Font ascent in pixels.
    """
    return table.read("8Bi")[8]


def _metrics(table: Table) -> list[Metric]:
    """Read the metrics table.

    Args:
        table: Metrics table.

    Returns:
        Metrics by glyph index.
    """
    if table.format & PCF_COMPRESSED_METRICS:
        (count,) = table.read("h")
        rows = ([value - 0x80 for value in table.read("5B")] for _ in range(count))
    else:
        (count,) = table.read("i")
        rows = (list(table.read("5hH")) for _ in range(count))
    return [
        Metric(left=left, right=right, ascent=ascent, descent=descent)
        for left, right, _, ascent, descent, *_ in rows
    ]


def _normalize_bitmap(bitmap: bytes, fmt: int) -> bytes:
    """Convert a bitmap to most significant bit and byte first.

    Args:
        bitmap: Bitmap data.
        fmt: Bitmaps table format.

    Returns:
        Bitmap data with the leftmost pixel in the highest bit of the first byte.
    """
    msb_bit = bool(fmt & 8)
    if not msb_bit:
        bitmap = bytes(int(f"{byte:08b}"[::-1], 2) for byte in bitmap)
    unit = 1 << ((fmt >> 4) & 3)
    if bool(fmt & 4) != msb_bit and unit > 1:
        bitmap = b"".join(
            bitmap[i : i + unit][::-1] for i in range(0, len(bitmap), unit)
        )
    return bitmap


def _bitmaps(table: Table, metrics: list[Metric]) -> list[bytes]:
    """Read the bitmaps table.

    Args:
        table: Bitmaps table.
        metrics: Metrics by glyph index.

    Returns:
        Bitmap by glyph index, rows padded as the table format says, most significant
        bit and byte first.

    Raises:
        ValueError: Glyph count differs from the metrics.
    """
    (count,) = table.read("i")
    if count != len(metrics):
        raise ValueError("Bitmaps and metrics glyph counts differ")
    offsets = table.read(f"{count}i")
    sizes = table.read("4i")
    data = _normalize_bitmap(table.bytes(sizes[table.format & 3]), table.format)
    pad = 1 << (table.format & 3)
    bitmaps = []
    for offset, metric in zip(offsets, metrics, strict=True):
        stride = -(-(metric.right - metric.left) // (8 * pad)) * pad
        size = stride * (metric.ascent + metric.descent)
        bitmaps.append(data[offset : offset + size])
    return bitmaps


def _encodings(table: Table) -> dict[int, int]:
    """Read the BDF encodings table.

    Args:
        table: BDF encodings table.

    Returns:
        Glyph index by code.
    """
    min_byte2, max_byte2, min_byte1, max_byte1, _ = table.read("5h")
    columns = max_byte2 - min_byte2 + 1
    count = columns * (max_byte1 - min_byte1 + 1)
    return {
        (min_byte1 + i // columns) * 256 + min_byte2 + i % columns: index
        for i, index in enumerate(table.read(f"{count}H"))
        if index != 0xFFFF
    }


def read_pcf(data: bytes) -> Font:
    """Read a PCF font.

    Args:
        data: Font file content (uncompressed).

    Returns:
        Font.

    Raises:
        ValueError: Not a PCF font, or a required table is missing.
    """
    tables = _tables(data)
    try:
        metrics = _metrics(tables[PCF_METRICS])
        return Font(
            properties=_properties(tables[PCF_PROPERTIES]),
            ascent=_ascent(
                tables.get(PCF_BDF_ACCELERATORS) or tables[PCF_ACCELERATORS]
            ),
            metrics=metrics,
            bitmaps=_bitmaps(tables[PCF_BITMAPS], metrics),
            encodings=_encodings(tables[PCF_BDF_ENCODINGS]),
        )
    except KeyError as error:
        raise ValueError(f"PCF table {error} missing") from error


def cell_rows(font: Font, index: int) -> bytes:
    """Draw a glyph in the display cell.

    Args:
        font: Font.
        index: Glyph index.

    Returns:
        8 rows, top to bottom, low 5 bits used, bit 4 is the leftmost column.
    """
    metric = font.metrics[index]
    bitmap = font.bitmaps[index]
    width = metric.right - metric.left
    height = metric.ascent + metric.descent
    stride = len(bitmap) // height if height else 0
    top = font.ascent - metric.ascent
    rows = bytearray(CELL_ROWS)
    for y in range(max(0, -top), min(height, CELL_ROWS - top)):
        for x in range(width):
            column = metric.left + x
            if 0 <= column < CELL_COLUMNS and bitmap[y * stride + x // 8] & (
                0x80 >> (x % 8)
            ):
                rows[top + y] |= 1 << (CELL_COLUMNS - 1 - column)
    return bytes(rows)


def font_glyphs(font: Font) -> dict[int, bytes]:
    """Draw every encoded character of a Unicode font, except control characters.

    Args:
        font: Font, with `CHARSET_REGISTRY` "ISO10646".

    Returns:
        Cell rows by code point.

    Raises:
        ValueError: Not a Unicode font.
    """
    if font.properties.get("CHARSET_REGISTRY") != "ISO10646":
        raise ValueError("Not a Unicode (ISO10646) font")
    return {
        code: cell_rows(font, index)
        for code, index in sorted(font.encodings.items())
        if code not in CONTROL_CODES
    }


def format_glyphs(header: str, glyphs: dict[int, bytes]) -> str:
    """Format the glyph file.

    Args:
        header: Header text, on one line.
        glyphs: Cell rows by code point.

    Returns:
        File content.
    """
    lines = [f"# {' '.join(header.split())}"]
    lines.extend(f"{code:04X} {rows.hex().upper()}" for code, rows in glyphs.items())
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> None:
    """Print the glyph file of a font.

    Args:
        argv: Command line arguments, default to `sys.argv`.
    """
    parser = ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("font", type=Path, help="PCF font, optionally gzipped")
    parser.add_argument("--source", required=True, help="Font package name-version")
    args = parser.parse_args(argv)
    data = args.font.read_bytes()
    font = read_pcf(gzip.decompress(data) if data[:2] == b"\x1f\x8b" else data)
    props = font.properties
    header = " ".join(
        (
            f"Glyphs from {args.source} {args.font.name} ({props.get('FONT', '')}).",
            *(
                f"{name}: {props[name]}"
                for name in ("COPYRIGHT", "NOTICE")
                if name in props
            ),
        )
    )
    print(format_glyphs(header, font_glyphs(font)), end="")


if __name__ == "__main__":
    main()
