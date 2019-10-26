This is a collection of Ansible roles for home free software self-hosting.

I use theses roles at home to configure my personal servers and machines.

Theses roles are done with in mind:

* Up to date and fully featured software.
* Security.
* Minimal maintenance.


Currently work in progress...

## Main roles

* `nextcloud`: Install a [Nextcloud](https://nextcloud.com) server.
* `kodi`: Install a [Kodi](https://kodi.tv) home theater personal computer.
* `mail`: Install a mail server using [Postfix](http://www.postfix.org/) and [Dovecot](https://www.dovecot.org/).
* `mpd`: Install a [Music Player Daemon](https://www.musicpd.org/) server.

## Dependencies roles

Theses roles are used as main roles dependencies:

* `common`: Perform common machine initialisation task like configuring:
            auto-updates, firewall, NTP server, SSH and OS security hardening,
            ...
* `clamav`: Install [ClamAV](https://www.clamav.net) antivirus.
* `mariadb`: Install a [MariaDB](https://mariadb.org) database.
* `nginx`: Install a [Nginx](https://nginx.org) web server.
* `postgresql`: Install a [PostgreSQL](https://www.postgresql.org) database.
* `redis`: Install [Redis](https://redis.io) in memory data store.
* `rpmfusion`: Enable [RPMFusion](https://rpmfusion.org) repositories.
