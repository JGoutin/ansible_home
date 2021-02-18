# Music player Ansible Role

![Ansible Role: "jgoutin.home.musicplayer"](https://github.com/JGoutin/ansible_home/workflows/Ansible%20Role:%20%22jgoutin.home.musicplayer%22/badge.svg)

## Description

This role installs a music player in standalone mode.
By default, [Lollypop](https://gitlab.gnome.org/World/lollypop), but should work with 
the player of your choice (Audacious, Clementine, Strawberry, ...).

This is intended to turn a computer into a dedicated music player that can be used with 
a small touchscreen for view and control.

### Features

Configuration:
* Installs the music player of your choice.
* Runs as a standalone fullscreen application using Wayland and Sway.
* Uses Alsa for high quality sound output.
* Configures `playerctl` to allow the use with multimedia keyboards and compatible 
  volume knobs.
* Ensures Alsa device is unmuted on player start.
* Prints track information on a serial alphanumeric display.

Security:
* Works with SElinux enforced.

#### About sound quality

With "Fedora minimal" as base OS, Pulseaudio is not installed, Alsa will be used by 
default by music players even if not providing an output selection option.
This will result in a bit-perfect quality sound output.

#### Serial alphanumeric display

This feature play track information (Artist, album, Title, Track number) on a serial
alphanumeric display. Information are played when track change.

The utility is intended to work with the Matrix Orbital OK202-25-USB (an OLED USB 
alphanumeric display) and should work out of the box with other serial/USB
displays from the same provider or compatible.

## Dependencies

### OS recommendation

* "Fedora minimal" is recommended. 

### Roles

* common

## Variables

### Optional

| Name           | Default Value | Description                        |
| -------------- | ------------- | -----------------------------------|
| `musicplayer_alsa_mixer` | `Master` | Alsa mixer used with the music player. Allow to ensure it is unmuted on start and allow to toggle mute state with player control.
| `musicplayer_command` | `/usr/bin/<musicplayer_package>` | Command to use to run the music player. By default, run the command based on the `musicplayer_package` name.
| `musicplayer_mute_ctrl_play_pause` | false | If `true`, bind the "mute" keystoke to the play/pause action instead of the mute action. 
| `musicplayer_package` | `lollypop` | Name of the music player Fedora package.
| `musicplayer_serial_display` | false | If `true`, install an utility that print track information on the serial alphanumeric display.
| `musicplayer_volume_ctrl_method` | `alsa` | Name of the music player Fedora package. Possible values are `alsa` to use Alsa mixer or `playerctl` to use music player volume control.
| `musicplayer_volume_ctrl_percent` | 5 | Amount of volume in percent to decrease/increase with the volume control.

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
