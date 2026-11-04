# ClamAV Ansible Role

## Description

This role installs the [ClamAV](https://www.clamav.net) antivirus.

### Features

Configuration:
* Install ClamAV and unofficial signature databases.
* Configure automatic definition updates (`clamav-freshclam` service).
* Configure an automatic scanning service.
* Run the scanner (`clamd@scan`) and the updater in a systemd sandbox. The scanner has a private `/tmp` and reads the
  rest of the system read-only: to scan files under `/tmp` or `/var/tmp`, pass `--fdpass` or `--stream` to `clamdscan`.

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
