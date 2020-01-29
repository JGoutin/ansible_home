# PostgreSQL Ansible Role

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
  roles:
    - jgoutin.home.postgresql
```

## Work in progress / planned

* Tests
