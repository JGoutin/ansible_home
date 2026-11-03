#! /usr/bin/env python3
"""Squid DNF repositories mirrors updater"""

# Copyright (C) 2024 J.Goutin
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

__version__ = "1.2.0"
__copyright__ = "Copyright 2024 J.Goutin"

import re
from os import getenv
from os.path import commonprefix
from pathlib import Path

import libdnf5

_HTTP_SCHEME = re.compile(r"^https?://")


def common_suffix_to_strip(urls: set[str], other_repos_urls: set[str]) -> int:
    """Get the number of trailing characters to remove from all mirrors URLs.

    The removed suffix is the one shared by all URLs, minus one character, and
    shortened so the stripped URLs are not a prefix of an URL of another repository.

    Args:
        urls: Mirrors URLs of the repository.
        other_repos_urls: Mirrors URLs of the other repositories.

    Returns:
        Number of characters to remove.
    """
    common = len(commonprefix([url[::-1] for url in urls]))
    for strip in range(1, common + 1):
        stripped = tuple({url[:-strip] for url in urls})
        if any(other_url.startswith(stripped) for other_url in other_repos_urls):
            return strip - 1
    # The whole shortest URL is shared: nothing can be removed safely
    return max(common - 1, 0) if common < min(map(len, urls)) else 0


def update_dnf_mirrors() -> dict[str, set[str]]:
    """Returns DNF repositories mirrors base URL list.

    Returns:
        Repositories IDs as key, mirrors URLs as values.
    """
    dnf = libdnf5.base.Base()
    dnf.setup()
    dnf_repo_sack = dnf.get_repo_sack()
    dnf_repo_sack.create_repos_from_system_configuration()
    dnf_repo_sack.load_repos(libdnf5.repo.Repo.Type_AVAILABLE)
    dnf_query = libdnf5.repo.RepoQuery(dnf)
    dnf_query.filter_enabled(True)

    repos_tmp: dict[str, set[str]] = {}
    for repo in dnf_query:
        mirrors = repo.get_mirrors()

        # Skip if only one URL since no need to create StoreID to optimize hit ratio
        if len(mirrors) < 2:
            continue

        # Keep HTTP mirrors only, the scheme being replaced by a regular expression
        repos_tmp[repo.get_id()] = {
            _HTTP_SCHEME.sub("https?://", url)
            for url in mirrors
            if _HTTP_SCHEME.match(url)
        }

    repos = {}
    for name, urls in repos_tmp.items():
        if len(urls) < 2:
            continue
        other_repos_urls = set().union(
            *(other for other_name, other in repos_tmp.items() if other_name != name)
        )
        strip = common_suffix_to_strip(urls, other_repos_urls)
        repos[name] = {url[: len(url) - strip] for url in urls}
    return repos


def write_squid_storeid_file(path: str, mirrors: dict[str, set[str]]) -> None:
    """Write Squid StoreID file.

    Args:
        path: Destination path.
        mirrors: DNF repositories mirrors list.
    """
    lines = sorted(
        f"^{url.replace('.', r'\.').replace('/', r'\/')}(.*)\t"
        f"http://{store_id}.squid.internal/$1\n"
        for store_id, urls in mirrors.items()
        for url in urls
    )
    Path(path).write_text("".join(lines))


if __name__ == "__main__":
    write_squid_storeid_file(
        getenv("STOREID_FILE_PATH", "/etc/squid/dnf_mirrors"), update_dnf_mirrors()
    )
