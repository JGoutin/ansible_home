# Mail Ansible Role

![Ansible Role: "jgoutin.home.mail"](https://github.com/JGoutin/ansible_home/workflows/Ansible%20Role:%20%22jgoutin.home.mail%22/badge.svg)

## Description

This role installs a mail server using [Postfix](http://www.postfix.org/) and
[Dovecot](https://www.dovecot.org/).

The aim is to provide a simple mail server to use on a local network for
administration mails (Logs and other notifications from servers).

### Features

* Postfix & Dovecot installation
* Default to IMAPS, SMTPS and SMTP-Submission protocols enabled, but also
  support SMTP, IMAP, POP3 and POP3S
* Authentication using OS users
* [Mozilla TLS Configuration](https://ssl-config.mozilla.org)
* Fail2ban configuration

## Dependencies

### OS recommendation

* "Fedora minimal" is recommended. 
* "Fedora server" is recommended if its extra features are required.

### Roles

* common

All variables from the `common` role that start by `common_mail_` must not
be used when using this role.

## Variables

### Mandatory

| Name           | Default Value | Description                        |
| -------------- | ------------- | -----------------------------------|
| `mail_domain`| local | The mail domain to configure.

### Optional

| Name           | Default Value | Description                        |
| -------------- | ------------- | -----------------------------------|
| `mail_firewalld_readers_source` | | If specified, restrict the IMAP/IMAPS/POP3/POP3S access to the specified source in CIDR notation (`192.168.1.10/32`, `192.168.1.0/24`, ...). By default, allow all using `public` zone. Exclusive with `mail_firewalld_readers_zone` parameter.
| `mail_firewalld_readers_zone` | | If specified, the existing firewalld zone where allow IMAP/IMAPS/POP3/POP3S access. By default, use `public` zone. Exclusive with `mail_firewalld_readers_source` parameter.
| `mail_firewalld_senders_source` | | If specified, restrict the SMTP/SMTPS/SMTP-Submission access to the specified source in CIDR notation (`192.168.1.10/32`, `192.168.1.0/24`, ...). By default, allow all using `public` zone. Exclusive with `mail_firewalld_senders_zone` parameter.
| `mail_firewalld_senders_zone` | | If specified, the existing firewalld zone where allow SMTP/SMTPS/SMTP-Submission access. By default, use `public` zone. Exclusive with `mail_firewalld_senders_source` parameter.
| `mail_inet_protocols`| `ipv4` | Postfix supported network protocols. `all` to enable IPv6 support.
| `mail_protocol_imap`| false | If `true` enable IMAP on port 143/tcp with STARTTLS supported. Not recommended.
| `mail_protocol_imaps`| true | If `true` enable IMAPS on port 993/tcp with TLS enabled.
| `mail_protocol_pop3`| false | If `true` enable POP3 on port 110/tcp with STARTTLS supported. Not recommended.
| `mail_protocol_pop3s`| false | If `true` enable POP3S on port 995/tcp with TLS enabled.
| `mail_protocol_smtp`| false | If `true` enable SMTP on port 25/tcp with STARTTLS supported. Not recommended.
| `mail_protocol_smtps`| true | If `true` enable SMTPS on port 465/tcp with TLS enabled.
| `mail_protocol_submission`| true | If `true` enable SMTP-Submission on port 587/tcp with STARTTLS enabled.
| `mail_tls_certificate`| | If specified, configure TLS using the specified certificate (That must include root CA and intermediates).
| `mail_tls_certificate_key`| | If specified, configure TLS using the specified private key.
| `mail_trusted_clients`| | If specified, configure mail services to restrict the server access to client that are in the specified list of source CIDR (`[192.168.1.10/32]`, `[192.168.1.0/24]`, ...).
| `mail_users`| | If specified, creates specified mail users. Must be a list of mappings (one per user) with keys: `name` (User name), `password` (User hashed password. Can be generated using `mkpasswd --method=sha-512`).
| `mail_users_aliases` | | If specified, set user aliases. Must be a list of mapping with `user` and `alias` keys.

If `mail_tls_certificate` and `mail_tls_certificate_key` variables are not set,
a self signed certificate is used (***Warning:** Self signed certificates are
only suitable for testing and should not be used on a publicly accessible
server.*)

## Example Playbook

```yaml
---
- hosts: all
  become: true
  collections:
    - jgoutin.home
  roles:
    - common
    - mail
  vars:
    mail_domain: local
```
