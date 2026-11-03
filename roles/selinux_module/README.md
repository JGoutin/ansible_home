# SELinux Module Ansible Role

## Description

Internal role used by the other roles of this collection (`nextcloud`, `nginx`,
`squid`, `valkey`, `mpd`) to install their custom SELinux policy modules. It is
not meant to be used on its own.

### Features

Installation:
* Install `checkpolicy` and `policycoreutils` (with `rpm-ostree` on Atomic
  systems).
* Keep the module source `<name>.te` in `/usr/local/share/selinux`.
* Compile (`checkmodule`, `semodule_package`) and install (`semodule -i`) the
  module only when its source changed or `semodule -l` does not list it. These
  tasks report "changed" when they run.

The sources are in the `files` directory of this role, one `<name>.te` per
module.

## Dependencies

*None*

## Variables

### Required

| Name                  | Description                                                  |
|-----------------------|--------------------------------------------------------------|
| `selinux_module_name` | Module name, also the base name of `files/<name>.te`.        |

### Optional

| Name                     | Default Value             | Description                           |
|--------------------------|---------------------------|---------------------------------------|
| `selinux_module_src_dir` | `/usr/local/share/selinux` | Persistent directory for the sources. |

## Example Playbook

```yaml
---
- hosts: all
  become: true
  tasks:
    - name: Ensure the Nginx SELinux module is installed
      ansible.builtin.include_role:
        name: jgoutin.home.selinux_module
      vars:
        selinux_module_name: nginx
```
