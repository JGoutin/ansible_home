# RPM Fusion Ansible Role

## Description

This role enables the [RPM Fusion](https://rpmfusion.org) repositories.

### Features

Configuration:
* Enable the Free and/or Nonfree repositories.
    
## Dependencies

*None*

## Variables

### Optional

| Name                | Default Value | Description                                          |
|---------------------|---------------|------------------------------------------------------|
| `rpmfusion_free`    | false         | If `true`, enable the RPM Fusion Free repository.    |
| `rpmfusion_nonfree` | false         | If `true`, enable the RPM Fusion Nonfree repository. |

## Example Playbook

```yaml
---
- hosts: all
  become: true
  collections:
    - jgoutin.home
  roles:
    - rpmfusion
  vars:
    rpmfusion_free: true
```
