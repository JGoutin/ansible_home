# ClamAV Ansible Role

![Ansible Role: "jgoutin.home.clamav"](https://github.com/JGoutin/ansible_home/workflows/Ansible%20Role:%20%22jgoutin.home.clamav%22/badge.svg)

## Description

This role installs the [ClamAV](https://www.clamav.net) antivirus.

### Features

* Install ClamAV + unofficial signatures.
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

## Work in progress / planned

* SELinux configuration check
<!---
Maybe requires:
- "setsebool -P antivirus_can_scan_system 1"
- "chcon -t clamd_var_run_t /var/run/clamd.scan/clamd.sock"
-->
