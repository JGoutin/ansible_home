# PostgreSQL Ansible Role

![Ansible Role: "jgoutin.home.postgresql"](https://github.com/JGoutin/ansible_home/workflows/Ansible%20Role:%20%22jgoutin.home.postgresql%22/badge.svg)

## Description

This role installs a [PostgreSQL](https://www.postgresql.org) database.

### Features

Configuration:
* Binds to an Unix socket.
* Initializes the database.
  
Security:
* Runs unprivileged in a Systemd sandbox.
* Works with SElinux enforced.

## Dependencies

*None*

## Variables

### Optional

| Name           | Default Value | Description                        |
| -------------- | ------------- | -----------------------------------|
| `postgresql_data`| `/var/lib/pgsql` | Path to the database. A `data` subdirectory is created inside this directory.
| `postgresql_database`| | If specified, creates a database with this name.
| `postgresql_upgrade`| true | If `true`, the role will upgrade and reindex the database if required.
| `postgresql_user`| | If specified, creates a database user with this name, must match a Unix user name.

## Example Playbook

```yaml
---
- hosts: all
  become: true
  force_handlers: true  # See known issues
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

## Known issues

### Ansible dependencies are not cleaned on failure

Some modules and sub-roles of this role require to install some packages on
the host to work. Since these packages are not required once the Ansible play is
done, this role provides handlers to clean up these packages.

In case of failure during the Ansible play, handlers are not applied and
packages are not cleaned up.

To avoid this issue and ensure the clean up is performed, add 
`force_handlers: true` in the playbook.
