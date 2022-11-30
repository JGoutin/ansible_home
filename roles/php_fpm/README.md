# PHP-FPM Ansible Role

![Ansible Role: "jgoutin.home.php_fpm"](https://github.com/JGoutin/ansible_home/workflows/Ansible%20Role:%20%22jgoutin.home.php_fpm%22/badge.svg)

## Description

This role installs a [PHP-FPM](https://php-fpm.org) server.

### Features

Configuration:
* Binds to a Unix socket.
* Installs the required PHP modules.
* Enables OPCache and allows memory limit configuration.
* Hides PHP version.
* Cleans up the default site.

Security:
* Runs in a Systemd sandbox with unprivileged workers.
* Works with SElinux enforced.
* Enables Fail2ban jails.

## Dependencies

*None*

## Variables

### Optional

| Name           | Default Value | Description                        |
| -------------- | ------------- | -----------------------------------|
| `php_fpm_group`| `nginx` | Unix group that will access to PHP-FPM.
| `php_fpm_inaccessible_paths`| | Space separated list of absolutes paths to make inaccessible from the PHP-FPM service.
| `php_fpm_user`| `nginx` | Unix user that will access to PHP-FPM.
| `php_fpm_site`| `site` | Site name.
| `php_memory_limit`| `128M` | PHP memory limit.
| `php_modules`| [] | PHP modules to install (Fedora packages names without `php-`, example: [`apcu`, `pgsql`]).
| `php_opcache_interned_strings_buffer`| `8` | The amount of memory used to store interned strings. Default to the default PHP value.
| `php_upload_max_filesize`| `2M` | PHP maximum upload size. Should be lower than `php_memory_limit`.

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
