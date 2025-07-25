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
To again improve security, hardening roles are applied in addition of some
security configuration.
To achieve the minimal maintenance, auto-updates (with auto-reboot, if required)
are set for all packages every day.

Of course, there are always drawbacks with all choices. In that case, it is the
risk of an update that breaks something and makes the service unavailable.

If you absolutely require a perfectly stable service with a 99.99% availability,
use some other role based on LTS OS and software versions.
No guarantee is provided with the use of these roles.

## Roles

### Main roles

* [**common**](roles/common/README.md): Perform common machine initialisation tasks like
  configuring: auto-updates, firewall, NTP server, SSH and OS security
  hardening,...
* [**nextcloud**](roles/nextcloud/README.md): Install a
  [Nextcloud](https://nextcloud.com) server.
* [**kodi**](roles/kodi/README.md): Install a [Kodi](https://kodi.tv) home theater
  personal computer.
* [**musicplayer**](roles/musicplayer/README.md): Install a standalone music player, by 
  default [Lollypop](https://gitlab.gnome.org/World/lollypop).
* [**mail**](roles/mail/README.md): Install a mail server using
  [Postfix](http://www.postfix.org/) and [Dovecot](https://www.dovecot.org/).
* [**mpd**](roles/mpd/README.md): Install a
  [Music Player Daemon](https://www.musicpd.org/) server.
* [**squid**](roles/squid/README.md): Install [Squid](https://www.squid-cache.org) 
  caching proxy server.

The **common** role is intended to be used with all other roles and may be
required by some of them.

### Dependencies roles

These roles are used as main roles dependencies:

* [**clamav**](roles/clamav/README.md): Install [ClamAV](https://www.clamav.net)
  antivirus.
* [**coturn**](roles/coturn/README.md): Install 
  [CoTURN](https://github.com/coturn/coturn) TURN/STUN server.
* [**nginx**](roles/nginx/README.md): Install a [Nginx](https://nginx.org) web server.
* [**postgresql**](roles/postgresql/README.md): Install a
  [PostgreSQL](https://www.postgresql.org) database.
* [**php_fpm**](roles/php_fpm/README.md): Install a [PHP-FPM](https://php-fpm.org)
  server.
* [**valkey**](roles/valkey/README.md): Install [Valkey](https://valkey.io) in memory data
  store.
* [**rpmfusion**](roles/rpmfusion/README.md): Enable [RPMFusion](https://rpmfusion.org)
  repositories.

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

## FAQ

Why recommend "Fedora Minimal" over "Fedora Server"?
> Fedora minimal is the Fedora version with the fewest pre-installed packages.
> Less packages means: less potential security vulnerabilities, less disc space 
> usage, less background services consuming RAM/CPU, less network usage on 
> packages update, ...
>
> In summary, this improves server security and energy consumption. 
> This can also help when running multiple virtual machines on the same host.
>
> Finally, if the Ansible role is done to work with the minimal version, it
> should work on any version with more packages. 
> So any variant can be freely used, the choice is yours.

Where find "Fedora Minimal"?
> Fedora Minimal is hidden and not directly provided as ISO on the Fedora 
> website.
>
> To install it, use the `Netinstall ISO image` of "Fedora Server" and select
> "Fedora Minimal" in the `Software Selection` screen.

How to upgrade Fedora when using these roles?
>A new Fedora version is released every 6 months, and it is highly recommended to 
>keep it up to date.
>
>Always ensure to have a back-up of your system before upgrading.
>
>Then, simply re-apply your Ansible playbook to upgrade fedora and ensure everything 
>is configured as intended.
>
>Some components like databases may require extra steps to upgrade. This is
>specified in the relevant role documentation.
>