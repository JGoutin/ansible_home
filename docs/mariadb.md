# MariaDB Ansible Role

![Ansible Role: "jgoutin.home.mariadb"](https://github.com/JGoutin/ansible_home/workflows/Ansible%20Role:%20%22jgoutin.home.mariadb%22/badge.svg)

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
  force_handlers: true  # See known issues
  collections:
    - jgoutin.home
  roles:
    - mariadb
```

## System upgrade

The database may require to be updated on system upgrade. Read the MariaDB
documentation for more information.

## Known issues

### Ansible dependencies are not cleaned on failure

Some modules and sub-roles of this role require to install some packages on
the host to work. Since these packages are not required once the Ansible play is
done, this role provides handlers to clean up these packages.

In case of failure during the Ansible play, handlers are not applied and
packages are not cleaned up.

To avoid this issue and ensure the clean up is performed, add 
`force_handlers: true` in the playbook.
