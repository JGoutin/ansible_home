[![Code lint](https://github.com/JGoutin/ansible_home/actions/workflows/lint.yml/badge.svg)](https://github.com/JGoutin/ansible_home/actions/workflows/lint.yml)

This repository contains a collection of Ansible roles for self-hosting free software.

The collection primarily targets individuals and small businesses, and is built to professional quality standards.

These roles are designed with the following goals in mind:

* Up-to-date and fully featured software
* Security
* Minimal maintenance

To meet the first two goals, [Fedora](https://getfedora.org/) is used as the base OS because it provides up-to-date software and advanced security features such as SELinux by default.
To further improve security, optional system-wide hardening can be applied and many security-related configurations are available.
To minimize maintenance, automatic updates (with automatic reboot when required) are enabled daily for all packages.

All choices come with trade-offs. Here, the main risk is that an update could break something and temporarily make a service unavailable.

If you require a perfectly stable service with 99.99% availability, consider other roles based on LTS operating systems and software versions. No guarantee is provided when using these roles.

## Roles

For more information on the roles, please refer to the [documentation](https://jgoutin.github.io/ansible_home/).

### Main roles

* **common**: Perform common machine initialization tasks such as configuring auto-updates, firewall, NTP server, SSH, and OS security hardening.
* **nextcloud**: Install a [Nextcloud](https://nextcloud.com) server.
* **musicplayer**: Install a standalone music player, by default [Lollypop](https://gitlab.gnome.org/World/lollypop).
* **kodi**: Install a [Kodi](https://kodi.tv) home theater PC.
* **mail**: Install a mail server using [Postfix](http://www.postfix.org/) and [Dovecot](https://www.dovecot.org/).
* **mpd**: Install a [Music Player Daemon](https://www.musicpd.org/) server.
* **squid**: Install a [Squid](https://www.squid-cache.org) caching proxy server.

The **common** role is intended to be used with all other roles and may be required by some of them.

### Dependency roles

These roles are used as dependencies of the main roles, but can also be used directly:

* **clamav**: Install the [ClamAV](https://www.clamav.net) antivirus.
* **coturn**: Install the [CoTURN](https://github.com/coturn/coturn) TURN/STUN server.
* **nginx**: Install an [Nginx](https://nginx.org) web server.
* **postgresql**: Install a [PostgreSQL](https://www.postgresql.org) database.
* **php_fpm**: Install a [PHP-FPM](https://php-fpm.org) server.
* **valkey**: Install the [Valkey](https://valkey.io) in-memory data store.
* **rpmfusion**: Enable the [RPMFusion](https://rpmfusion.org) repositories.

## Installation

This collection is available on [Ansible Galaxy](https://galaxy.ansible.com/jgoutin/home).

```bash
ansible-galaxy collection install jgoutin.home
```

## Example playbook

```yaml
---
- hosts: all
  become: true
  collections:
    - jgoutin.home
  roles:
    - common
    - kodi
```
