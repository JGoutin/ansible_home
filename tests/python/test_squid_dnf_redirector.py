"""Tests of the Squid URL rewriter."""

import io

import pytest
from conftest import load_script

redirector = load_script("squid/files/squid_dnf_redirector.py")

BASE = "http://mirror.example/pub/fedora/linux/updates/44/Everything/x86_64"


@pytest.mark.parametrize(
    ("url", "releasever", "basearch"),
    [
        (f"{BASE}/repodata/repomd.xml", "44", "Everything"),
        (f"{BASE}/Packages/f/foo-1.rpm", "44", "Everything"),
        (f"{BASE}/foo-1.drpm", "44", "Everything"),
        ("https://m.example/fedora/44/aarch64/foo.src.rpm", "44", "aarch64"),
    ],
)
def test_rpm_repo_matches_repository_urls(url, releasever, basearch):
    match = redirector.rpm_repo(url)
    assert match
    assert match["releasever"] == releasever
    assert match["basearch"] == basearch


@pytest.mark.parametrize(
    "url",
    [
        "http://example.com/index.html",
        f"{BASE}/foo.txt",
        "ftp://m.example/fedora/44/x86_64/foo.rpm",
        "http://m.example/fedora/x86_64/foo.rpm",
    ],
)
def test_rpm_repo_ignores_other_urls(url):
    assert redirector.rpm_repo(url) is None


@pytest.fixture
def out(monkeypatch):
    buffer = io.StringIO()
    monkeypatch.setattr(redirector, "stdout", buffer)
    return buffer


def fake_head(monkeypatch, codes):
    calls = []

    def head(url):
        calls.append(url)
        code = codes[len(calls) - 1]
        if isinstance(code, Exception):
            raise code
        return code

    monkeypatch.setattr(redirector, "head", head)
    return calls


URL = f"{BASE}/Packages/f/foo-1.rpm"
PREVIOUS = URL.replace("/44/", "/43/")


def test_rewrite_to_previous_release_when_missing(monkeypatch, out):
    calls = fake_head(monkeypatch, [404, 200])
    redirector.rewrite_url(URL, "3")
    assert out.getvalue() == f'3 OK rewrite-url="{PREVIOUS}"\n'
    assert calls == [URL, PREVIOUS]


def test_no_change_when_url_exists(monkeypatch, out):
    fake_head(monkeypatch, [200])
    redirector.rewrite_url(URL, "")
    assert out.getvalue() == "ERR\n"


def test_no_change_when_previous_release_also_missing(monkeypatch, out):
    fake_head(monkeypatch, [403, 404])
    redirector.rewrite_url(URL, "1")
    assert out.getvalue() == "1 ERR\n"


def test_non_repository_url_makes_no_request(monkeypatch, out):
    calls = fake_head(monkeypatch, [])
    redirector.rewrite_url("http://example.com/", "1")
    assert out.getvalue() == "1 ERR\n"
    assert not calls


def test_bad_helper_answer_on_server_error(monkeypatch, out):
    fake_head(monkeypatch, [redirector.HttpException("x")])
    redirector.rewrite_url(URL, "2")
    assert out.getvalue() == "2 BH\n"


def test_head_returns_client_error_code(monkeypatch):
    from urllib.error import HTTPError

    def urlopen(request, **_):
        raise HTTPError(request.full_url, 404, "nf", {}, None)

    monkeypatch.setattr(redirector, "urlopen", urlopen)
    assert redirector.head(URL) == 404


def test_head_raises_on_server_error(monkeypatch):
    from urllib.error import HTTPError

    def urlopen(request, **_):
        raise HTTPError(request.full_url, 503, "bad", {}, None)

    monkeypatch.setattr(redirector, "urlopen", urlopen)
    with pytest.raises(redirector.HttpException):
        redirector.head(URL)


def test_head_raises_on_connection_failure(monkeypatch):
    from urllib.error import URLError

    def urlopen(request, **_):
        raise URLError("down")

    monkeypatch.setattr(redirector, "urlopen", urlopen)
    with pytest.raises(redirector.HttpException):
        redirector.head(URL)


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        (f"{URL} 10.0.0.1/- - GET\n", ("", URL)),
        (f"7 {URL} 10.0.0.1/- - GET\n", ("7", URL)),
        ("\n", None),
        ("7\n", None),
    ],
)
def test_url_rewrite_program_parses_lines(monkeypatch, line, expected):
    calls = []
    monkeypatch.setattr(redirector, "stdin", io.StringIO(line))
    monkeypatch.setattr(
        redirector, "rewrite_url", lambda url, channel: calls.append((channel, url))
    )
    redirector.url_rewrite_program()
    assert calls == ([expected] if expected else [])
