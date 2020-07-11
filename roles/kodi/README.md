# Kodi Ansible Role

![Ansible Role: "jgoutin.home.kodi"](https://github.com/JGoutin/ansible_home/workflows/Ansible%20Role:%20%22jgoutin.home.kodi%22/badge.svg)

## Description

This role install [Kodi](https://kodi.tv) and configure it to start automatically a 
dedicated home theater personal computer.

### Features

* Installation with auto start
* GPU drivers installation
* Kodi profile restoration
* IR device setting
* Firewall configuration

Notes: The **kodi** role combines well with [**mpd**](mpd.md) role to create a
multimedia computer.

## Dependencies

### OS recommendation

* "Fedora minimal" is recommended. 
* "Fedora server" is recommended if its additional functionalities are required.

### Roles

* common

## Variables

### Optional

| Name           | Default Value | Description                        |
| -------------- | ------------- | -----------------------------------|
| `kodi_firewalld_source`| | If specified, restrict the Kodi remote control to the specified source in CIDR notation (`192.168.1.10/32`, `192.168.1.0/24`, ...). By default, allow all machines from the current local network.
| `kodi_gpu_vendor`| `intel` | Graphical card vendor. May be `intel` or `amd`. Used to install proper GPU drivers.
| `kodi_ir_remote`| false | If `true`, install Lirc to enable IR devices support.
| `kodi_remote_control`| false | If `true`, configure Firewalld to allow Kodi remote control over the network.
| `kodi_restore_profile`| | If specified, restore a previously exiting Kodi profile from the specified ZIP archive path. The archive must contain the `~/.kodi/` content with no extra top directory.

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
    - kodi
```

## Work in progress / planned

* Update to use Wayland instead of X11.
