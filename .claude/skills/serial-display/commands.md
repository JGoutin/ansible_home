# OK202-25 command reference

From the OK202-25 Technical Manual revision 1.1 (firmware 5.6 or later). Every command is `FE` followed by the command
byte and its parameters. "Saved" says when a setting is written to non-volatile memory: always, never, or only while
"remember" (`FE 93 1`) is on.

## Communication

| Command | Bytes | Parameters | Saved |
|---|---|---|---|
| Change baud rate | `FE 39 <speed>` | speed byte: 1200 = 83, 2400 = 41, 4800 = 207, 9600 = 103, 19200 = 51, 28800 = 34, 38400 = 25, 57600 = 16, 76800 = 12, 115200 = 8 (the last two need firmware 5.7) | always |
| Set a non-standard baud rate | `FE A4 <speed, 2 bytes>` | speed = 16 MHz / (8 × baud) − 1; baud 977-153800, actual baud within 3 % | always |
| Change I2C slave address | `FE 33 <address>` | even value, default 80 | always |
| Transmission protocol select | `FE A0 <protocol>` | 1 serial (RS232, RS422, TTL, USB), 0 I2C | remember |

## Text

| Command | Bytes | Parameters | Saved |
|---|---|---|---|
| Clear screen | `FE 58` | | never |
| Change the start-up screen | `FE 40 <80 bytes>` | text shown at power-up, custom characters as ids 0-7, wraps automatically | always |
| Auto scroll on / off | `FE 51` / `FE 52` | on: the screen shifts up at its end; off: text overwrites the top line. Default on | remember |
| Auto line wrap on / off | `FE 43` / `FE 44` | off: writing order skips one row when wrapping. Default on | remember |
| Set cursor position | `FE 47 <column> <row>` | 1-based | never |
| Go home | `FE 48` | cursor to the top left | never |
| Move cursor back / forward | `FE 4C` / `FE 4D` | obeys the wrap setting | never |
| Underline cursor on / off | `FE 4A` / `FE 4B` | | remember |
| Blinking cursor on / off | `FE 53` / `FE 54` | | remember |

## Special characters

| Command | Bytes | Parameters | Saved |
|---|---|---|---|
| Create a custom character | `FE 4E <id> <8 bytes>` | id 0-7; one byte per row from the top, 3 zero bits then 5 pixel bits, bit 4 leftmost; lost when a bank is loaded | remember |
| Save custom characters | `FE C1 <bank> <id> <8 bytes>` | bank 0 start-up characters, 1 horizontal bars, 2 vertical bars, 3 medium digits, 4 large digits; overwrites that bank | always |
| Load custom characters | `FE C0 <bank>` | loads a bank into the 8 ids | never |
| Save start-up screen custom characters | `FE C2 <id> <8 bytes>` | characters usable in the start-up screen | always |
| Initialize medium numbers | `FE 6D` | loads the medium digits bank | never |
| Place medium numbers | `FE 6F <row> <column> <digit>` | digit 2 rows high, 1 column wide | never |
| Initialize horizontal bar | `FE 68` | | never |
| Place horizontal bar graph | `FE 7C <column> <row> <direction> <length>` | direction 0 right, 1 left; length 0-100 pixels | never |
| Initialize narrow / wide vertical bar | `FE 73` / `FE 76` | 2 or 5 pixels wide | never |
| Place vertical bar | `FE 3D <column> <length>` | grows up from the bottom row; length 0-32 pixels | never |

## General purpose outputs

| Command | Bytes | Parameters | Saved |
|---|---|---|---|
| General purpose output on / off | `FE 57 <number>` / `FE 56 <number>` | on sources 5 V, off sinks to 0 V | never |
| Set start-up GPO state | `FE C3 <number> <state>` | state 1 on, 0 off | always |

## Dallas One-Wire (USB model header)

| Command | Bytes | Parameters | Saved |
|---|---|---|---|
| Search for a One-Wire device | `FE C8 02` | answers one 14-byte packet per device: preamble `9002`, 138 if another packet follows or 10 if last, type 49, error code, 8-byte address, CRC8 check | never |
| Dallas One-Wire transaction | `FE C8 01 <flags> <send bytes> <receive bytes> <data>` | flags: bit 0 reset bus first, bit 1 read CRC8, bit 3 add CRC8; errors 1 unknown command, 2 no devices, 3 fatal search error | never |

## Keypad

| Command | Bytes | Parameters | Saved |
|---|---|---|---|
| Auto transmit key presses on / off | `FE 41` / `FE 4F` | off keeps presses in a 10-key buffer to poll. Default on | remember |
| Poll key press | `FE 26` | answers the oldest unread key, MSB set if more keys wait, 0 if none | never |
| Clear key buffer | `FE 45` | | never |
| Set debounce time | `FE 55 <time>` | time × 6.554 ms, default 8 (about 52 ms) | remember |
| Set auto repeat mode | `FE 7E <mode>` | 1 hold (key down, then key up on release), 0 typematic (repeats 5 times a second after 1 s). Default typematic | remember |
| Auto repeat mode off | `FE 60` | | remember |
| Assign keypad codes | `FE D5 <25 key-down bytes> <25 key-up bytes>` | row 1 column 1 first; 255 leaves a key unchanged. Defaults: key down `A`-`Y`, key up `a`-`y` | always |

## Display functions

| Command | Bytes | Parameters | Saved |
|---|---|---|---|
| Brightness on | `FE 42 <minutes>` | 0 keeps it on | remember |
| Brightness off | `FE 46` | | remember |
| Set brightness | `FE 99 <0-255>` | default 255 | remember |
| Set and save brightness | `FE 98 <0-255>` | restored at each start | always |

## Data security

| Command | Bytes | Parameters | Saved |
|---|---|---|---|
| Set remember | `FE 93 <switch>` | 1 on, 0 off; default off | always |
| Set data lock | `FE CA F5 A0 <level>` | bits: 7 display (no new text), 6 commands, 4 settings, 3 baud rate and address; released at power-off | remember |
| Set and save data lock | `FE CB F5 A0 <level>` | same bits, kept across power cycles | always |

## Miscellaneous

| Command | Bytes | Parameters | Saved |
|---|---|---|---|
| Write customer data | `FE 34 <16 bytes>` | | always |
| Read customer data | `FE 35` | answers 16 bytes | never |
| Read version number | `FE 36` | answers 1 byte: major and minor version in hexadecimal | never |
| Read module type | `FE 37` | answers 1 byte: 17 OK202-25, 46 OK202-25-USB | never |
