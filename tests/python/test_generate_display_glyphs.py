"""Tests of the display glyph generator, with synthetic PCF fonts."""

import gzip
import struct

import pytest
from conftest import load_script, load_tool

generator = load_tool("generate_display_glyphs.py")
display_module = load_script("musicplayer/files/musicplayer_serial_display.py")

#: Synthetic glyphs: code point, (left, right, ascent, descent), rows MSB first.
GLYPHS = (
    (0x41, (0, 5, 7, 1), [0x00, 0x60, 0x90, 0x90, 0xF0, 0x90, 0x90, 0x00]),
    (0xE9, (1, 3, 3, 0), [0xC0, 0x40, 0x80]),
    (0x2588, (-1, 6, 9, 2), [0xFE] * 11),
    (0x01, (0, 5, 7, 1), [0xF8] * 8),
)
#: Expected cells of `GLYPHS`, control character excluded.
EXPECTED = {
    0x41: bytes((0x00, 0x0C, 0x12, 0x12, 0x1E, 0x12, 0x12, 0x00)),
    0xE9: bytes((0, 0, 0, 0, 0x0C, 0x04, 0x08, 0)),
    0x2588: bytes((0x1F,) * 8),
}
COPYRIGHT = "Public domain font.  Share and enjoy."


def build_pcf(
    msb_byte=True,
    msb_bit=True,
    pad_index=0,
    unit_index=0,
    compressed=True,
    registry="ISO10646",
):
    """Build a PCF font of `GLYPHS` with the given table formats."""
    order = ">" if msb_byte else "<"
    fmt = pad_index | (4 if msb_byte else 0) | (8 if msb_bit else 0) | unit_index << 4
    pad = 1 << pad_index

    def table(payload, extra=0):
        return struct.pack("<i", fmt | extra) + payload

    strings = b""
    props = []
    for name, value in (("COPYRIGHT", COPYRIGHT), ("CHARSET_REGISTRY", registry)):
        props.append((len(strings), len(strings) + len(name) + 1))
        strings += name.encode() + b"\0" + value.encode() + b"\0"
    properties = struct.pack(f"{order}i", len(props))
    properties += b"".join(struct.pack(f"{order}ibi", n, 1, v) for n, v in props)
    properties += b"\0" * (-len(props) % 4)
    properties += struct.pack(f"{order}i", len(strings)) + strings

    accelerators = bytes(8) + struct.pack(f"{order}3i", 7, 1, 0)

    if compressed:
        metrics = struct.pack(f"{order}h", len(GLYPHS)) + b"".join(
            bytes(v + 0x80 for v in (left, right, right - left, ascent, descent))
            for _, (left, right, ascent, descent), _ in GLYPHS
        )
    else:
        metrics = struct.pack(f"{order}i", len(GLYPHS)) + b"".join(
            struct.pack(f"{order}5hH", left, right, right - left, ascent, descent, 0)
            for _, (left, right, ascent, descent), _ in GLYPHS
        )

    data = b""
    offsets = []
    for _, _, rows in GLYPHS:
        offsets.append(len(data))
        for row in rows:
            byte = row if msb_bit else int(f"{row:08b}"[::-1], 2)
            data += bytes((byte,)) + bytes(pad - 1)
    unit = 1 << unit_index
    if msb_byte != msb_bit:
        data = b"".join(data[i : i + unit][::-1] for i in range(0, len(data), unit))
    sizes = [0, 0, 0, 0]
    sizes[pad_index] = len(data)
    bitmaps = struct.pack(f"{order}i", len(GLYPHS))
    bitmaps += struct.pack(f"{order}{len(GLYPHS)}i", *offsets)
    bitmaps += struct.pack(f"{order}4i", *sizes) + data

    indexes = [0xFFFF] * (0x26 * 256)
    for index, (code, _, _) in enumerate(GLYPHS):
        indexes[code] = index
    encodings = struct.pack(f"{order}5h", 0, 0xFF, 0, 0x25, 0)
    encodings += struct.pack(f"{order}{len(indexes)}H", *indexes)

    tables = (
        (generator.PCF_PROPERTIES, table(properties)),
        (generator.PCF_ACCELERATORS, table(accelerators)),
        (generator.PCF_METRICS, table(metrics, 0x100 if compressed else 0)),
        (generator.PCF_BITMAPS, table(bitmaps)),
        (generator.PCF_BDF_ENCODINGS, table(encodings)),
    )
    offset = 8 + 16 * len(tables)
    header = b"\x01fcp" + struct.pack("<i", len(tables))
    body = b""
    for kind, content in tables:
        header += struct.pack("<4i", kind, 0, len(content), offset + len(body))
        body += content
    return header + body


@pytest.mark.parametrize(
    "options",
    [
        {},
        {"pad_index": 2},
        {"msb_byte": False, "msb_bit": False, "compressed": False},
        {"msb_byte": False, "pad_index": 1},
        {"msb_byte": False, "pad_index": 2, "unit_index": 2},
    ],
)
def test_glyphs_are_placed_in_the_cell_and_clipped(options):
    font = generator.read_pcf(build_pcf(**options))
    assert font.properties["COPYRIGHT"] == COPYRIGHT
    assert generator.font_glyphs(font) == EXPECTED


def test_main_prints_a_glyph_file_the_display_reads(tmp_path, capsys):
    path = tmp_path / "5x8.pcf.gz"
    path.write_bytes(gzip.compress(build_pcf()))
    generator.main([str(path), "--source", "fonts-1.0"])
    content = capsys.readouterr().out
    header = content.splitlines()[0]
    assert header == (
        "# Glyphs from fonts-1.0 5x8.pcf.gz (). "
        "COPYRIGHT: Public domain font. Share and enjoy."
    )
    assert display_module.parse_glyphs(content.splitlines()) == EXPECTED


def test_glyph_file_format_round_trips():
    glyphs = {0x5C: bytes(range(8)), 0x1F600: bytes((0x1F,) * 8)}
    text = generator.format_glyphs("a\nheader", glyphs)
    assert text.startswith("# a header\n")
    assert display_module.parse_glyphs(text.splitlines()) == glyphs


def test_non_pcf_data_is_rejected():
    with pytest.raises(ValueError, match="Not a PCF font"):
        generator.read_pcf(b"STARTFONT 2.1\n")


def test_missing_table_is_rejected():
    data = bytearray(build_pcf())
    struct.pack_into("<i", data, 8, 0)  # Properties table type no longer known
    with pytest.raises(ValueError, match="missing"):
        generator.read_pcf(bytes(data))


def test_non_unicode_font_is_rejected():
    font = generator.read_pcf(build_pcf(registry="ISO8859"))
    with pytest.raises(ValueError, match="Unicode"):
        generator.font_glyphs(font)
