# CoTURN Ansible Role

![Ansible Role: "jgoutin.home.coturn"](https://github.com/JGoutin/ansible_home/workflows/Ansible%20Role:%20%22jgoutin.home.coturn%22/badge.svg)

## Description

This role installs the [CoTURN](https://github.com/coturn/coturn) TURN/STUN server.

### Features

Configuration:
* Installs CoTURN.
* Runs unprivileged in a Systemd sandbox.
* Sets up TLS certificate (or generates self-signed certificate).
* Uses [modern TLS configuration from Mozilla](https://ssl-config.mozilla.org/#config=modern).

## Dependencies

*None*

## Variables

### Mandatory

| Name           | Default Value | Description                        |
| -------------- | ------------- | -----------------------------------|
| `coturn_realm`| | Server domain.
| `coturn_static_auth_secret`| | TURN credentials.

### Optional

| Name           | Default Value | Description                        |
| -------------- | ------------- | -----------------------------------|
| `coturn_bps_capacity`| 0 | Max bandwidth per session. Default to no limit.
| `coturn_firewalld_source` | | If specified, restrict the proxy access to the specified sources list in CIDR notation (`["192.168.1.10/32", "192.168.1.0/24", "2001:db8:1234:5678::/64"]`, ...). By default, allow all using `public` zone. Exclusive with `coturn_firewalld_zone` parameter.
| `coturn_firewalld_zone` | | If specified, the existing firewalld zone where allow proxy access. By default, use `public` zone. Exclusive with `coturn_firewalld_source` parameter.
| `coturn_listening_port`| 3478 | Server port.
| `coturn_tls_certificate`| | Path to the TLS certificate associated to the `coturn_realm` domain.
| `coturn_tls_certificate_key`| | Path to the TLS private key associated to the `coturn_realm` domain.
| `coturn_tls_listening_port`| 5349 | TLS server port.
| `coturn_total_quota`| 0 | Simultaneous connections limit. Default to no limit.

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
