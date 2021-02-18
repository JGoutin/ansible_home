# Redis Ansible Role

![Ansible Role: "jgoutin.home.redis"](https://github.com/JGoutin/ansible_home/workflows/Ansible%20Role:%20%22jgoutin.home.redis%22/badge.svg)

## Description

This role installs a [Redis](https://redis.io) in memory data store.

### Features

Configuration:
* Binds to an Unix socket.
  
Security:
* Runs unprivileged in a Systemd sandbox.
* Works with SElinux enforced.

## Dependencies

*None*

## Variables

### Optional

| Name           | Default Value | Description                        |
| -------------- | ------------- | -----------------------------------|
| `redis_user`| | If specified, allow this Unix user to access to Redis.

## Example Playbook

```yaml
---
- hosts: all
  become: true
  collections:
    - jgoutin.home
  roles:
    - redis
```
