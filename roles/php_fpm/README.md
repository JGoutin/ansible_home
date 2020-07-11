# PHP-FPM Ansible Role

![Ansible Role: "jgoutin.home.php_fpm"](https://github.com/JGoutin/ansible_home/workflows/Ansible%20Role:%20%22jgoutin.home.php_fpm%22/badge.svg)

## Description

This role installs a [PHP-FPM](https://php-fpm.org) server.

### Features

* Installation with PHP modules
* Unix socket based configuration
* Enable OPCache and allow memory limit configuration
* Hide PHP version to clients
* Default site configuration clean up
    
## Dependencies

*None*

## Variables

### Optional

| Name           | Default Value | Description                        |
| -------------- | ------------- | -----------------------------------|
| `php_fpm_group`| `nginx` | Unix group that will access to PHP-FPM.
| `php_fpm_user`| `nginx` | Unix user that will access to PHP-FPM.
| `php_fpm_site`| `site` | Site name.
| `php_memory_limit`| `128M` | PHP memory limit.
| `php_modules`| [] | PHP modules to install (Fedora packages names without `php-`, example: [`apcu`, `pgsql`]).

## Example Playbook

```yaml
---
- hosts: all
  become: true
  collections:
    - jgoutin.home
  roles:
    - php_fpm
```
