# ClamAV Ansible Role

![Ansible Role: "jgoutin.home.clamav"](https://github.com/JGoutin/ansible_home/workflows/Ansible%20Role:%20%22jgoutin.home.clamav%22/badge.svg)

## Description

This role installs the [ClamAV](https://www.clamav.net) antivirus.

### Features

Configuration:
* Installs ClamAV and unofficial signatures.
* Configures automatic definitions updates.
* Configures automatic scan service.

## Dependencies

*None*

## Variables

*None*

## Example Playbook

```yaml
---
- hosts: all
  become: true
  collections:
    - jgoutin.home
  roles:
    - clamav
```
