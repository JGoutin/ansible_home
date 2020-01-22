# MPD Ansible Role

## Description

This role install a [Music Player Daemon](https://www.musicpd.org/) server.

### Features

* MPD Installation and Configuration.
* MPD user and password configuration.
* SELinux configuration.
* Ensure Alsa device is unmuted on MPD start.
* Start MPD as Socket service.
* Firewall configuration.

## dependencies

* common

## Variables

| Name           | Default Value | Description                        |
| -------------- | ------------- | -----------------------------------|
| `mpd_alsa_unmute`| | If specified, ensure the specified mixer control is unmuted before starting MPD.
| `mpd_audio_output`| type	 "alsa" \n name "ALSA Device" | The MPD audio output using [MPD audio output format](https://www.musicpd.org/doc/html/user.html#config-audio-output).
| `mpd_auto_update`| true | If `true`, enable auto-updates of the MPD database.
| `mpd_default_permissions`| read,add,control,admin | The permission of the default unauthenticated user.
| `mpd_firewalld_source`| | If specified, restrict the MPD access to the specified source in CIDR notation (`192.168.1.10/32`, `192.168.1.0/24`, ...). By default, allow all machines from the current local network.
| `mpd_input_cache`| | If specified, use the specified input cache. Must be formatted using [MPD input cache size format](https://www.musicpd.org/doc/html/user.html#configuring-the-input-cache) (Example: `"1 GB"`).
| `mpd_music_directory`| /var/lib/mpd/music | MPD music directory, can also be a share with specific scheme like `nfs://`, `smb://`, ...
| `mpd_passwords`| | If specified, set the specified list of passwords and access rights. Must be formatted using [MPD password format](https://www.musicpd.org/doc/html/user.html#permissions-and-passwords).
| `mpd_update`| true | If `true`, update the MPD database after installation.
| `mpd_replaygain`| auto | Replay gain mode to use.
| `mpd_use_cifs`| false | If `true`, configure SELinux to allow MPT to access to CIFS/SMB shares.
| `mpd_use_nfs`| false | If `true`, configure SELinux to allow MPT to access to NFS shares.
| `mpd_zeroconf`| false | If `true`, enable Zeroconf/mDNS.

## Example Playbook

```yaml
- hosts: localhost
  roles:
    - name: mpd
      vars:
        mpd_passwords:
          - my_password@read,add,control,admin
        mpd_default_permissions: read
        mpd_alsa_unmute: Master
        mpd_audio_output: |
           type            "alsa"
           name            "My sound card"
           device          "default:CARD=II"
           mixer_control   "Master"
```

## Work in progress / planned

* Tests