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

__version__ = "1.0.1"
__copyright__ = "Copyright 2025 J.Goutin"

import re
from concurrent.futures import ThreadPoolExecutor
from http.client import HTTPException
from platform import freedesktop_os_release, machine
from signal import SIGINT, SIGTERM, signal
from sys import exit, stderr, stdin, stdout
from threading import Lock
from urllib.error import HTTPError
from urllib.request import Request, urlopen


class HttpException(Exception):
    """HTTP Exception."""


#: HTTP status codes meaning the requested file does not exist.
NOT_FOUND_CODES = (403, 404)

#: Timeout in seconds of each HEAD request, so a stalled mirror cannot block a worker.
REQUEST_TIMEOUT = 10

#: Number of concurrent requests, the same as Squid "url_rewrite_children" concurrency.
MAX_WORKERS = 32

HEADERS = {
    "User-Agent": (
        f"libdnf (Fedora {freedesktop_os_release()['VERSION_ID']}; "
        f"server; Linux.{machine()})"
    )
}

rpm_repo = re.compile(
    r"^https?://.+/(?P<releasever>\d+)/(?P<basearch>[^/]+)"
    r"(?:/[^/]+)*?(?:/repodata/|[^/]+\.rpm$|[^/]+\.drpm$|[^/]+\.srpm$)"
).match

_stdout_lock = Lock()


def signal_handler(*_: object) -> None:
    """Handle signals."""
    exit(0)


def head(url: str) -> int:
    """Make a HEAD request to the specified URL and return the response code.

    Args:
        url: The URL to request.

    Returns:
        HTTP status code.

    Raises:
        HttpException: Server error (5xx) or connection failure.
    """
    # Only http(s) URLs matched by rpm_repo reach this function.
    request = Request(url, method="HEAD", headers=HEADERS)  # noqa: S310
    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT) as response:  # noqa: S310
            return response.status
    except HTTPError as error:
        if error.code >= 500:
            raise HttpException(f"Server error: {error.code}") from error
        return error.code
    except (OSError, HTTPException) as error:
        raise HttpException(f"Failed to connect to {url}") from error


def rewrite_url(url: str, channel_id: str) -> None:
    """Rewrite URL and return output to stdout in Squid format.

    Args:
        url: URL to rewrite.
        channel_id: Channel ID.
    """
    # Default response (No URL change)
    kvpair = ""
    result = "ERR"

    try:
        repo = rpm_repo(url)
        if repo and head(url) in NOT_FOUND_CODES:
            releasever = int(repo["releasever"])
            candidate = url.replace(f"/{releasever}/", f"/{releasever - 1}/")
            if head(candidate) not in NOT_FOUND_CODES:
                kvpair = f'rewrite-url="{candidate}"'
                result = "OK"

    # Response in case the server is down or the URL is not reachable
    except HttpException:
        result = "BH"

    # Last resort: Squid waits forever for a request left without reply
    except Exception as error:
        print(f"Unexpected error rewriting {url}: {error!r}", file=stderr)
        result = "BH"

    # One lock for write and flush, since workers answer concurrently
    with _stdout_lock:
        stdout.write(" ".join(filter(None, (channel_id, result, kvpair))) + "\n")
        stdout.flush()


def url_rewrite_program() -> None:
    """Redirect DNF repositories.

    In the case no repository is found for the current Fedora version,
    redirect to the previous Fedora version repository.

    To user with Squid "url_rewrite_program".
    https://wiki.squid-cache.org/Features/Redirectors
    """
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for line in stdin:
            params = line.split(maxsplit=2)
            if not params:
                continue
            if "://" in params[0]:
                channel_id, url = "", params[0]
            elif len(params) > 1:
                channel_id, url = params[0], params[1]
            else:
                continue
            executor.submit(rewrite_url, url, channel_id)


if __name__ == "__main__":
    signal(SIGTERM, signal_handler)
    signal(SIGINT, signal_handler)
    url_rewrite_program()
