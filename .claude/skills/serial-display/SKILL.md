---
name: serial-display
description: Load before changing or testing the musicplayer role's serial character display (musicplayer_serial_display.py, its glyphs or its device commands).
---

# Musicplayer serial display

`roles/musicplayer/files/musicplayer_serial_display.py` shows the playing track on a Matrix Orbital OK202-25-USB:
a 20x2 OLED character display on a USB serial port. The facts below come from the OK202-25 Technical Manual revision
1.1 (firmware 5.6 or later), a browser download from https://www.matrixorbital.com/ok-series-manuals. The full command
table is in `commands.md`.

## Device

- The script finds the port by its USB description `OK202-25-USB`. The USB model answers 46 to "read module type"
  (`FE 37`); the RS232/TTL/I2C model answers 17.
- Serial at 19200 baud by default; up to 115200 with "change baud rate" (`FE 39`). Powering up with a jumper
  on keypad pins R5 and C1 temporarily restores 19200 baud and brightness 255.
- Screen positions are 1-based: columns 1-20, rows 1-2.
- OLED pixels burn in: blank the display or change its content when idle.

## Sending data

- Every command starts with `0xFE`. Any other byte is printed at the cursor, which then advances.
- Never send `0xFE` or bytes below `0x20` as text: `0xFE` starts a command and `0x00`-`0x07` show custom characters.
  Sanitize text at the metadata boundary (control characters, newlines and tabs become spaces).
- The script turns auto scroll (`FE 52`) and line wrap (`FE 44`) off, clears the screen (`FE 58`) before each new
  text and places the cursor explicitly (`FE 47 <column> <row>`) before writing each row.
- After a USB reconnect the display has power-cycled: resend the setup commands and every custom character in use
  before retrying the data.

## Non-volatile memory

- Each write to non-volatile memory consumes one of at least 100,000 cycles.
- Always written: change start-up screen `FE 40`, set and save brightness `FE 98`, set remember `FE 93`, save custom
  characters `FE C1` and `FE C2`, start-up GPO state `FE C3`, baud rate, I2C address, keypad codes, customer data and
  set and save data lock.
- Written only while "remember" is on (`FE 93 1`, off by default and never sent by the script): create custom
  character `FE 4E`, set brightness `FE 99`, scroll, wrap, cursor and keypad settings.
- The script writes the start-up screen and the saved brightness once at each start, on purpose. Everything sent per
  track (clear, cursor, text, custom characters) is volatile.

## Built-in characters

The character table is "English Japanese", like the HD44780 ROM A00:

- `0x20`-`0x7D`: ASCII, except `0x5C` = ¥, `0x7E` = →, `0x7F` = ←. Backslash and tilde have no built-in character.
- `0xA1`-`0xDF`: half-width katakana in the order of U+FF61-U+FF9F (`A1` ｡ to `DD` ﾝ, `DE` ﾞ dakuten, `DF` ﾟ
  handakuten, also used for °). The script uses them natively: it shows hiragana and full-width katakana as half-width
  katakana, a voiced kana as two cells (ガ as ｶﾞ), and kana without a half-width form as the nearest one (ヶ as ｹ).
- `0xE0`-`0xFF`: `E0` α, `E1` ä, `E2` β, `E3` ε, `E4` μ, `E5` σ, `E6` ρ, `E8` √, `EC` ¢, `EE` ñ, `EF` ö, `F2` θ,
  `F3` ∞, `F4` Ω, `F5` ü, `F6` Σ, `F7` π, `FA` 千, `FB` 万, `FC` 円, `FD` ÷, `FF` full block. Other codes in this range
  are math symbols and kanji that the script does not map.
- `0x10`-`0x1F` and `0x80`-`0x9F` hold glyphs that are not legible in the manual: map them only after checking them on
  the device with the script's `--charset-test` option.

## Custom characters

- Create one with `FE 4E <id> <8 bytes>`: id 0-7, one byte per pixel row from the top, 5 low bits per row with bit 4
  the leftmost pixel and bit 0 the rightmost; a set bit is a lit pixel. All 8 rows are visible.
- Show it by sending its id (`0x00`-`0x07`). The table also lists `0x08`-`0x0F` as CG RAM; the script never uses them.
- Redefining an id changes every visible cell showing it at once: redefine only ids absent from the visible text.
- Defining 8 characters costs 88 bytes, about 46 ms at 19200 baud; a full 20x2 screen of text costs 40 bytes.
- The manual's example draws a degree sign with the rows `8 20 8 3 4 4 3 0`.

## Glyphs for characters without a built-in code

- Glyphs come from the public-domain X11 misc-fixed 5x8 font shipped by Fedora's `xorg-x11-fonts-misc` package.
  `tools/generate_display_glyphs.py` (stdlib PCF reader) writes them to
  `roles/musicplayer/files/musicplayer_serial_display_glyphs.txt`; its docstring gives the podman command that
  regenerates the file. The role deploys it as `/usr/local/share/musicplayer_serial_display/glyphs.txt`; without it,
  the script warns and only transliterates.
- A character whose 5x8 glyph is pixel-identical to a built-in character's glyph uses that built-in code (Cyrillic А
  shows as A), which saves slots.
- Slots are planned per visible 20-column window: a scroll step only needs the characters it shows, and a slot is
  redefined only when its character is in neither the old nor the new window.
- When more characters need slots than are free, the script drops the one with the lowest fallback cost times
  frequency: a fallback to one Latin letter or symbol (é→e) is cheap, an empty, longer or other-script fallback is
  expensive. A dropped character transliterates every word containing it; glyphs and transliteration never mix inside
  one word.
- Fallback order: the Unicode decomposition's base characters, then `unidecode` restricted to built-in characters.
  Expansions of symbols and other scripts get spaces around them so words stay apart ("5€" → "5 EUR").

## Testing

- Unit tests in `tests/python/` drive the script with a fake serial port and assert the exact bytes sent: run them
  with the collection's gates (`collection` skill).
- On the device, stop the music player service and run the script with `--charset-test`: it pages through the
  built-in codes with their hex values and shows a test custom character.
