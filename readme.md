This is a collection of Ansible roles for home free software self-hosting.

I use these roles at home to configure my personal servers and machines.

These roles are done with in mind:

* Up to date and fully featured software.
* Security.
* Minimal maintenance.

For more information on a particular role, please refer to its documentation inside its folder.

## Main roles

* `common`: Perform common machine initialisation task like configuring:
            auto-updates, firewall, NTP server, SSH and OS security hardening,
            ...
* `nextcloud`: Install a [Nextcloud](https://nextcloud.com) server.
* `kodi`: Install a [Kodi](https://kodi.tv) home theater personal computer.
* `mail`: Install a mail server using [Postfix](http://www.postfix.org/) and [Dovecot](https://www.dovecot.org/). [Work in progress]
* `mpd`: Install a [Music Player Daemon](https://www.musicpd.org/) server.

The `common` role is intended to be used with all other roles and may be 
required by some of them.

## Dependencies roles

These roles are used as main roles dependencies:

* `clamav`: Install [ClamAV](https://www.clamav.net) antivirus.
* `mariadb`: Install a [MariaDB](https://mariadb.org) database.
* `nginx`: Install a [Nginx](https://nginx.org) web server.
* `postgresql`: Install a [PostgreSQL](https://www.postgresql.org) database.
* `redis`: Install [Redis](https://redis.io) in memory data store.
* `rpmfusion`: Enable [RPMFusion](https://rpmfusion.org) repositories.

## Roles without readme status

* Nextcloud:
    * [X] Installation
    * [X] Nginx/PostgreSQL/PHP FPM/Redis/ClamAV configuration
    * [X] Initial configuration
    * [X] Applications and related dependencies installation
    * [X] Auto-updates
    * [X] OCC Bash auto-completion
    * [X] SELinux configuration
    * [X] Unix user permission setting
    * [ ] LibreOffice online / CollaboraOnline
    <!---
    https://nextcloud.com/collaboraonline/
    https://www.collaboraoffice.com/code/#what_is_code
    -->
    * [ ] Encryption keys back-up/recovery
    * [ ] `config.php` back-up/recovery
    * [ ] Enable enforced 2FA
    * [ ] Configured host full audit
    * [ ] Tests

* Nginx:
    * [X] Installation
    * [X] Default site configuration clean up
    * [X] Performance configuration tweaks
    * [X] Site specific configuration inclusion
    * [X] Hardening (Dev-Sec role)
    * [X] Security HTTP headers
    * [ ] Hide insecure HTTP headers <!--- https://veggiespam.com/headers/ -->
    * [X] SELinux boolean configuration
    * [X] Firewall configuration
    * [X] TLS certificate set up (or self-signed certificate generation)
    * [X] HTTP to HTTPS redirection
    * [X] PHP FPM support
    * [X] Unix user permission setting
    * [X] Service start
    * [ ] Tests

* PHP FPM:
    * [X] Installation with PHP modules
    * [X] Performance configuration tweaks
    * [X] Default site configuration clean up
    * [X] Service start
    * [ ] Tests

* PostgreSQL:
    * [X] Installation
    * [X] Unix socket only configuration
    * [X] Initial configuration
    * [X] Unix user permission setting
    * [X] Database setting
    * [X] Database user setting
    * [X] Service start
    * [ ] Tests

* Redis:
    * [X] Installation
    * [X] Unix socket only configuration
    * [X] SELinux configuration for web servers
    * [X] Service start
    * [X] Unix user permission setting
    * [X] Authentication setting
    * [ ] Tests

* RPM Fusion:
    * [X] Installation Free / Non-free
    * [X] Tests
