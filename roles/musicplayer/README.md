# Music Player Ansible Role

## Description

This role installs a music player in standalone mode.
By default, [Lollypop](https://gitlab.gnome.org/World/lollypop), but should work with 
the player of your choice (Audacious, Clementine, Strawberry, ...).

This is intended to turn a computer into a dedicated music player that can be used with 
a small touchscreen for view and control.

### Features

Configuration:
* Install the music player of your choice.
* Run as a standalone fullscreen application using Wayland and Sway.
* Use ALSA without dmix for high-quality sound output (from the
  `/etc/alsa/conf.d/99-zz-musicplayer.conf` drop-in).
* Configure `playerctl` to allow the use with multimedia keyboards and compatible 
  volume knobs.
* Ensure the ALSA device is unmuted on player start.
* Print track information on a serial alphanumeric display.

Security:
* Works with SELinux enforced.

#### About sound quality

With "Fedora minimal" as base OS, ALSA will be used by default by music players without
requiring to specify it.
This will result in a bit-perfect quality sound output.

#### Serial alphanumeric display

This feature plays track information (Artist, album, Title, Track number) on a serial
alphanumeric display.
Information is played when the track changes.

The utility is intended to work with the Matrix Orbital OK202-25-USB (an OLED USB 
alphanumeric display) and should work out of the box with other serial/USB
displays from the same provider or compatible.

Text is shown with the display character table where it has the character (ASCII,
¥, £, °, ·, ä, ñ, ö, ü, some Greek and math symbols, half-width katakana and the kanji 千,
万 and 円). Japanese kana are shown with the built-in katakana and need no custom
character: hiragana and full-width katakana become half-width katakana, a voiced
kana takes two cells (`ガ` to `ｶﾞ`), and full-width Latin letters and digits become
ASCII. Other kanji are replaced by their Japanese reading in katakana, from
[KAKASI](http://kakasi.namazu.org/) (`東京` to `ﾄｳｷｮｳ`); a kanji KAKASI cannot read
(such as simplified Chinese) follows the rules below, and the kana around it stay
as they are. Any other character with a glyph in the glyph file is shown as one of the 8 custom characters the display allows at
a time, defined for each screen and redefined while a long row scrolls. When there
are not enough custom characters, the characters that transliterate worst (other
scripts, symbols) keep theirs first, and a word that cannot be shown whole with
custom characters is transliterated as a whole with
[Unidecode](https://pypi.org/project/Unidecode/) (`é` to `e`, `ß` to `ss`, `€` to
`EUR`).

To check the display character table and the custom character command on the
device, stop the music player session, then run:

```bash
musicplayer_serial_display --charset-test
```

It shows 9 pages for 4 seconds each, starting with the codes 0x10-0x1F whose
characters are unknown, and prints on the terminal what each page
should show.

##### Glyph file

The role deploys `files/musicplayer_serial_display_glyphs.txt` to
`/usr/local/share/musicplayer_serial_display/glyphs.txt`. It holds the 5x8 pixel
glyphs of the X11 "misc-fixed" `5x8` font (`/usr/share/X11/fonts/misc/5x8.pcf.gz`)
from the Fedora package `xorg-x11-fonts-misc`; its first line records the package
version and the font COPYRIGHT property: "Public domain font. Share and enjoy."

To regenerate it, run from the repository root (Podman, no mount):

```bash
podman run --rm -i registry.fedoraproject.org/fedora:45 sh -c '
  dnf -q -y install xorg-x11-fonts-misc python3 </dev/null >/dev/null &&
  python3 - --source "$(rpm -q xorg-x11-fonts-misc)" \
    /usr/share/X11/fonts/misc/5x8.pcf.gz' \
  < tools/generate_display_glyphs.py \
  > roles/musicplayer/files/musicplayer_serial_display_glyphs.txt
```

The file format is described in `tools/generate_display_glyphs.py`.

## Dependencies

### Packages

The serial display utility installs these Fedora packages: `python3-pyserial`,
`python3-gobject`, `python3-unidecode`, and for kanji readings `kakasi`,
`kakasi-dict` (its dictionary) and `glibc-gconv-extra` (the character set
converters KAKASI needs for UTF-8 text). Without them, the utility transliterates
kanji with Unidecode (Chinese readings).

### OS recommendation

* "Fedora minimal" is recommended. 

### Roles

* common

## Variables

### Optional

| Name                               | Default Value                    | Description                                                                                                                                                 |
|------------------------------------|----------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `musicplayer_alsa_mixer`           | `Master`                         | ALSA mixer used with the music player. Ensures it is unmuted on start and allows toggling mute state with player controls.                                  |
| `musicplayer_alsa_only`            | true                             | If `true`, ensure the sound is managed only with ALSA and remove Pipewire. The `alsamixer` shell command can be used to configure sound output if required. |
| `musicplayer_command`              | `/usr/bin/<musicplayer_package>` | Command to use to run the music player. By default, run the command based on the `musicplayer_package` name.                                                |
| `musicplayer_disable_hdmi_sound`   | false                            | If `true`, disable the HDMI sound. Useful if the HDMI sound conflict with another sound card and HDMI sound is never used.                                  |
| `musicplayer_gtk_theme`            | `Adwaita:dark`                   | Configure GTK based applications theme.                                                                                                                     |
| `musicplayer_mute_ctrl_play_pause` | false                            | If `true`, bind the "mute" keystoke to the play/pause action instead of the mute action.                                                                    |
| `musicplayer_package`              | `lollypop`                       | Name of the music player Fedora package.                                                                                                                    |
| `musicplayer_serial_display`       | false                            | If `true`, install an utility that print track information on the serial alphanumeric display; if `false`, the utility is removed.                                                              |
| `musicplayer_volume_ctrl_method`   | `alsa`                           | Volume control method to use. Possible values are `alsa` to use the ALSA mixer or `playerctl` to use the music player's volume control.                     |
| `musicplayer_volume_ctrl_percent`  | 5                                | Amount of volume in percent to decrease/increase with the volume control.                                                                                   |

It is also recommended to look at the [**common**](../common/README.md) role variables
to customize the server OS (SSH, NTP, Firewall, and more).

## Example Playbook

```yaml
---
- hosts: all
  become: true
  force_handlers: true  # See "jgoutin.home.common" documentation
  collections:
    - jgoutin.home
  roles:
    - common
    - musicplayer
```
