
![Ansible Role: "jgoutin.home.clamav"](https://github.com/JGoutin/ansible_home/actions/workflows/clamav.yml/badge.svg)
![Ansible Role: "jgoutin.home.common"](https://github.com/JGoutin/ansible_home/actions/workflows/common.yml/badge.svg)
![Ansible Role: "jgoutin.home.coturn"](https://github.com/JGoutin/ansible_home/actions/workflows/coturn.yml/badge.svg)
![Ansible Role: "jgoutin.home.kodi"](https://github.com/JGoutin/ansible_home/actions/workflows/kodi.yml/badge.svg)
![Ansible Role: "jgoutin.home.musicplayer"](https://github.com/JGoutin/ansible_home/actions/workflows/musicplayer.yml/badge.svg)
![Ansible Role: "jgoutin.home.mail"](https://github.com/JGoutin/ansible_home/actions/workflows/mail.yml/badge.svg)
![Ansible Role: "jgoutin.home.mpd"](https://github.com/JGoutin/ansible_home/actions/workflows/mpd.yml/badge.svg)
![Ansible Role: "jgoutin.home.nextcloud"](https://github.com/JGoutin/ansible_home/actions/workflows/nextcloud.yml/badge.svg)
![Ansible Role: "jgoutin.home.nginx"](https://github.com/JGoutin/ansible_home/actions/workflows/nginx.yml/badge.svg)
![Ansible Role: "jgoutin.home.php_fpm"](https://github.com/JGoutin/ansible_home/actions/workflows/php_fpm.yml/badge.svg)
![Ansible Role: "jgoutin.home.postgresql"](https://github.com/JGoutin/ansible_home/actions/workflows/postgresql.yml/badge.svg)
![Ansible Role: "jgoutin.home.redis"](https://github.com/JGoutin/ansible_home/actions/workflows/redis.yml/badge.svg)
![Ansible Role: "jgoutin.home.rpmfusion"](https://github.com/JGoutin/ansible_home/actions/workflows/rpmfusion.yml/badge.svg)
![Ansible Role: "jgoutin.home.squid"](https://github.com/JGoutin/ansible_home/actions/workflows/squid.yml/badge.svg)

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
* **redis**: Install [Redis](https://redis.io) in memory data store.
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
