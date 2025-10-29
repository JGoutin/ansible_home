# ClamAV Ansible Role

## Description

This role installs the [ClamAV](https://www.clamav.net) antivirus.

### Features

Configuration:
* Install ClamAV and unofficial signature databases.
* Configure automatic definition updates.
* Configure an automatic scanning service.

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
