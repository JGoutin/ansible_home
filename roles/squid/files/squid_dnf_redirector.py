#! /usr/bin/env python3
"""Squid DNF repositories redirector."""
# Copyright (C) 2025 J.Goutin
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

__version__ = "1.0.0"
__copyright__ = "Copyright 2025 J.Goutin"

from sys import stdin, stdout, exit
from re import compile
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from concurrent.futures import ThreadPoolExecutor
from signal import signal, SIGTERM, SIGINT
from platform import machine


class HttpException(Exception):
    """HTTP Exception."""


def get_release_ver() -> str:
    """Get Current OS release.

    Returns:
        OS release version.
    """
    with open("/etc/os-release", "rt") as os_release:
        for line in os_release:
            if line.startswith("VERSION_ID="):
                return line.split("=", 1)[1].strip()
    raise RuntimeError("VERSION_ID not found in /etc/os-release")


NOT_FOUND_CODES = (403, 404)
HEADERS = {
    "User-Agent": f"libdnf (Fedora {get_release_ver()}; server; Linux.{machine()})"
}

rpm_repo = compile(
    r"^https?://.+/(?P<releasever>\d+)/(?P<basearch>[^/]+)"
    r"(?:/[^/]+)*?(?:/repodata/|[^/]+\.rpm$|[^/]+\.drpm$|[^/]+\.srpm$)"
).match


def signal_handler(*_: object) -> None:
    """Handle signals."""
    exit(0)


def head(url: str) -> int:
    """Make a HEAD request to the specified URL and return the response code.

    Args:
        url: The URL to request

    Returns:
        tuple: (status_code, headers)
    """
    request = Request(url, method="HEAD", headers=HEADERS)
    try:
        with urlopen(request) as response:  # nosec
            return response.status  # type: ignore
    except HTTPError as error:
        if error.code >= 500:
            raise HttpException(f"Server error: {error.code}")
        return error.code
    except URLError:
        raise HttpException(f"Failed to connect to {url}")


def rewrite_url(url: str, channel_id: str) -> None:
    """Rewrite URL and return output to stdout in Squid format.

    Args:
        url: URL to rewrite.
        channel_id: Channel ID.
        +
    """
    # Default response (No URL change)
    kvpair = ""
    result = "ERR"

    # Analyse URL
    try:
        repo = rpm_repo(url)
        if repo and head(url) in NOT_FOUND_CODES:
            releasever = int(repo.group("releasever"))
            candidate = url.replace(f"/{releasever}/", f"/{releasever - 1}/")
            if head(candidate) not in NOT_FOUND_CODES:
                # Response if URL changed
                kvpair = f'rewrite-url="{candidate}"'
                result = "OK"

    # Response in case the server is down or the URL is not reachable
    except HttpException:
        result = "BH"

    # Response must be output to stdout in Squid format
    stdout.write(
        " ".join((param for param in (channel_id, result, kvpair) if param)) + "\n"
    )
    stdout.flush()


def url_rewrite_program() -> None:
    """Redirect DNF repositories.

    In the case no repository is found for the current Fedora version,
    redirect to the previous Fedora version repository.

    To user with Squid "url_rewrite_program".
    https://wiki.squid-cache.org/Features/Redirectors
    """
    with ThreadPoolExecutor(max_workers=32) as executor:
        try:
            for line in stdin:
                params = line.split(maxsplit=2)
                try:
                    if "://" in params[0]:
                        channel_id = ""
                        url = params[0]
                    else:
                        channel_id = params[0]
                        url = params[1]
                except IndexError:
                    continue
                executor.submit(rewrite_url, url, channel_id)
        except KeyboardInterrupt:
            return


if __name__ == "__main__":
    signal(SIGTERM, signal_handler)
    signal(SIGINT, signal_handler)
    url_rewrite_program()
