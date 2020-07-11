# Redis Ansible Role

![Ansible Role: "jgoutin.home.rpmfusion"](https://github.com/JGoutin/ansible_home/workflows/Ansible%20Role:%20%22jgoutin.home.rpmfusion%22/badge.svg)

## Description

This role enables [RPMFusion](https://rpmfusion.org) repositories.

### Features

* Enable Free and Non-free repositories
    
## Dependencies

*None*

## Variables

### Optional

| Name           | Default Value | Description                        |
| -------------- | ------------- | -----------------------------------|
| `rpmfusion_free`| false | If `true`, enable RPMFusion Free repository.
| `rpmfusion_nonfree`| false | If `true`, enable RPMFusion Non-Free repository.

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
