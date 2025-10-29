# Valkey Ansible Role

## Description

This role installs the [Valkey](https://valkey.io/) in-memory data store.

### Features

Configuration:
* Bind to Unix socket.
* Log in Systemd journal.

Security:
* Run in a Systemd sandbox.
* Works with SELinux enforced.

## Dependencies

*None*

## Variables

### Optional

| Name               | Default Value | Description                                          |
|--------------------|---------------|------------------------------------------------------|
| `valkey_log_level` | `"warning"`   | Valkey log level in the journal.                     |
| `valkey_user`      |               | If specified, allow this Unix user to access Valkey. |

## Example Playbook

```yaml
---
- hosts: all
  become: true
  collections:
    - jgoutin.home
  roles:
    - valkey
```
