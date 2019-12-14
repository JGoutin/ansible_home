# Mail Ansible Role

**Warning: This role is in early work in progress state**

## Description

Install a mail server using [Postfix](http://www.postfix.org/) and [Dovecot](https://www.dovecot.org/).

### Features

* Postfix & Dovecot installation
* TLS enabled secure configuration

## dependencies

* common

## Variables

| Name           | Default Value | Description                        |
| -------------- | ------------- | -----------------------------------|
| `mail_domain`| local | The mail domain to configure.
| `mail_firewalld_zone`| local | The mail domain to configure.
| `mail_protocol_imap`| true | If t`true` enable the IMAP mail protocol (143/tcp 993/tcp).
| `mail_protocol_lmtp`| false | If t`true` enable the LMTP mail protocol.
| `mail_protocol_pop3`| false | If t`true` enable the POP3 mail protocol (110/tcp 995/tcp).
| `mail_protocol_smtp`| true | If t`true` enable the SMTP mail protocol (25/tcp 465/tcp).
| `mail_protocol_submission`| true | If t`true` enable the SMTP-Submission mail protocol (587/tcp).
| `mail_tls_certificate`| | If specified, configure TLS using the specified certificate (That must include root CA and intermediates).
| `mail_tls_certificate_key`| | If specified, configure TLS using the specified private key.
| `mail_trusted_clients`| | If specified, configure Firewalld to restrict the server access to client that are in the specified list of source CIDR (`[192.168.1.10/32]`, `[192.168.1.0/24]`, ...).

## Example Playbook

```yaml
- hosts: localhost
  roles:
    - mail
```

## Work in progress / planned

* Postfix configuration
* Dovecot configuration
* Firewall configuration
* Allow/disallow unsecure protocols
* Tests
