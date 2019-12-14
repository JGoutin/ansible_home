# Kodi Ansible Role

## Description

This role install [Kodi](https://kodi.tv) and configure it to start automatically on a dedicated
home theater personal computer.

### Features

* Installation with auto start
* GPU drivers installation
* Kodi profile restoration
* IR device setting
* Firewall configuration

## dependencies

* common

## Variables

| Name           | Default Value | Description                        |
| -------------- | ------------- | -----------------------------------|
| `kodi_firewalld_source`| | If specified, restrict the Kodi remote control to the specified source in CIDR notation (`192.168.1.10/32`, `192.168.1.0/24`, ...). By default, allow all machines from the current local network.
| `kodi_gpu_vendor`| intel | Graphical card vendor. May be `intel` or `amd`. Used to install proper GPU drivers.
| `kodi_ir_remote`| false | If `true`, install Lirc to enable IR devices support.
| `kodi_remote_control`| false | If `true`, configure Firewalld to allow Kodi remote control over the network.
| `kodi_restore_profile`| | If specified, restore a previously exiting Kodi profile from the specified ZIP archive path. The archive must contain the `~/.kodi/` content with no extra top directory.

## Example Playbook

```yaml
- hosts: localhost
  roles:
    - kodi
```

## Work in progress / planned

* Tests
