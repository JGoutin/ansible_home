# CoTURN Ansible Role

## Description

This role installs the [CoTURN](https://github.com/coturn/coturn) TURN/STUN server.

### Features

Configuration:
* Install CoTURN.
* Run unprivileged in a Systemd sandbox.
* Set up a TLS certificate (or generate a self-signed certificate).
* Use [modern TLS configuration from Mozilla](https://ssl-config.mozilla.org/#config=modern).
* Log in the Systemd journal.

## Dependencies

*None*

## Variables

### Mandatory

| Name                        | Default Value | Description       |
|-----------------------------|---------------|-------------------|
| `coturn_realm`              |               | Server domain.    |
| `coturn_static_auth_secret` |               | TURN credentials. |

### Optional

| Name                         | Default Value | Description                                                                                                                                                                                                                                                            |
|------------------------------|---------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `coturn_bps_capacity`        | 0             | Maximum bandwidth per session. Defaults to no limit.                                                                                                                                                                                                                   |
| `coturn_firewalld_source`    |               | If specified, restrict TURN/STUN access to the specified sources list in CIDR notation (`["192.168.1.10/32", "192.168.1.0/24", "2001:db8:1234:5678::/64"]`, ...). By default, allow all using the `public` zone. Exclusive with the `coturn_firewalld_zone` parameter. |
| `coturn_firewalld_zone`      |               | If specified, the existing firewalld zone where TURN/STUN access is allowed. By default, use the `public` zone. Exclusive with the `coturn_firewalld_source` parameter.                                                                                                |
| `coturn_listening_port`      | 3478          | TURN server port.                                                                                                                                                                                                                                                      |
| `coturn_tls_certificate`     |               | Path to the TLS certificate associated with the `coturn_realm` domain.                                                                                                                                                                                                 |
| `coturn_tls_certificate_key` |               | Path to the TLS private key associated with the `coturn_realm` domain.                                                                                                                                                                                                 |
| `coturn_tls_listening_port`  | 5349          | TURN TLS port.                                                                                                                                                                                                                                                         |
| `coturn_total_quota`         | 0             | Simultaneous connections limit. Defaults to no limit.                                                                                                                                                                                                                  |

## Example Playbook

```yaml
---
- hosts: all
  become: true
  collections:
    - jgoutin.home
  roles:
    - coturn
  vars:
    coturn_realm: my_turn.com
    coturn_static_auth_secret: my_secret_password
```
