# Redis Ansible Role

## Description

This role installs a [Redis](https://redis.io) in memory data store.

### Features

Configuration:
* Bind to Unix socket.
* Log in Systemd journal.

Security:
* Run in a Systemd sandbox.
* Work with SElinux enforced.

## Dependencies

*None*

## Variables

### Optional

| Name         | Default Value | Description                                            |
|--------------|---------------|--------------------------------------------------------|
| `redis_user` |               | If specified, allow this Unix user to access to Redis. |

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
