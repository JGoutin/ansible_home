# PostgreSQL Ansible Role

## Description

This role installs a [PostgreSQL](https://www.postgresql.org) database.

### Features

Configuration:
* Bind to a Unix socket.
* Initialize the database.
  
Security:
* Run in a Systemd sandbox.
* Work with SElinux enforced.

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

The database may require to be updated on system upgrade, the role will try to perform
the update and reindex the database. 

To do it manually, run command `sudo postgresql-setup --upgrade` after the system 
upgrade, then re-apply the Ansible playbook (With `postgresql_upgrade` set to `false`). 
It is also recommended running `sudo -u postgres reindexdb -a` once the role completed.

A backup of the previous database is available as a `-old` suffixed copy of the
`data` sub-directory of the directory specified by `postgresql_data`
(Default to `/var/lib/pgsql/data-old`)

Read the PostgreSQL documentation for more information on database upgrades.
