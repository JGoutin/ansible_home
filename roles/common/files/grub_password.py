#! /usr/bin/env python3
"""Set the GRUB password in user.cfg as grub2-setpassword does, only when it differs.

Usage: grub_password.py <user.cfg path>, with the password as the whole standard input.
Prints "changed" when it writes the file; exits 1 on an empty password.
"""

# Copyright (C) 2026 J.Goutin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import hashlib
import os
import re
import secrets
import sys
from pathlib import Path

#: PBKDF2 iterations of new entries, the grub2-mkpasswd-pbkdf2 default.
ITERATIONS = 10000
#: Salt and hash size of new entries in bytes, the grub2-mkpasswd-pbkdf2 default.
SIZE = 64
#: The line grub2-setpassword writes: iterations, salt and hash in upper-case hex.
ENTRY = re.compile(
    r"GRUB2_PASSWORD=grub\.pbkdf2\.sha512\.([1-9]\d*)\.((?:[0-9A-F]{2})+)\.((?:[0-9A-F]{2})+)"
)


def pbkdf2(password: bytes, salt: bytes, iterations: int, size: int) -> str:
    """Return the PBKDF2-SHA512 hash of the password in upper-case hexadecimal."""
    return hashlib.pbkdf2_hmac("sha512", password, salt, iterations, size).hex().upper()


def matches(content: str, password: bytes) -> bool:
    """Return whether the user.cfg content holds an entry for this password."""
    entry = ENTRY.fullmatch(content.strip())
    if not entry:
        return False
    iterations, salt, digest = entry.groups()
    return secrets.compare_digest(
        pbkdf2(password, bytes.fromhex(salt), int(iterations), len(digest) // 2), digest
    )


def entry(password: bytes) -> str:
    """Return a user.cfg line for the password, with a new random salt."""
    salt = secrets.token_bytes(SIZE)
    hashed = (
        f"{ITERATIONS}.{salt.hex().upper()}.{pbkdf2(password, salt, ITERATIONS, SIZE)}"
    )
    return f"GRUB2_PASSWORD=grub.pbkdf2.sha512.{hashed}\n"


def main(argv: list[str]) -> int:
    """Write an entry to the file argv[1], unless it holds one for the password."""
    path = Path(argv[1])
    password = sys.stdin.buffer.read()
    if not password:
        print("grub_password: empty password", file=sys.stderr)
        return 1
    try:
        current = path.read_text()
    except FileNotFoundError:
        current = ""
    if matches(current, password):
        return 0
    temporary = path.with_name(f".{path.name}.tmp")
    with os.fdopen(
        os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), "w"
    ) as file:
        file.write(entry(password))
        file.flush()
        os.fsync(file.fileno())
    os.replace(temporary, path)
    print("changed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
