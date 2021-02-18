# Nginx Ansible Role

![Ansible Role: "jgoutin.home.nginx"](https://github.com/JGoutin/ansible_home/workflows/Ansible%20Role:%20%22jgoutin.home.nginx%22/badge.svg)

## Description

This role installs a [Nginx](https://nginx.org) web server.

### Features

Configuration:
* Easily includes the site specific configuration.
* Sets up TLS certificate (or generates self-signed certificate).
* Optionally, sets SELinux boolean according the application needs.
* Supports PHP-FPM.
* Cleans up the default site.

Security:
* Uses [modern TLS configuration from Mozilla](https://ssl-config.mozilla.org/#server=nginx&config=modern).
* Provides HTTP to HTTPS redirection by default.
* Adds recommended security HTTP headers.
* Runs fully unprivileged in a Systemd sandbox.
* Works with SElinux enforced.
* Hides the server version.
* Restricts accesses using firewall.
* Applies extra hardening using [DevSec role](https://dev-sec.io/baselines/nginx).

## Variables

### Mandatory

| Name           | Default Value | Description                        |
| -------------- | ------------- | -----------------------------------|
| `nginx_server_name` | | Server domain name.
| `nginx_site` | | Name of the site.
| `nginx_site_conf` | | Site specific configuration to insert into Nginx configuration. The content is inserted in the `server` section of the generated site `.conf` file.
| `nginx_site_user` | | Unix user used to run the site application.

### Optional

| Name           | Default Value | Description                        |
| -------------- | ------------- | -----------------------------------|
| `nginx_can_connect_ldap` | false | If `true`, configure SELinux to allow Nginx to access to LDAP.
| `nginx_can_network_connect` | false | If `true`, configure SELinux to allow Nginx to access to the network.
| `nginx_can_network_connect_db` | false | If `true`, configure SELinux to allow Nginx to access to a database.
| `nginx_can_network_memcache` | false | If `true`, configure SELinux to allow Nginx to access to a memcache.
| `nginx_can_sendmail` | false | If `true`, configure SELinux to allow Nginx to send emails.
| `nginx_can_use_cifs` | false | If `true`, configure SELinux to allow Nginx to access to CIFS/SMB shares.
| `nginx_can_use_fusefs` | false | If `true`, configure SELinux to allow Nginx to access to FUSE filesystems.
| `nginx_can_use_gpg` | false | If `true`, configure SELinux to allow Nginx to use GPG.
| `nginx_domain_can_mmap_files` | false | If `true`, configure SELinux to allow memory map files.
| `nginx_hardening` | false | If `true`, run hardening role from Dev-Sec.
| `nginx_firewalld_source` | | If specified, restrict the HTTP/HTTPS access to the specified sources list in CIDR notation (`["192.168.1.10/32", "192.168.1.0/24", "2001:db8:1234:5678::/64"]`, ...). By default, allow all using `public` zone. Exclusive with `nginx_firewalld_zone` parameter.
| `nginx_firewalld_zone` | | If specified, the existing firewalld zone where allow HTTP/HTTPS access. By default, use `public` zone. Exclusive with `nginx_firewalld_source` parameter.
| `nginx_inaccessible_paths`| | Space separated list of absolutes paths to make inaccessible from the Nginx service.
| `nginx_php_fpm`| false | If `true`, configure Nginx for PHP-FPM (See `php-pfm` role).
| `nginx_read_user_content` | false | If `true`, configure SELinux to allow Nginx to read user content.
| `nginx_resolver` | `127.0.0.1` | Nginx resolver.
| `nginx_security_header_content_security_policy` | false | If `true`, add the `Content-Security-Policy` HTTP header with the value set in `nginx_security_header_content_security_policy_value`.
| `nginx_security_header_content_security_policy_value` | `script-src 'self'` | Value of the `Content-Security-Policy` HTTP header set if `nginx_security_header_content_security_policy` is `true`.
| `nginx_security_header_feature_policy` | false | If `true`, add the `Feature-Policy` HTTP header with the value set in `nginx_security_header_feature_policy_value`. 
| `nginx_security_header_feature_policy_value` | `geolocation none; midi none; notifications none; push none; sync-xhr none; microphone none; camera none; magnetometer none; gyroscope none; speaker self; vibrate none; fullscreen self; payment none;` | Value of the `Feature-Policy` HTTP header set if `nginx_security_header_feature_policy` is `true`. note that `Feature-Policy` is deprecated and should be replaced by `Permission-Policy`.
| `nginx_security_header_permission_policy` | false | If `true`, add the `Permissions-Policy` HTTP header with the value set in `nginx_security_header_permission_policy_value`. 
| `nginx_security_header_permission_policy_value` | `geolocation(), midi(), notifications(), push(), sync-xhr(), microphone(), camera(), magnetometer(), gyroscope(), speaker(), vibrate(), fullscreen(), payment()"` | Value of the `Permissions-Policy` HTTP header set if `nginx_security_header_feature_policy` is `true`.
| `nginx_security_header_public_key_pins` | false | If `true`, add the `Public-Key-Pins` HTTP header to enable HTTP Public Key Pinning.
| `nginx_security_header_public_key_pins_backup_pins` | [] | List of SHA256 base64 digests of certificates to add as backup HTTP Public Key Pinning.
| `nginx_security_header_public_key_pins_max_age` | 2592000 | Age in seconds of the HTTP Public Key Pinning.
| `nginx_security_header_referrer_policy` | true | If `true`, add the `Referrer-Policy` HTTP header to disable referer.
| `nginx_security_header_x_content_type_options` | true | If `true`, add the `X-Content-Type-Options` HTTP header to mitigate MIME-sniffing attacks.
| `nginx_security_header_x_download_options` | true | If `true`, add the `X-Download-Options` HTTP header to mitigate MIME-sniffing attacks.
| `nginx_security_header_x_frame_options` | true | If `true`, add the `X-Frame-Options` HTTP header to mitigate clickjacking attacks.
| `nginx_security_header_x_permitted_cross_domain_policies` | true | If `true`, add the `X-Permitted-Cross-Domain-Policies` HTTP header to disallow cross domain policy.
| `nginx_security_header_x_robots_tag` | true | If `true`, add the `X-Robots-Tag` HTTP header and a `robot.txt` file to disable crawlers indexations.
| `nginx_security_header_x_xss_protection` | true | If `true`, add the `X-XSS-Protection` HTTP header to mitigate cross site scripting attacks.
| `nginx_site_conf` | | Path to a Jinja template file that contains the site specific Nginx configuration. This template will be evaluated and inserted inside the `server` section of the configuration.
| `nginx_ssl_certificate`| | Path to the TLS certificate associated to the `nginx_server_name` domain.
| `nginx_ssl_certificate_key`| | Path to the TLS private key associated to the `nginx_server_name` domain.
| `nginx_ssl_trusted_certificate`| | Path to the TLS certificate chain (root + intermediates) associated to the `nginx_server_name` domain.
| `nginx_unified` | false | If `true`, configure SELinux to allow unified handling of all content files.

If `nginx_ssl_certificate`, `nginx_ssl_certificate_key` and
`nginx_ssl_trusted_certificate` variables are not set, a self signed certificate
is used (***Warning:** Self signed certificates are only suitable for testing
and should not be used on a publicly accessible server.*)

## Example Playbook

```yaml
---
- hosts: all
  become: true
  collections:
    - jgoutin.home
  roles:
    - nginx
```
