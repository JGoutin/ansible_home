# ClamAV Ansible Role

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
