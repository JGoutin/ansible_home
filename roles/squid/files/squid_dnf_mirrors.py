#! /usr/bin/env python3
"""Squid DNF repositories mirrors updater"""
# Copyright (C) 2021 J.Goutin
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
__copyright__ = "Copyright 2021 J.Goutin"

import dnf
import re

_HTTP = re.compile(r"^https?://")
_is_http = _HTTP.match
_http_sub = _HTTP.sub


def update_dnf_mirrors(store_ids, releasever):
    """
    Updates DNF repositories mirrors list.

    Args:
        store_ids (dict): IDs as key, mirrors URLs as values.
        releasever (str or int): OS release version.
    """
    # Update repository information and get mirrors
    conf = dnf.conf.Conf()
    conf.releasever = str(releasever)
    repos = {}
    for repo in dnf.conf.read.RepoReader(conf, {}):
        try:
            repo.load()
        except dnf.exceptions.RepoError:
            pass
        mirrors = repo._repo.getMirrors()
        if len(mirrors) <= 2:
            # Skip if only one URL since no need to create StoreID to optimize hit ratio
            continue

        # Filter HTTP mirrors only and simplify scheme
        urls = set()
        for url in mirrors:
            if not _is_http(url):
                continue
            elif (
                _http_sub("http://", url) in mirrors
                and _http_sub("https://", url) in mirrors
            ):
                urls.add(_http_sub("https?://", url))
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
        repos[repo.id] = set(url[:-i] for url in urls)

    # Deduplicate mirrors
    for repo_id, repo_urls in repos.items():
        main_id = repo_id.split("-", 1)[0]
        if main_id == "updates":
            main_id = "fedora"
        store_id_urls = store_ids.setdefault(main_id, set())
        store_id_urls |= repo_urls


if __name__ == "__main__":

    # Get current OS version repository mirrors
    _store_ids = dict()
    update_dnf_mirrors(
        _store_ids, dnf.rpm.detect_releasever(dnf.conf.Conf().installroot)
    )

    # Write the Squid StoreID file
    with open("/etc/squid/dnf_mirrors", "wt") as _store_id_file:
        for _store_id, _urls in _store_ids.items():
            line = f"^%s(.*)\thttp://{_store_id}.squid.internal/$1\n"
            for _url in sorted(_urls):
                _store_id_file.write(
                    line % (_url.replace(".", r"\.").replace("/", r"\/"))
                )
