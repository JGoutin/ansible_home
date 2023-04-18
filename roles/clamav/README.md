# ClamAV Ansible Role

![Ansible Role: "jgoutin.home.clamav"](https://github.com/JGoutin/ansible_home/workflows/Ansible%20Role:%20%22jgoutin.home.clamav%22/badge.svg)

## Description

This role installs the [ClamAV](https://www.clamav.net) antivirus.

### Features

Configuration:
* Install ClamAV and unofficial signatures.
* Configure automatic definitions updates.
* Configure automatic scan service.

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
