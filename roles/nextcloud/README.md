# Nextcloud Ansible Role

![Ansible Role: "jgoutin.home.nextcloud"](https://github.com/JGoutin/ansible_home/workflows/Ansible%20Role:%20%22jgoutin.home.nextcloud%22/badge.svg)

## Description

This role installs a [Nextcloud](https://nextcloud.com) server.

### Features

Configuration:
* Fully installs and configures Nextcloud.
* Installs Nextcloud applications and related dependencies (PHP modules, ClamAV).
* Provides variables to easily configure Nextcloud options.
* Provides mail configuration (With default to the system mail server).
* Auto-updates Nextcloud and Nextcloud applications using a dedicated service.
* Configures Redis & APCu cache.
* Provides `occ` command Bash auto-completion.
* Configures Nextcloud Cron using a dedicated service.
* Uses Nginx and PostgreSQL as backend.
* Uses Unix sockets only for backend communication.

Security:
* Provides variables to easily enable Nextcloud hardened security features like 2FA.
* Uses [modern TLS configuration from Mozilla](https://ssl-config.mozilla.org/#server=nginx&config=modern).
* Provides HTTP to HTTPS redirection by default.
* Adds recommended security HTTP headers.
* Optionally, restricts accesses using firewall.
* Runs related services sandboxed and unprivileged.
* Works with SElinux enforced.
* Enables Fail2ban jail.

Also look to the [**nginx**](../nginx/README.md) role for more information on the web
server configuration.

### Limitations

This role is mainly intended and optimized to run Nextcloud as a single server.
It does not yet support to run PostgreSQL or Redis on another machine to create
a scalable infrastructure.

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
| `nextcloud_allow_web_update`| false | If `true`, allow Nextcloud and applications updates/installation from the web interface. Else only allow update from the `occ` command line utility.
| `nextcloud_applications`| [`admin_audit`, `calendar`, `circles`, `contacts`, `deck`, `encryption`, `files_accesscontrol`, `files_antivirus`, `files_automatedtagging`, `files_external`, `files_retention`, `groupfolders`, `mail`, `maps`, `notes`, `spreed`, `tasks`, `twofactor_totp`, `twofactor_u2f`] | Install the specified list of Nextcloud applications. Default to Nextcloud Hub applications and some common applications.
| `nextcloud_applications_config` | [] | Application configuration to set. mapping of `name`, `value` and `type`. Possible values for type: `string` (Default if unspecified) `boolean`, `integer`, `float`.
| `nextcloud_country_code`| | ISO 3166-1 country codes such as `DE` for Germany, `FR` for France, …
| `nextcloud_smtp_authtype`| `LOGIN` | SMTP authentication mode. Possibles values are `PLAIN` or `LOGIN`.
| `nextcloud_smtp_domain`| | Domain mail sending the Email. Default to `nextcloud_domain` value.
| `nextcloud_smtp_from`| `no-reply` | Username sending the Email.
| `nextcloud_smtp_host`| 127.0.0.1 | SMTP server host. Default to system SMTP relay server, see the [**common**](../common/README.md) role to configure it.
| `nextcloud_smtp_password`| | Password of the `nextcloud_smtp_user` user on the SMTP server.
| `nextcloud_smtp_port`| 25 | SMTP server port to use, can be: 25 (SMTP), 465 (SMTPS), 587 (SMTP-Submission).
| `nextcloud_smtp_secure`| `` | Security mode to use. Possible values are `ssl` (For SMTPS) or `tls` (for STARTTLS SMTP/SMTP-Submission).
| `nextcloud_smtp_user`| | User to authenticate on the SMTP server, if specified enable SMTP authentication.
| `nextcloud_system_config` | [] | System configuration to set. mapping of `name`, `value` and `type`. Possible values for type: `string` (Default if unspecified) `boolean`, `integer`, `float`.
| `nextcloud_token_auth_enforced`| true | If `true`, enforce token authentication with Nextcloud client to improve security.
| `nextcloud_twofactor_enforced`| false | If `true`, enforce two factor authentication to improve security.
| `nextcloud_upload_max_size`| `512M` | Maximum upload size. This should be lower than the maximum amount of memory.

It is also possible to set following variables from the [**nginx**](../nginx/README.md)
role:

| Name           | Default Value | Description                        |
| -------------- | ------------- | -----------------------------------|
| `nginx_firewalld_source` | | If specified, restrict the HTTP/HTTPS access to the specified source in CIDR notation (`192.168.1.10/32`, `192.168.1.0/24`, ...). By default, allow all.
| `nginx_ssl_certificate`| | Path to the TLS certificate associated to the `nextcloud_domain` domain.
| `nginx_ssl_certificate_key`| | Path to the TLS private key associated to the `nextcloud_domain` domain.
| `nginx_ssl_trusted_certificate`| | Path to the TLS certificate chain (root + intermediates) associated to the `nextcloud_domain` domain.

If `nginx_ssl_certificate`, `nginx_ssl_certificate_key` and
`nginx_ssl_trusted_certificate` variables are not set, a self signed certificate
is used (***Warning:** Self signed certificates are only suitable for testing
and should not be used on a publicly accessible server.*)

It is also recommended looking at the [**common**](../common/README.md) role variables
to customize the server OS (SSH, NTP, Firewall, and more).

## Example Playbook

```yaml
---
- hosts: all
  become: true
  force_handlers: true  # See known issues
  collections:
    - jgoutin.home
  roles:
    - common
    - nextcloud
  vars:
    nextcloud_domain: my_nextcloud.com
    nextcloud_admin_password: my_password
    nginx_ssl_certificate: my_nextcloud_cert.crt
    nginx_ssl_certificate_key: my_nextcloud_cert.key
    nginx_ssl_trusted_certificate: root_and_intermediates.crt
```

## Data to backup

Even is Ansible allow to easily rebuild the server the following data requires to pay
attention:

- `/var/www/nextcloud/config/config.php`: This file contains the whole Nextcloud
  configuration including the password salt. This file requires to be saved securely
  only once after running the role.
- `/var/lib/nextcloud`: This directory contains both the database and the data files.
  It requires regular backups to avoid data loss. Mounting this directory on a NAS
  volume or similar is recommended.

## System upgrade

The database may require to be updated on system upgrade.
See the [**postgresql**](../postgresql/README.md) role for more information.

## Known issues

### Ansible dependencies are not cleaned on failure

Some modules and sub-roles of this role require to install some packages on
the host to work. Since these packages are not required once the Ansible play is
done, this role provides handlers to clean up these packages.

In case of failure during the Ansible play, handlers are not applied and
packages are not cleaned up.

To avoid this issue and ensure the clean up is performed, add 
`force_handlers: true` in the playbook.
