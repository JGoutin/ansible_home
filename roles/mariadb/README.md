# MariaDB Ansible Role

![Ansible Role: "jgoutin.home.mariadb"](https://github.com/JGoutin/ansible_home/workflows/Ansible%20Role:%20%22jgoutin.home.mariadb%22/badge.svg)

## Description

This role installs a [MariaDB](https://mariadb.org) database

### Features

Configuration:
* Initializes the database.

Security:
* Applies extra hardening using [DevSec role](https://dev-sec.io/baselines/mysql).

## Variables

### Optional

| Name                | Default Value | Description                                                                                                                         |
|---------------------|---------------|-------------------------------------------------------------------------------------------------------------------------------------|
| `mariadb_database`  |               | If specified, create the specified database.                                                                                        |
| `mariadb_hardening` | true          | If `true`, run hardening role from Dev-Sec.                                                                                         |
| `mariadb_password`  |               | If specified, use this password for the `mariadb_user` user.                                                                        |
| `mariadb_user`      |               | If specified, create the specified database user with the `mariadb_password` and give it access to the `mariadb_database` database. |

## Example Playbook

```yaml
---
- hosts: all
  become: true
  collections:
    - jgoutin.home
  roles:
    - mariadb
```

## System upgrade

The database may require to be updated on system upgrade. Read the MariaDB
documentation for more information.
