This repository contains a collection of Ansible roles for self-hosting free software.

The collection primarily targets individuals and small businesses and is built to professional quality standards.

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

### Main roles

* [**common**](roles/common/README.md): Perform common machine initialization tasks such as configuring auto-updates, firewall, NTP server, SSH, and OS security hardening.
* [**nextcloud**](roles/nextcloud/README.md): Install a [Nextcloud](https://nextcloud.com) server.
* [**kodi**](roles/kodi/README.md): Install a [Kodi](https://kodi.tv) home theater PC.
* [**musicplayer**](roles/musicplayer/README.md): Install a standalone music player, by default [Lollypop](https://gitlab.gnome.org/World/lollypop).
* [**mail**](roles/mail/README.md): Install a mail server using [Postfix](http://www.postfix.org/) and [Dovecot](https://www.dovecot.org/).
* [**mpd**](roles/mpd/README.md): Install a [Music Player Daemon](https://www.musicpd.org/) server.
* [**squid**](roles/squid/README.md): Install a [Squid](https://www.squid-cache.org) caching proxy server.

The **common** role is intended to be used with all other roles and may be required by some of them.

### Dependency roles

These roles are used as dependencies of the main roles:

* [**clamav**](roles/clamav/README.md): Install the [ClamAV](https://www.clamav.net) antivirus.
* [**coturn**](roles/coturn/README.md): Install the [CoTURN](https://github.com/coturn/coturn) TURN/STUN server.
* [**nginx**](roles/nginx/README.md): Install an [Nginx](https://nginx.org) web server.
* [**postgresql**](roles/postgresql/README.md): Install a [PostgreSQL](https://www.postgresql.org) database.
* [**php_fpm**](roles/php_fpm/README.md): Install a [PHP-FPM](https://php-fpm.org) server.
* [**valkey**](roles/valkey/README.md): Install the [Valkey](https://valkey.io) in-memory data store.
* [**rpmfusion**](roles/rpmfusion/README.md): Enable the [RPMFusion](https://rpmfusion.org) repositories.

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

## FAQ

Why recommend "Fedora Minimal" over "Fedora Server"?
> Fedora Minimal is the Fedora variant with the fewest preinstalled packages.
> Fewer packages means fewer potential vulnerabilities, less disk space usage,
> fewer background services consuming RAM/CPU, and lower network usage during updates.
>
> In summary, this improves server security and energy consumption. 
> It can also help when running multiple virtual machines on the same host.
>
> Finally, if an Ansible role works with the Minimal variant, it should work on
> any variant with more packages. The choice is yours.

Where can I find "Fedora Minimal"?
> Fedora Minimal is not directly provided as an ISO on the Fedora website.
>
> To install it, use the `Netinstall ISO image` of Fedora Server and select
> "Fedora Minimal" in the `Software Selection` screen.

How do I upgrade Fedora when using these roles?
> A new Fedora version is released every 6 months, and it is highly recommended to
> keep it up to date.
>
> Always ensure you have a backup of your system before upgrading.
>
> Then, simply reapply your Ansible playbook to upgrade Fedora and ensure everything
> is configured as intended.
>
> Some components, such as databases, may require extra steps to upgrade. This is
> specified in the relevant role documentation.
>