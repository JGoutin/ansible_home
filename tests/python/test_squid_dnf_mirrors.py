"""Tests of the Squid StoreID file generator."""

import sys
from types import SimpleNamespace

from conftest import load_script

sys.modules.setdefault("libdnf5", SimpleNamespace())
mirrors = load_script("squid/files/squid_dnf_mirrors.py")


class FakeRepo:
    def __init__(self, repo_id, urls):
        self._id, self._urls = repo_id, urls

    def get_id(self):
        return self._id

    def get_mirrors(self):
        return self._urls


def fake_libdnf(monkeypatch, repos):
    class Base:
        def setup(self):
            pass

        def get_repo_sack(self):
            return SimpleNamespace(
                create_repos_from_system_configuration=lambda: None,
                load_repos=lambda _: None,
            )

    class RepoQuery(list):
        def __init__(self, _base):
            super().__init__(repos)

        def filter_enabled(self, _):
            pass

    monkeypatch.setattr(
        mirrors,
        "libdnf5",
        SimpleNamespace(
            base=SimpleNamespace(Base=Base),
            repo=SimpleNamespace(
                Repo=SimpleNamespace(Type_AVAILABLE=0), RepoQuery=RepoQuery
            ),
        ),
    )


def test_common_suffix_is_removed(monkeypatch):
    fake_libdnf(
        monkeypatch,
        [
            FakeRepo(
                "fedora",
                [
                    "https://a.example/fedora/44/x86_64/os/",
                    "http://b.example/pub/fedora/44/x86_64/os/",
                ],
            )
        ],
    )
    assert mirrors.update_dnf_mirrors() == {
        "fedora": {"https?://a.example/", "https?://b.example/pub/"}
    }


def test_repository_with_one_mirror_is_skipped(monkeypatch):
    fake_libdnf(monkeypatch, [FakeRepo("single", ["http://a.example/x/"])])
    assert mirrors.update_dnf_mirrors() == {}


def test_storeid_file_is_sorted_and_escaped(tmp_path):
    path = tmp_path / "ids"
    mirrors.write_squid_storeid_file(str(path), {"r": {"b.example/x", "a.example/x"}})
    assert path.read_text() == (
        "^a\\.example\\/x(.*)\thttp://r.squid.internal/$1\n"
        "^b\\.example\\/x(.*)\thttp://r.squid.internal/$1\n"
    )


def test_conflict_with_another_repository_keeps_the_url_unstripped(monkeypatch):
    fake_libdnf(
        monkeypatch,
        [
            FakeRepo("r1", ["http://a.example/os/", "http://b.example/os/"]),
            FakeRepo("r2", ["http://a.example/os2/", "http://c.example/os2/"]),
        ],
    )
    assert mirrors.update_dnf_mirrors()["r1"] == {
        "https?://a.example/os/",
        "https?://b.example/os/",
    }


def test_urls_without_common_suffix_are_kept_whole(monkeypatch):
    fake_libdnf(
        monkeypatch, [FakeRepo("r", ["http://a.example/x", "http://b.example/y"])]
    )
    assert mirrors.update_dnf_mirrors() == {
        "r": {"https?://a.example/x", "https?://b.example/y"}
    }


def test_repository_without_two_http_mirrors_is_skipped(monkeypatch):
    fake_libdnf(
        monkeypatch,
        [
            FakeRepo("ftp", ["ftp://a.example/x/", "ftp://b.example/x/"]),
            FakeRepo("one", ["http://a.example/x/", "ftp://b.example/x/"]),
        ],
    )
    assert mirrors.update_dnf_mirrors() == {}


def test_url_ending_with_another_url_is_left_unchanged(monkeypatch):
    fake_libdnf(monkeypatch, [FakeRepo("r", ["http://b/x", "http://a/https?://b/x"])])
    assert mirrors.update_dnf_mirrors() == {
        "r": {"https?://b/x", "https?://a/https?://b/x"}
    }
