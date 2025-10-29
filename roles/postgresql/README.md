# PostgreSQL Ansible Role

## Description

This role installs a [PostgreSQL](https://www.postgresql.org) database.

### Features

Configuration:
* Bind to a Unix socket.
* Initialize the database.
  
Security:
* Run in a Systemd sandbox.
* Works with SELinux enforced.

## Dependencies

*None*

## Variables

### Optional

| Name                   | Default Value    | Description                                                                        |
|------------------------|------------------|------------------------------------------------------------------------------------|
| `postgresql_data`      | `/var/lib/pgsql` | Path to the database. A `data` subdirectory is created inside this directory.      |
| `postgresql_database`  |                  | If specified, creates a database with this name.                                   |
| `postgresql_local`     |                  | If specified, install associated language packs.                                   |
| `postgresql_upgrade`   | true             | If `true`, the role will upgrade and reindex the database if required.             |
| `postgresql_user`      |                  | If specified, creates a database user with this name, must match a Unix user name. |

## Example Playbook

```yaml
---
- hosts: all
  become: true
  collections:
    - jgoutin.home
  roles:
    - postgresql
```

## System upgrade

The database may need to be updated during a system upgrade; the role will attempt to perform the update and reindex the database.

To do it manually, run `sudo postgresql-setup --upgrade` after the system upgrade, then reapply the Ansible playbook (with `postgresql_upgrade` set to `false`). It is also recommended to run `sudo -u postgres reindexdb -a` once the role has completed.

A backup of the previous database is available as a `-old` suffixed copy of the `data` subdirectory of the directory specified by `postgresql_data` (defaults to `/var/lib/pgsql/data-old`).

Read the PostgreSQL documentation for more information on database upgrades.

### Fedora 42 to 43 upgrade (PostgreSQL 16 to 18)

Fedora 43 upgrades PostgreSQL from 16 to 17. This breaks the automatic upgrade with the role or direct usage of `postgresql-setup --upgrade`.
In addition, checksums are enabled on PostgreSQL 18.
The following commands are required (from Fedora 43):

```bash
# Upgrade PostgreSQL from 16 to 17
sudo dnf install postgresql17-server postgresql17 postgresql17-upgrade --allowerasing
sudo /usr/bin/postgresql-setup --upgrade

# Enable checksums (Adapt the pgdata path, for example /var/lib/nextcloud/pgsql/data/ with Nextcloud)
sudo pg_checksums --pgdata=/var/lib/pgsql/data/ --enable --progress --verbose

# Upgrade PostgreSQL from 17 to 18, and install PostgreSQL 18
sudo dnf install postgresql-server postgresql-upgrade postgresql-contrib --allowerasing
sudo /usr/bin/postgresql-setup --upgrade
```
