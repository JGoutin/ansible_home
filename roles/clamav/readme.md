# ClamAV Ansible Role

## Description

This role installs the [ClamAV](https://www.clamav.net) antivirus.

### Features

* Install ClamAV + unofficial signatures.
* Configure automatic definitions updates.
* Configure automatic scan service.

## dependencies

*None*

## Variables

*None*

## Example Playbook

```yaml
- hosts: localhost
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
* Tests
