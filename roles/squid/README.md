# Squid Ansible Role

![Ansible Role: "jgoutin.home.squid"](https://github.com/JGoutin/ansible_home/workflows/Ansible%20Role:%20%22jgoutin.home.squid%22/badge.svg)

## Description

This role installs a [Squid](https://www.squid-cache.org) caching proxy.

This proxy allow to speed up internet connection and save bandwidth.

**Warning:** Pay attention when using the SSL Bump option because it can lead to 
security and privacy issues on your network. With this option, it is recommended 
to restrict the use of the proxy to limited usage like packages updates and avoid using
it as a transparent proxy on your full network or from users browsers. The CA used 
should be dedicated to Squid only.

### Features

* Install and configure Squid as a caching proxy.
* Configured to cache both HTTP and HTTPS requests (With SSL bump feature).
* Preconfigured to cache Fedora RPM repositories and optimize the hit ratio of mirrored
  repositories.
* TLS modern security configuration.
* Firewall configuration.

## Dependencies

### OS recommendation

* "Fedora minimal" is recommended. 
* "Fedora server" is recommended if its additional functionalities are required.

### Roles

* common

## Variables

### Optional

| Name           | Default Value | Description                        |
| -------------- | ------------- | -----------------------------------|
| `squid_cache_dir`| `"/var/spool/squid"` | Path to the squid cache directory.
| `squid_cache_dir_size`| 4096 | Size in MB of the squid cache directory. If using a full disk drive, does not exceed 80% of the size of the drive.
| `squid_firewalld_source` | | If specified, restrict the proxy access to the specified source in CIDR notation (`192.168.1.10/32`, `192.168.1.0/24`, ...). By default, allow all using `public` zone. Exclusive with `squid_firewalld_zone` parameter.
| `squid_firewalld_zone` | | If specified, the existing firewalld zone where allow proxy access. By default, use `public` zone. Exclusive with `squid_firewalld_source` parameter.
| `squid_http_access_all`| false | If `true`, configure Squid to accept connection from everywhere, else it is restricted to the local network.
| `squid_http_port`| 3128 | Squid HTTP proxy port number.
| `squid_maximum_object_size`| 1024 | Maximum size in MB of objets cached by Squid.
| `squid_refresh_patterns`| [] | Squid `refresh_pattern` directives to add to the Squid configuration file. Example value `["refresh_pattern -i .zip$ 10080 100% 43200"]`
| `squid_ssl_bump_ca`| | If specified, enable SSL bumb with the specified root CA. The certificate must be in PEM format and contain both the private key and the certificate. The certificate of this CA (Without the private key) need to be added to the clients root CA trust store.

It is also recommended setting the `common_dnf_proxy` variable from the 
[**common**](common.md) role to `http://127.0.0.1:<squid_http_port>`. Doing this will 
make DNF on the Squid host using the caching proxy. The root CA certificate can be
configured using `common_dnf_sslcacert`.

## Example Playbook

```yaml
---
- hosts: all
  become: true
  collections:
    - jgoutin.home
  roles:
    - common
    - squid
  vars:
    # Set the cache size
    squid_cache_dir_size: 40960

    # Enable SSL bump
    squid_ssl_bump_ca: squiq_ca_key_and_cert.pem

    # Use itself as proxy for DNF
    common_dnf_proxy: http://127.0.0.1:3128
    common_dnf_sslcacert: squid_ca_cert_only.crt
```

## Configuring RPM hit ratio optimization for more repositories

The hit ratio optimization will be automatically configured for any DNF repository 
installed on the Squid host.

Repositories that does not use mirrors (with `metalink`/`mirrorlist` options) or that
only have a single mirror does not require to be optimized and will be properly cached
natively.

To add the support of a new repository, simply install it the squid host.

To add the support of RPMfusion repositories , simply use the 
[**rpmfusion**](rpmfusion.md) role with `rpmfusion_free` & `rpmfusion_nonfree` variables
set to `true`.

The Squid mirror configuration is updated each day, but it is possible to force update 
with `sudo systemctl start squid_dnf_mirrors`.

## Configuring other machines to use the Squid proxy

### Configuring DNF to use the proxy

If your machine is managed with Ansible and the [**common**](common.md) role, simply
set the `common_dnf_proxy` variable on the machine playbook to 
`http://<squid-host-ip-or-hostname>:<squid_http_port>`.

If you enabled the `squid_ssl_bump_ca` feature, you also need to add the CA certificate
(Without the private key) to the `common_dnf_sslcacert` variable.

Then, apply the playbook.

It is also possible to configure DNF manually by adding the line 
`proxy=http://<squid-host-ip-or-hostname>:<squid_http_port>` to the DNF configuration 
file (`/etc/dnf/dnf.conf`). The SSL bump CA certificate can be configured by adding the
`sslcacert=path_to_squid_ca_cert_only.crt` line.

It is also possible to enable the CA certificate at system wide level. This can be 
useful is the proxy is not used only by DNF. But can also be less secure.
