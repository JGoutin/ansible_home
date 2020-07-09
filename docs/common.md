# Common Ansible Role

![Ansible Role: "jgoutin.home.common"](https://github.com/JGoutin/ansible_home/workflows/Ansible%20Role:%20%22jgoutin.home.common%22/badge.svg)

## Description

This role initializes a new host by performing some common configuration tasks.

### Features

* SSH authorized key setting
* SSH Firewall admin restriction
* Fail2ban configuration
* Admin user password setting
* NTP client configuration
* Grub timeout setting
* DNF speed up
* DNF auto-updates (With auto-restart)
* NFS share set up
* CIFS/SMB share set up
* OS and SSH hardening
* `root` user mail redirection with SMTP relay on external server
* CA certificates installation

## Dependencies

### Roles

* [dev-sec.os-hardening](https://galaxy.ansible.com/dev-sec/os-hardening)
* [dev-sec.ssh-hardening](https://galaxy.ansible.com/dev-sec/ssh-hardening)

## Variables

### Optional

| Name           | Default Value | Description                        |
| -------------- | ------------- | -----------------------------------|
| `common_admin_password`| | If specified, Set this password to the current remote user. (Must be a hashed password. Can be generated using `mkpasswd --method=sha-512`)
| `common_ca_certificates`| | If specified, CA certificates to install in the system CA trust store. Must be a list of local path to PEM or DER formatted certificates.
| `common_dnf_automatic_restart`| true | If `true`, restart the host if required when performing DNF automatic updates.
| `common_dnf_install_weak_deps`| false | If `"true"`, configure DNF to install weak dependencies.
| `common_dnf_keepcache`| false | If `"true"`, configure DNF to keep the package cache.
| `common_fail2ban_action` | `%(action_mwl)s` | Fail2ban default action. By default, ban user and send mail with detailed logs to root.
| `common_grub_auto_hide`| false | If `true` configure Grub to auto-hide.
| `common_grub_hidden_timeout`| 0 | Grub hidden timeout to set.
| `common_grub_timeout`| 1 | Grub timeout to set.
| `common_mail_smtp_host`| | SMTP server host.
| `common_mail_smtp_inet_interfaces`| `127.0.0.1` | Interface from where accept SMTP requests. By default, localhost only. Only if `common_mail_smtp_host` is specified.
| `common_mail_smtp_password`| | Password of the `common_mail_relay_user` user on the SMTP server. Only if `common_mail_smtp_host` is specified.
| `common_mail_smtp_port`| 465 | SMTP server port to use, can be: 25 (SMTP), 465 (SMTPS), 587 (SMTP-Submission). Only if `common_mail_smtp_host` is specified.
| `common_mail_smtp_user`| | User to authenticate on the SMTP server, if specified enable SMTP authentication. Only if `common_mail_smtp_host` is specified.
| `common_mail_smtp_tls`| `TLS` | Security mode to use. Possible values are `TLS` (For SMTPS) or `STARTTLS` (for SMTP/SMTP-Submission).
| `common_mail_smtp_send_to`| | If specified, redirect all root mails to the specified email address.
| `common_nfs_mount`| | If specified, mount specified NFS shares. Must be a list of mapping (one per share to mount) with keys: `path` (mount point path), `src` (share to mount), `opts` (optional, mount options, see fstab(5)), `owner` (optional, user owning the mount), `group` (optional, group owning the mount), `mode` (optional, permission mode) , `state` (optional, `present` if require to only add it to `/etc/fstab` without applying it now).
| `common_ntp_server`| | If specified, configure Chrony to use the specified NTP server.
| `common_os_hardening`| true | If `true`, run OS hardening role from Dev-Sec.
| `common_smb_mount`| | If specified, mount specified CIFS/SMB shares. The value format is identical to `common_nfs_mount`.
| `common_ssh_authorized_key`| | If specified, add the specified SSH public key to `~/.ssh/authorized_keys`. (A key can be generated using `ssh-keygen -t ed25519`)
| `common_ssh_hardening`| true | If `true`, run SSH hardening role from Dev-Sec.
| `common_trusted_firewalld_source`| | If specified, configure Firewalld to authorize SSH access only from the specified source in CIDR notation (`192.168.1.10/32`, `192.168.1.0/24`, ...). 

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
  vars:
    common_ssh_authorized_key: ssh-ed25519 XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    common_ntp_server: 192.168.1.1
    common_trusted_firewalld_source: 192.168.1.10/32
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

### Failure with `common_admin_password` variable

When using the `common_admin_password` variable, the playbook may fail on the
first step that follow `Ensure current user password is set` with the message
`Incorrect sudo password`. 

In this case, simply re-run the playbook and enter the new password when asked 
by Ansible (`BECOME password`).

If the failure is an issue in complex playbook, do not use this variable to set
the password.

## Work in progress / planned

* Mails alert (auditd, DNF automatic, user connexion)
* `/tmp` as TMPFS
