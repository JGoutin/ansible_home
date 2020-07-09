# Music player Ansible Role

![Ansible Role: "jgoutin.home.musicplayer"](https://github.com/JGoutin/ansible_home/workflows/Ansible%20Role:%20%22jgoutin.home.musicplayer%22/badge.svg)

## Description

This role installs a music player in standalone mode.
By default, [Lollypop](https://gitlab.gnome.org/World/lollypop), but should work with 
the player of your choice (Audacious, Clementine, Strawberry, ...).

This is intended to turn a computer into a dedicated music player that can be used with 
a small touchscreen for view and control.

### Features

* Music player of your choice installation.
* Run as a standalone fullscreen application using Wayland and Sway.
* Use Alsa for high quality sound output.
* Configure `playerctl` to allow the use with multimedia keyboards and compatible volume 
  knobs.
* Ensure Alsa device is unmuted on player start.

#### About sound quality

With "Fedora minimal" as base OS, Pulseaudio is not installed, Alsa will be used by 
default by music players even if not providing an output selection option.
This will result in a bit-perfect quality sound output.

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
| `musicplayer_package` | `lollypop` | Name of the music player Fedora package.
| `musicplayer_volume_ctrl_method` | `alsa` | Name of the music player Fedora package. Possible values are `alsa` to use Alsa mixer or `playerctl` to use music player volume control.
| `musicplayer_volume_ctrl_percent` | 5 | Amount of volume in percent to decrease/increase with the volume control.

It is also recommended to look at the [**common**](common.md) role variables to
customize the server OS (SSH, NTP, Firewall, and more).

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
