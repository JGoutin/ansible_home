# Kodi Ansible Role

![Ansible Role: "jgoutin.home.kodi"](https://github.com/JGoutin/ansible_home/workflows/Ansible%20Role:%20%22jgoutin.home.kodi%22/badge.svg)

## Description

This role installs [Kodi](https://kodi.tv) and configures it to automatically start a 
dedicated home theater personal computer.

### Features

Configuration:
* Run as a standalone fullscreen application.
* Support existing Kodi profile restoration.
* Optional IR devices support.
* Optional PVR plugins support.

Security:
* Run unprivileged.
* Work with SElinux enforced.
* Configure the firewall.

Notes: The **kodi** role combines well with [**mpd**](../mpd/README.md) role to create a
multimedia computer.

## Dependencies

### OS recommendation

* "Fedora minimal" is recommended. 
* "Fedora server" is recommended if its additional functionalities are required.

### Roles

* common

## Variables

### Optional

| Name                        | Default Value | Description                                                                                                                                                                                                                                                                                                                     |
|-----------------------------|---------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `kodi_power_button_confirm` | false         | If `true`, confirm exit when computer power button is pressed.                                                                                                                                                                                                                                                                  |
| `kodi_firewalld_source`     |               | If specified, restrict the Kodi remote control to the specified sources list in CIDR notation (`["192.168.1.10/32", "192.168.1.0/24", "2001:db8:1234:5678::/64"]`, ...). By default, allow all machines from the current local network.                                                                                         |                                                                                                                                                  |
| `kodi_ir_remote`            | false         | If `true`, install Lirc to enable IR devices support.                                                                                                                                                                                                                                                                           |
| `kodi_libretro`             | true          | If `true`, install Kodi Libretro add-on and a repository providing Libretro cores add-ons. Allow the use of games and emulators inside Kodi.                                                                                                                                                                                    |
| `kodi_plugins_pvr`          | []            | List of names of PVR plugin(s) to install (for instance `["iptvsimple"]`). Selected plugins to install must me available on Fedora repositories (Can be listed with `dnf list kodi-pvr-*` on your Kodi installed machine).                                                                                                      |
| `kodi_remote_control`       | false         | If `true`, configure Firewalld to allow Kodi remote control over the network.                                                                                                                                                                                                                                                   |
| `kodi_restore_profile`      |               | If specified, restore a previously exiting Kodi profile from the specified ZIP archive path. The archive must contain the `~/.kodi/` content with no extra top directory. )                                                                                                                                                     |
| `kodi_wayland`              | false         | If `true`, use Wayland as display manager (With Sway compositor) instead of Kodi GBM. GBM is generally recommended over Wayland.                                                                                                                                                                                                |
| `kodi_wayland_output`       |               | If specified and `kodi_wayland` is `true`, set configuration for this display output. If not specified, the default display configuration will be used. Possible values like `HDMI-A-1`, available displays are listed when starting the kodi service, use `journalvtl -u kodi` to see result as list and get the `name` field. |
| `kodi_wayland_output_mode`  |               | If specified along with `kodi_wayland_output`, set this mode for this display, values are in the form `3840x2160@29.97Hz`, `3840x2160`.                                                                                                                                                                                         |

It is also recommended to look at the [**common**](../common/README.md) role variables
to customize the server OS (SSH, NTP, Firewall, and more).

The `common_os_hardening=false` option is recommended with this role because performance
and full hardware support are important for Kodi, and improved security is generally not
relevant on an HTPC. The `common_cpu_vulnerabilities_mitigation=off` option can also be 
set to improve the performance.

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
    - kodi
```
