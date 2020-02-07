# Redis Ansible Role

## Description

This role installs a [Redis](https://redis.io) in memory data store.

### Features

* Installation
* Unix socket based configuration
* SELinux configuration for web servers
* Service start
* Unix user permission setting
* Authentication setting
    
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
  roles:
    - jgoutin.home.redis
```

## Work in progress / planned

* CI
