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

__version__ = "1.1.0"
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

    repos = {}
    for repo in dnf_query:
        mirrors = repo.get_mirrors()

        # Skip if only one URL since no need to create StoreID to optimize hit ratio
        if len(mirrors) <= 2:
            continue

        # Filter HTTP mirrors only and simplify scheme
        urls = set()
        for url in mirrors:
            if not is_http(url):
                continue
            elif (
                http_sub("http://", url) in mirrors
                and http_sub("https://", url) in mirrors
            ):
                urls.add(http_sub("https?://", url))
            else:
                urls.add(url)

        # Remove the common suffix of all mirrors
        shorter = min(urls)
        others = list(urls)
        others.remove(shorter)
        for i, char in enumerate(reversed(shorter)):
            if any(url[-i - 1] != char for url in others):
                i -= 1
                break
        else:
            i = 0
        repos[repo.get_id()] = set(url[:-i] for url in urls)

    return repos


def write_squid_storeid_file(path: str, mirrors: dict[str, set[str]]) -> None:
    """Write Squid StoreID file.

    Args:
        path: Destination path.
        mirrors: DNF repositories mirrors list.
    """
    store_ids = dict()
    for repo_id, repo_urls in mirrors.items():
        # Deduplicate mirrors
        main_id = repo_id.split("-", 1)[0]
        if main_id == "updates":
            main_id = "fedora"
        store_id_urls = store_ids.setdefault(main_id, set())
        store_id_urls |= repo_urls

    with open(path, "wt") as _store_id_file:
        for _store_id, _urls in store_ids.items():
            line = f"^%s(.*)\thttp://{_store_id}.squid.internal/$1\n"
            for _url in sorted(_urls):
                _store_id_file.write(
                    line % (_url.replace(".", r"\.").replace("/", r"\/"))
                )


if __name__ == "__main__":
    write_squid_storeid_file(
        getenv("STOREID_FILE_PATH", "/etc/squid/dnf_mirrors"), update_dnf_mirrors()
    )
