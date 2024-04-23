# Kodi Ansible Role

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

| Name                             | Default Value | Description                                                                                                                                                                                                                             |
|----------------------------------|---------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `kodi_power_button_confirm`      | false         | If `true`, confirm exit when computer power button is pressed.                                                                                                                                                                          |
| `kodi_firewalld_source`          |               | If specified, restrict the Kodi remote control to the specified sources list in CIDR notation (`["192.168.1.10/32", "192.168.1.0/24", "2001:db8:1234:5678::/64"]`, ...). By default, allow all machines from the current local network. |                                                                                                                                                  |
| `kodi_ir_remote`                 | false         | If `true`, install Lirc to enable IR devices support.                                                                                                                                                                                   |
| `kodi_plugins_pvr`               | []            | List of names of PVR plugin(s) to install (for instance `["iptvsimple"]`). Selected plugins to install must me available on Fedora repositories (Can be listed with `dnf list kodi-pvr-*` on your Kodi installed machine).              |
| `kodi_remote_control`            | false         | If `true`, configure Firewalld to allow Kodi remote control over the network.                                                                                                                                                           |
| `kodi_restore_profile`           |               | If specified, restore a previously exiting Kodi profile from the specified ZIP archive path. The archive must contain the `~/.kodi/` content with no extra top directory. )                                                             |
| `kodi_wayland`                   | false         | If `true`, use Wayland as display manager (With Sway compositor) instead of Kodi GBM. GBM is generally recommended over Wayland.                                                                                                        |
| `kodi_wayland_output_width`      |               | If specified along with `kodi_wayland_output_height`, set this pixel width of the output.                                                                                                                                               |
| `kodi_wayland_output_height`     |               | If specified along with `kodi_wayland_output_width`, set this pixel height of the output.                                                                                                                                               |
| `kodi_wayland_output_rate`       |               | If specified along with `kodi_wayland_output_height` and `kodi_wayland_output_width`, set the refresh rate of the output in Hz.                                                                                                         |
| `kodi_xbox_controller_bluetooth` | false         | If `true`, install driver to allow the use of Bluetoolh Xbox controllers. **WARNING:** This will reboot the machine to trigger key enrollment in Secure Boot, follow instructions prompted on the screen just before the reboot step.   |

It is also recommended to look at the [**common**](../common/README.md) role variables
to customize the server OS (SSH, NTP, Firewall, and more).

The `common_os_hardening=false` option is recommended with this role because performance
and full hardware support are important for Kodi, and improved security is generally not
relevant on an HTPC. The `common_cpu_vulnerabilities_mitigation=off` option can also be 
set to improve the performance.

If using, `common_os_hardening=true`, `common_os_hardening_localpkg_gpgcheck=false` 
must be set if `kodi_xbox_controller_bluetooth=true`.

## How to connect Xbox controller with bluetooth

Kodi does not provide an interface to connect bluetooth controller.
This can be done using the command line with SSH with the following steps:
```bash
sudo bluetoothctl
# Start scan and wait until all available devices are listed (otherwise it may be hard 
# to identify which one is the gamepad) push the connect button on upper side of the 
# gamepad, and hold it down until the light starts flashing fast  wait for the gamepad
# to show up in bluetoothctl, remember the address (e.g. "C8:3F:26:XX:XX:XX")
[bluetooth]$ scan on
# to stop scanning as it may interfere with properly pairing the controller
[bluetooth]$ scan off
# Pair the controller using the MAC
[bluetooth]$ pair C8:3F:26:XX:XX:XX
[bluetooth]$ trust C8:3F:26:XX:XX:XX
# should usually not be needed but there are open bugs
[bluetooth]$ connect C8:3F:26:XX:XX:XX
# The MAC parameter is optional if the command line already shows the controller name.
```
For more details see the [xpadneo documentation](https://atar-axis.github.io/xpadneo/).

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
