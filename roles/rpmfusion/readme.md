# Redis Ansible Role

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
  roles:
    - jgoutin.home.rpmfusion
  vars:
    rpmfusion_free: true
```

## Work in progress / planned

* CI
