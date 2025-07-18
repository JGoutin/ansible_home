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

import libdnf5
import re
from os import getenv


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

    http_pattern = re.compile(r"^https?://")
    is_http = http_pattern.match
    http_sub = http_pattern.sub

    repos_tmp = {}
    for repo in dnf_query:
        mirrors = repo.get_mirrors()

        # Skip if only one URL since no need to create StoreID to optimize hit ratio
        if len(mirrors) < 2:
            continue

        # Keep HTTP mirrors only
        repos_tmp[repo.get_id()] = urls = set()
        for url in mirrors:
            if is_http(url):
                urls.add(http_sub("https?://", url))

    repos = {}
    for name, urls in repos_tmp.items():
        other_repos_urls = set()
        for other_name, other_urls in repos_tmp.items():
            if other_name != name:
                other_repos_urls |= other_urls

        # Remove the common suffix of all mirrors
        shorter = min(urls)
        others = urls.copy()
        others.remove(shorter)
        for i, char in enumerate(reversed(shorter)):
            if any(url[-i - 1] != char for url in others):
                i -= 1
                break

            # Ensure there is no conflicts with other repositories
            pending_result = set(url[: -i - 1] for url in urls)
            if any(
                any(other_url.startswith(url) for url in pending_result)
                for other_url in other_repos_urls
            ):
                break
        else:
            i = 0
        repos[name] = set(url[:-i] for url in urls)
    return repos


def write_squid_storeid_file(path: str, mirrors: dict[str, set[str]]) -> None:
    """Write Squid StoreID file.

    Args:
        path: Destination path.
        mirrors: DNF repositories mirrors list.
    """
    lines = []
    for store_id, urls in mirrors.items():
        line = f"^%s(.*)\thttp://{store_id}.squid.internal/$1\n"
        for url in urls:
            lines.append(line % (url.replace(".", r"\.").replace("/", r"\/")))

    with open(path, "wt") as _store_id_file:
        _store_id_file.write("".join(sorted(lines)))


if __name__ == "__main__":
    write_squid_storeid_file(
        getenv("STOREID_FILE_PATH", "/etc/squid/dnf_mirrors"), update_dnf_mirrors()
    )
