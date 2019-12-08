This is a collection of Ansible roles for home free software self-hosting.

I use these roles at home to configure my personal servers and machines.

These roles are done with in mind:

* Up to date and fully featured software.
* Security.
* Minimal maintenance.

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

## Project status

This project is work in progress, here is the advancement status:

### Roles

* ClamAv:
    * [X] ClamAv and definitions installation
    * [X] Definitions auto-update
    * [X] Scan service start
    * [ ] SELinux configuration
    <!---
    Maybe requires:
    - "setsebool -P antivirus_can_scan_system 1"
    - "chcon -t clamd_var_run_t /var/run/clamd.scan/clamd.sock"
    -->
    * [ ] Tests

* Common:
    * [ ] Admin mail redirection
    * [X] Firewall admin restriction
    * [X] SSH authorized key setting
    * [X] SSH hardening (Dev-Sec role)
    * [X] OS hardening (Dev-Sec role)
    * [X] Fail2ban installation
    * [X] User password setting
    * [X] NTP client configuration
    * [X] Grub timeout setting
    * [X] DNF speed up
    * [X] DNF auto-updates
    * [X] NFS share set up
    * [X] CIFS/SMB share set up
    * [ ] Mails alert (Fail2ban, auditd, DNF automatic, user connexion)
    * [ ] `/tmp` as TMPFS
    * [ ] Tests

* Kodi:
    * [X] Installation
    * [X] GPU drivers installation
    * [X] Configuration restoration
    * [X] Autostart
    * [X] IR device setting
    * [X] Firewall configuration
    * [ ] Tests

* Mail:
    * [X] Postfix & Dovecot installation
    * [ ] Postfix configuration
    * [ ] Dovecot configuration
    * [X] TLS configuration
    * [X] Postfix & Dovecot services start
    * [X] Firewall configuration
    * [ ] Tests

* MariaDB:
    * [X] Installation
    * [X] Database setting
    * [X] Database user setting
    * [X] Service start
    * [X] Hardening (Dev-Sec role)
    * [ ] Tests

* MPD:
    * [X] Installation
    * [X] Configuration
    * [X] SELinux configuration
    * [X] Alsa devices unmute
    * [X] Socket service start
    * [X] Firewall configuration
    * [ ] Tests

* Nextcloud:
    * [X] Installation
    * [X] Nginx/PostgreSQL/PHP FPM/Redis/ClamAV configuration
    * [X] Initial configuration
    * [X] Applications and related dependencies installation
    * [X] Auto-updates
    * [X] OCC Bash auto-completion
    * [X] SELinux configuration
    * [X] Unix user permission setting
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

### Common

* [ ] CI
* [ ] Ansible clean up (Remove packages/dirs used by Ansible but not required)
