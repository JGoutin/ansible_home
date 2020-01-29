# MariaDB Ansible Role

## Description

This role installs a [MariaDB](https://mariadb.org) database

### Features

* Database setting
* Database user setting
* Hardening

## Dependencies

### Roles

* [dev-sec.mysql-hardening](https://galaxy.ansible.com/dev-sec/mysql-hardening)

## Variables

### Optional

| Name           | Default Value | Description                        |
| -------------- | ------------- | -----------------------------------|
| `mariadb_database`| | If specified, create the specified database.
| `mariadb_hardening`| true | If `true`, run hardening role from Dev-Sec.
| `mariadb_password`| | If specified, use this password for the `mariadb_user` user.
| `mariadb_user`| | If specified, create the specified database user with the `mariadb_password` and give it access to the `mariadb_database` database.

## Example Playbook

```yaml
---
- hosts: all
  become: true
  roles:
    - jgoutin.home.mariadb
```

## Work in progress / planned

* Tests
