# Nextcloud Ansible Role

## Description

This role installs a [Nextcloud](https://nextcloud.com) server.

### Features

* Nextcloud Installation and full configuration
* Applications and related dependencies installation (PHP modules, ClamAV)
* Custom applications and configuration set up
* Auto-updates systemd service for Nextcloud and Nextcloud applications
* SELinux enforced and strict Unix permission setting
* Nginx/PostgreSQL based backend
* Redis & APCu caching enabled
* Unix socket based backend communication 
* `OCC` command Bash auto-completion
* Easy setup of hardened security features like 2FA

Also look to the Nginx role for more information on the web server configuration.

### Limitations

This role is mainly intended and optimized to run Nextcloud as a single server.
It does not yet support to run PostgreSQL or Redis on another machine to create a scalable infrastructure.

## Dependencies

### OS recommendation

* "Fedora minimal" is recommended. 
* "Fedora server" is recommended if its additional functionalities are required.

### Roles

* common

## Variables

### Mandatory

| Name           | Default Value | Description                        |
| -------------- | ------------- | -----------------------------------|
| `nextcloud_admin_password`| | Password of the Nexctloud administrator user.
| `nextcloud_domain`| | Domain name of the Nextcloud server.

### Optional

| Name           | Default Value | Description                        |
| -------------- | ------------- | -----------------------------------|
| `nextcloud_admin_user`| `nextcloud` | Name of the Nexctloud administrator user.
| `nextcloud_applications`| [`bruteforcesettings`, `calendar`, `contacts`, `deck`, `maps`, `news`, `notes`, `spreed`, `tasks`, `twofactor_totp`,  `twofactor_u2f`] | Install the specified list of Nextcloud applications. Default to a list of official applications.
| `nextcloud_applications_config` | [] | Application configuration to set. mapping of `name`, `value` and `type`. Possible values for type: `string` (Default if unspecified) `boolean`, `integer`, `float`.
| `nextcloud_enable_encryption`| false | If `true`, enable Nextcloud encryption.
| `nextcloud_enable_antivirus`| false | If `true`, enable antivirus scan using ClamAV.
| `nextcloud_enable_external_storage`| false | If `true`, install the external storage application and configure related SELinux permissions.
| `nextcloud_enable_mail`| false | If `true`, install the mail application and configure related SELinux permissions.
| `nextcloud_enable_ldap`| false | If `true`, install the LDAP application and configure related SELinux permissions.
| `nextcloud_enable_audit`| false | If `true`, install the Audit application and configure related SELinux permissions.
| `nextcloud_system_config` | [] | System configuration to set. mapping of `name`, `value` and `type`. Possible values for type: `string` (Default if unspecified) `boolean`, `integer`, `float`.
| `nextcloud_token_auth_enforced`| false | If `true`, enforce token authentication with Nextcloud client to improve security.
| `nextcloud_twofactor_enforced`| false | If `"true"`, enforce two factor authentication to improve security.

It is also possible to set following variables from the [**nginx**](nginx.md) role:

| Name           | Default Value | Description                        |
| -------------- | ------------- | -----------------------------------|
| `nginx_firewalld_source` | | If specified, restrict the HTTP/HTTPS access to the specified source in CIDR notation (`192.168.1.10/32`, `192.168.1.0/24`, ...). By default, allow all.
| `nginx_ssl_certificate`| | Path to the TLS certificate associated to the `nextcloud_domain` domain.
| `nginx_ssl_certificate_key`| | Path to the TLS private key associated to the `nextcloud_domain` domain.
| `nginx_ssl_trusted_certificate`| | Path to the TLS certificate chain (root + intermediates) associated to the `nextcloud_domain` domain.

If `nginx_ssl_certificate`, `nginx_ssl_certificate_key` and `nginx_ssl_trusted_certificate` variables are not set, a self signed certificate is used (***Warning:** Self signed certificates are only suitable for testing and should not be used on a publicly accessible server.*)

It is also recommended to look at the [**common**](common.md) role variables to customize the server OS (SSH, NTP, Firewall, and more).

## Example Playbook

```yaml
---
- hosts: all
  become: true
  roles:
    - jgoutin.home.common
    - jgoutin.home.nextcloud
  vars:
    nextcloud_domain: my_nextcloud.com
    nextcloud_admin_password: my_password
    nginx_ssl_certificate: my_nextcloud_cert.crt
    nginx_ssl_certificate_key: my_nextcloud_cert.key
    nginx_ssl_trusted_certificate: root_and_intermediates.crt
```

## Work in progress / planned

* LibreOffice online / CollaboraOnline
* Encryption keys back-up/recovery
* `config.php` back-up/recovery
* CI
