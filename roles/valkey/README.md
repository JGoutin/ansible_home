# Valkey Ansible Role

## Description

This role installs the [Valkey](https://valkey.io/) in-memory data store.

### Features

Configuration:
* Bind to Unix socket.
* Log in Systemd journal.
* With `common_netdata_enable` (see the [**common**](../common/README.md) role), monitor it with Netdata. Turning it off removes the collector configuration and the `netdata` user's access to the Valkey socket, only when the collector configuration is the role's (it starts with the "Managed by the jgoutin.home.valkey role" comment, or matches what earlier role versions wrote).

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
