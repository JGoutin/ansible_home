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

## Known issues

### The role fails on Fedora 45

Since 2026-11-03, dnf refuses to install the Fedora 45 release packages, `rpmfusion-free-release-45-1` and
`rpmfusion-nonfree-release-45-1`, with "nothing provides /usr/share/dnf5/libdnf.conf.d/". These packages require
that path with a trailing slash, and no package provides it. This is a packaging regression in RPM Fusion: the
previous release, `45-0.2`, installed fine. It also breaks the roles that include this one: kodi and nextcloud.

The role has no workaround. Wait for a fixed release package from RPM Fusion (`45-2` or later).
