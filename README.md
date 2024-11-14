[![Code lint](https://github.com/JGoutin/ansible_home/actions/workflows/lint.yml/badge.svg)](https://github.com/JGoutin/ansible_home/actions/workflows/lint.yml)

This is a collection of Ansible roles for free software self-hosting.

This collection mainly targets individuals or eventually small companies, but is
done with professional quality standards.

These roles are done with in mind:

* Up to date and fully featured software.
* Security.
* Minimal maintenance.

To achieve well the two first points, [Fedora](https://getfedora.org/) is used
as the base OS because it always provides up-to-date versions of software and
advanced security feature like SELinux by default.
To again improve the security, optional system-wide hardening can be applied and many 
security-related configurations are available.
To achieve the minimal maintenance, auto-updates (with auto-reboot, if required)
are set for all packages every day.

Of course, there are always drawbacks with all choices. In that case, it is the
risk of an update that breaks something and makes the service unavailable.

If you absolutely require a perfectly stable service with a 99.99% availability,
use some other role based on LTS OS and software versions.
No guarantee is provided with the use of these roles.

## Roles

For more information on roles, please refer to the 
[documentation](https://jgoutin.github.io/ansible_home/).

### Main roles

* **common**: Perform common machine initialisation tasks like configuring:
  auto-updates, firewall, NTP server, SSH and OS security hardening,...
* **nextcloud**: Install a [Nextcloud](https://nextcloud.com) server.
* **musicplayer**: Install a standalone music player, by default 
  [Lollypop](https://gitlab.gnome.org/World/lollypop).
* **kodi**: Install a [Kodi](https://kodi.tv) home theater personal computer.
* **mail**: Install a mail server using [Postfix](http://www.postfix.org/) and
  [Dovecot](https://www.dovecot.org/).
* **mpd**: Install a [Music Player Daemon](https://www.musicpd.org/) server.
* **squid**: Install [Squid](https://www.squid-cache.org) caching proxy server.

The **common** role is intended to be used with all other roles and may be
required by some of them.

### Dependencies roles

These roles are used as main roles dependencies, but is it also possible to use them
directly:

* **clamav**: Install [ClamAV](https://www.clamav.net) antivirus.
* **coturn**: Install [CoTURN](https://github.com/coturn/coturn) TURN/STUN server.
* **nginx**: Install a [Nginx](https://nginx.org) web server.
* **postgresql**: Install a [PostgreSQL](https://www.postgresql.org) database.
* **php_fpm**: Install a [PHP-FPM](https://php-fpm.org) server.
* **valkey**: Install [Valkey](https://valkey.io) in memory data store.
* **rpmfusion**: Enable [RPMFusion](https://rpmfusion.org) repositories.

## Installation

This collection is available on
[Ansible Galaxy](https://galaxy.ansible.com/jgoutin/home).

```bash
ansible-galaxy collection install jgoutin.home
```

## Example Playbook

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
