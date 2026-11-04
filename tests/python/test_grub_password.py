"""Tests of the GRUB password setter."""

import hashlib
import io
import sys
from types import SimpleNamespace

import pytest
from conftest import load_script

grub_password = load_script("common/files/grub_password.py")

#: Salt of the reference entries, shorter than the 64 bytes grub2-mkpasswd-pbkdf2 uses.
REFERENCE_SALT = bytes(range(16))


def reference_entry(password: bytes, iterations: int = 10000) -> str:
    salt = REFERENCE_SALT.hex().upper()
    digest = hashlib.pbkdf2_hmac("sha512", password, REFERENCE_SALT, iterations, 32)
    hashed = f"{iterations}.{salt}.{digest.hex().upper()}"
    return f"GRUB2_PASSWORD=grub.pbkdf2.sha512.{hashed}\n"


#: Output of grub2-mkpasswd-pbkdf2 on Fedora 44 for the password "s3cret".
GRUB_REFERENCE = (
    "GRUB2_PASSWORD=grub.pbkdf2.sha512.10000."
    "DAB7C52468716D1FCED12C157DDCC89621B47F343B63129C87B6C26685D28EB6"
    "02D1752F8EBE06A808095166D4BA4E5F0EB993E7975936C57B3D0AB4B7B43050."
    "AA34731143AB4449127F7FAC113EF86619D8C492F4B07BE773ACB6BCE883BF13"
    "790A3ECBE1F26498510B30BC2743BE3C41863350936EB71D9C655918567D1225\n"
)


def test_grub_entry_matches_only_its_password():
    assert grub_password.matches(GRUB_REFERENCE, b"s3cret")
    assert not grub_password.matches(GRUB_REFERENCE, b"s3cret2")


def run(monkeypatch, capsys, path, password: bytes):
    monkeypatch.setattr(sys, "stdin", SimpleNamespace(buffer=io.BytesIO(password)))
    code = grub_password.main(["grub_password.py", str(path)])
    return code, capsys.readouterr()


def test_existing_entry_with_the_same_password_is_kept(monkeypatch, capsys, tmp_path):
    """Any iteration count and hash size of an existing entry is accepted."""
    path = tmp_path / "user.cfg"
    path.write_text(reference_entry(b"s3cret", 20000))
    code, out = run(monkeypatch, capsys, path, b"s3cret")
    assert (code, out.out) == (0, "")
    assert path.read_text() == reference_entry(b"s3cret", 20000)


@pytest.mark.parametrize(
    "content",
    [
        None,
        "",
        "GRUB2_PASSWORD=grub.pbkdf2.sha512.10000.ABC.DEF\n",
        "GRUB2_PASSWORD=grub.pbkdf2.sha512.0.AB.CD\n",
        reference_entry(b"other"),
    ],
    ids=["missing", "empty", "malformed", "no iterations", "other password"],
)
def test_entry_is_written_when_absent_or_different(
    monkeypatch, capsys, tmp_path, content
):
    """The new entry has the grub2-mkpasswd-pbkdf2 format and matches the password."""
    path = tmp_path / "user.cfg"
    if content is not None:
        path.write_text(content)
    code, out = run(monkeypatch, capsys, path, b"s3cret")
    assert (code, out.out) == (0, "changed\n")
    assert path.stat().st_mode & 0o777 == 0o600
    assert grub_password.matches(path.read_text(), b"s3cret")
    assert path.read_text().startswith("GRUB2_PASSWORD=grub.pbkdf2.sha512.10000.")
    assert list(tmp_path.iterdir()) == [path]
    salt = path.read_text().split(".")[4]
    assert len(salt) == 128


def test_new_entries_use_a_new_salt():
    assert grub_password.entry(b"s3cret") != grub_password.entry(b"s3cret")


def test_empty_password_is_refused(monkeypatch, capsys, tmp_path):
    path = tmp_path / "user.cfg"
    code, out = run(monkeypatch, capsys, path, b"")
    assert code == 1
    assert out.err
    assert not path.exists()
