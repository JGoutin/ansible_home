# Common Ansible Role

## Description

This role initializes a new host by performing some common configuration tasks.

### Features

* SSH authorized key setting
* SSH Firewall admin restriction
* Fail2ban installation
* Admin user password setting
* NTP client configuration
* Grub timeout setting
* DNF speed up
* DNF auto-updates (With auto-restart)
* NFS share set up
* CIFS/SMB share set up
* OS and SSH hardening

## Dependencies

### Roles

* [dev-sec.os-hardening](https://galaxy.ansible.com/dev-sec/os-hardening)
* [dev-sec.ssh-hardening](https://galaxy.ansible.com/dev-sec/ssh-hardening)

## Variables

### Optional

| Name           | Default Value | Description                        |
| -------------- | ------------- | -----------------------------------|
| `common_admin_password`| | If specified, Set this password to the current remote user. (Must be a hashed password. Can be generated using `mkpasswd --method=sha-512`)
| `common_dnf_automatic_restart`| true | If `true`, restart the host if required when performing DNF automatic updates.
| `common_dnf_install_weak_deps`| false | If `"true"`, configure DNF to install weak dependencies.
| `common_dnf_keepcache`| false | If `"true"`, configure DNF to keep the package cache.
| `common_grub_timeout`| 1 | Grub timeout to set.
| `common_nfs_mount`| | If specified, mount specified NFS shares. Must be a list of mapping (one per share to mount) with keys: `path` (mount point path), `src` (share to mount), `opts` (optional, mount options, see fstab(5)), `owner` (optional, user owning the mount), `group` (optional, group owning the mount), `mode` (optional, permission mode) , `state` (optional, `present` if require to only add it to `/etc/fstab` without applying it now).
| `common_ntp_server`| | If specified, configure Chrony to use the specified NTP server.
| `common_os_hardening`| true | If `true`, run OS hardening role from Dev-Sec.
| `common_postfix_inet_protocols`| `ipv4` | Postfix Inet protocols, set to `all` to enable IPv6.
| `common_root_mail`| | If specified, configure redirect all root mails to the specified email address.
| `common_smb_mount`| | If specified, mount specified CIFS/SMB shares. The value format is identical to `common_nfs_mount`.
| `common_ssh_authorized_key`| | If specified, add the specified SSH public key to `~/.ssh/authorized_keys`. (A key can be generated using `ssh-keygen -t ed25519`)
| `common_ssh_hardening`| true | If `true`, run SSH hardening role from Dev-Sec.
| `common_trusted_firewalld_source`| | If specified, configure Firewalld to authorize SSH access only from the specified source in CIDR notation (`192.168.1.10/32`, `192.168.1.0/24`, ...). 

## Example Playbook

```yaml
---
- hosts: all
  become: true
  roles:
    - name: jgoutin.home.common
  vars:
    common_ssh_authorized_key: ssh-ed25519 XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    common_ntp_server: 192.168.1.1
    common_trusted_firewalld_source: 192.168.1.10/32
```

## Work in progress / planned

* Admin mail redirection
* Mails alert (Fail2ban, auditd, DNF automatic, user connexion)
* `/tmp` as TMPFS
* CI
