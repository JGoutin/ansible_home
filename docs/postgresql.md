# PostgreSQL Ansible Role

![Ansible Role: "jgoutin.home.postgresql"](https://github.com/JGoutin/ansible_home/workflows/Ansible%20Role:%20%22jgoutin.home.postgresql%22/badge.svg)

## Description

This role installs a [PostgreSQL](https://www.postgresql.org) database.

### Features

* Installation & Initial configuration
* Unix socket based configuration
* Unix user permission setting
* Database setting
* Database user setting
    
## Dependencies

*None*

## Variables

### Optional

| Name           | Default Value | Description                        |
| -------------- | ------------- | -----------------------------------|
| `postgresql_data`| `/var/lib/pgsql/data` | Path to the database.
| `postgresql_database`| | If specified, creates a database with this name.
| `postgresql_user`| | If specified, creates a database user with this name, must match a Unix user name.

## Example Playbook

```yaml
---
- hosts: all
  become: true
  force_handlers: true  # See known issues
  roles:
    - jgoutin.home.postgresql
```

## Known issues

### Ansible dependencies are not cleaned on failure

Some modules and sub-roles of this role require to install some packages on
the host to work. Since these packages are not required once the Ansible play is
done, this role provides handlers to clean up these packages.

In case of failure during the Ansible play, handlers are not applied and
packages are not cleaned up.

To avoid this issue and ensure the clean up is performed, add 
`force_handlers: true` in the playbook.

## Work in progress / planned

* Fedora update: https://fedoraproject.org/wiki/Changes/PostgreSQL_12#User_Experience
