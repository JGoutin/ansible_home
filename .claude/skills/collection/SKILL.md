---
name: collection
description: Load before changing, testing or reviewing this Ansible collection (roles, CI, role scripts, the musicplayer serial display).
---

# jgoutin.home collection

Ansible collection `jgoutin.home` for Fedora servers and desktops, including Fedora Atomic (rpm-ostree) hosts. Roles
are in `roles/`, the Python role scripts' tests in `tests/python/`, the CI tools project in `.github/`.

This skill and every file under `.claude/skills/` are published with the repository: keep local environment details
(paths, accounts, private hosts) out of them and assume only a Fedora development machine with podman.

## Goals

The README sets three goals; weigh every change against them:

- Up-to-date, fully featured software: use the newest features the packaged versions support, such as TLS 1.3 with
  the `X25519MLKEM768` hybrid group first, HTTP/3, and the applications' own performance features.
- Security: hardened defaults, and stricter settings behind the hardening options. Give each service a role starts a
  systemd sandboxing drop-in and aim for an "OK" exposure in `systemd-analyze security <unit>`.
- Minimal maintenance: daily automatic updates and reboots must keep working, with no step left to a person.

When a role runs on a real host, also read what the host reports about it: `systemd-analyze security`, AVC denials
(`ausearch -m avc -ts this-week`), warnings in the journal since boot, the application's own checks (such as
Nextcloud's `occ setupchecks`) and the TLS group each listener negotiates (`openssl s_client`).

## Gates

Run them from the repository root before each commit; CI runs the same steps (`.github/workflows/lint.yml`).

```
uv sync -q --locked --project .github
export PATH="$PWD/.github/.venv/bin:$PATH"
ansible-lint
ruff check . && ruff format --check .
radon mi -n B .
PYTHONDONTWRITEBYTECODE=1 pytest -q -p no:cacheprovider tests/python
```

- The `schema[meta]` warning about Fedora versions in `meta/main.yml` is expected: ansible-lint's schema lags behind
  Fedora releases and `.ansible-lint` keeps it as a warning.
- Syntax-check roles as collection members, so `jgoutin.home.*` names resolve: create a temporary directory holding
  `ansible_collections/jgoutin/home` as a symlink to the repository root, set `ANSIBLE_COLLECTIONS_PATH` to it, then run
  `ansible-playbook --syntax-check` on a small playbook listing the roles.
- CI tools are locked in `.github/uv.lock` with `exclude-newer = "7 days"`; relock with `uv lock --project .github`.
  Python is pinned to the newest version ansible-core supports (`requires-python` in `.github/pyproject.toml`).
- A tag `X.Y.Z` publishes the collection to Ansible Galaxy and creates the GitHub release; `galaxy.yml` keeps
  `version: 0.0.0`, which the workflow replaces.

## Role conventions

- Leave packaged files untouched whenever the software reads a drop-in directory: write the role's settings in its
  own file there (`/etc/<name>/<name>.d/`, `conf.d/`, `/etc/systemd/system/<unit>.d/`, `/etc/sysctl.d/`, …).
- When a packaged file must be edited, start from the current packaged version: if `<file>.rpmnew` exists, copy it
  over the file before applying the role's edits, then remove the `.rpmnew` and `.rpmsave` files. Edit with targeted
  tasks (`lineinfile`, `ini_file`) rather than templating the whole file.
- Make every conditional change revertible: when an option is turned off or a variable unset, the role removes its
  files, restores the packaged setting and restarts or reloads the service, so the host returns to the packaged
  state.
- Revert only what the role owns, because most options are off by default and the role cannot tell its own past
  changes from a person's: files at paths the role chose, lines and settings it writes, firewalld zones it creates
  (with their sources reconciled against the variable), services and packages it adds only for that option. Never
  uninstall or stop software other roles or people may use (Netdata, a third-party repository): remove the role's
  configuration of it.
- Start each file the role writes at a path a person may also use (Netdata collectors, `stream.conf`, `pg_hba.conf`)
  with the comment `Managed by the jgoutin.home.<role> role`. A revert deletes such a file only when it carries that
  marker or matches exactly what an earlier role version wrote; otherwise it leaves the file alone.
- Restart a shared service that may be stopped on purpose or absent (Netdata) with `systemctl try-restart <unit>`,
  which leaves a stopped unit stopped, and accept its exit code 5 (unit not installed). Handlers that listen on the
  same topic in several roles all run in one play unless they share a name: give them the same name and form.
- In a firewalld zone the role does not own (`public`, `internal`), only enable services. Disable one there only when
  a variable the person set asks to restrict access (a source list moving the service to a role zone).
- When a role change alters what earlier versions left on a host (a file, unit, package, group membership, setting
  or path moved, renamed or dropped), also clean up that leftover state, so a host configured by an earlier version
  ends as a fresh install would. Keep each cleanup task idempotent and name it after what it removes.
- Keep every role runnable with `--check --diff`, also on a host configured by an earlier version. Check mode
  installs, copies and creates nothing, and a changed `copy` result has no `checksum`: skip a task that needs what an
  earlier task only pretends to create with `when: not (ansible_check_mode and <registered result> is changed)`, and
  compare against a source file by hashing it on the controller (`lookup('ansible.builtin.file', path,
  rstrip=false) | hash('sha1')`).
- Read facts as `ansible_facts['name']`, never the injected `ansible_<name>` variables.
- Cast every boolean option with `| bool` in conditions, templates and `ternary`: values from `-e` or INI inventories
  are strings, and `"false"` is truthy.
- Compare versions with `community.general.version_sort` or the `version` test, never as text (`"8.10" < "8.9"`).
- Apply configuration changes with handlers (`listen: <service>_restarted`) or a restart task gated on registered
  results' `.changed`; never restart on every run with `changed_when: false`.
- Prefix a registered variable with the role name (`_squid_...`) when other roles may use the same name: a registered
  result stays set for the rest of the play and overrides task `vars` of the same name in later roles.
- Name internal variables with a leading `_`; read-only commands get `changed_when: false` and `check_mode: false`.
- Build SELinux policy modules with the internal role `jgoutin.home.selinux_module` (`selinux_module_name`); the
  `.te` sources live in `roles/selinux_module/files/`.
- Import third-party repository keys from Fedora's signed `distribution-gpg-keys` package before installing release
  RPMs; never use `disable_gpg_check`.
- Remove packages with `autoremove: true`: the common role's autoremove runs before later removals, so their
  leftover dependencies would go only on the next run. Pass `install_weak_deps` to every `dnf` install or upgrade
  task: the module default (`true`) overrides the DNF configuration.
- Declare every collection a role uses in `galaxy.yml` `dependencies`, with the lowest version that has the options
  used.
- Role Python scripts run with the host's system `python3`: keep them compatible with the oldest supported Fedora's
  Python, with no dependency beyond the packages the role installs.

## Fedora facts that affect the roles

- `dnf` is dnf5: no dnf4 plugins or options; `dnf module` works with Remi's modular repositories.
- Since Fedora 45, distribution repository files are in `/usr/share/dnf5/repos.d` (overridable from
  `/etc/yum.repos.d`) and rpm verifies signatures by default (`%_pkgverify_level all`).
- Dovecot 2.4 syntax: settings go in a `/etc/dovecot/conf.d/` drop-in, which the stock `dovecot.conf` includes.
- Postfix still supports `hash:` maps; `*_use_tls` parameters are deprecated in favour of `*_tls_security_level`.
- Third-party repositories (Netdata, RPM Fusion, Remi, Copr) may lag a new Fedora release; the OS upgrade tasks must
  check them first.

## Testing in Fedora containers

Check package contents and command behaviour on a given release in a throwaway container, never on the host:

```
podman run --rm registry.fedoraproject.org/fedora:45 dnf -q repoquery --latest-limit 1 --qf '%{name} %{version}\n' <packages>
```

- To run role tasks in a container, install `ansible-core` with dnf, mount the repository read-only at `/src`, link
  `/src` as `/c/ansible_collections/jgoutin/home`, and mount `community.general` from `.github/.venv` (Fedora's
  packaged copy is too old) at `/cg/ansible_collections/community/general`, with `ANSIBLE_COLLECTIONS_PATH=/c:/cg`.
  Pass `--security-opt label=disable` rather than `:z` on these mounts: relabeling the repository fails on files you
  do not own and changes their SELinux labels.
- SELinux modules install in a container once `selinux-policy-targeted` is installed; services, firewalld and reboots
  need a real VM.
- Test RPM Fusion and Remi release installs with `--setopt=localpkg_gpgcheck=1` to prove the signature check runs.

## Serial display (musicplayer role)

Load the `serial-display` skill before changing the musicplayer role's serial display script, its glyphs or its device
commands.
