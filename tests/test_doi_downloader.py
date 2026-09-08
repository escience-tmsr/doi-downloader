import os

from doi_downloader import doi_downloader as dd
from doi_downloader import progress, progress_browser
from doi_downloader.plugins import Plugin

DOI = "10.1000/progress-example"


class FakePlugin(Plugin):
    """A plugin double that skips the real cache/network machinery."""

    plugin_name = "FakePlugin"

    def __init__(self, urls=None):
        self._urls = urls or []

    def get_pdf_urls(self, doi):
        return self._urls


class FakeBrowserView:
    def __init__(self):
        self.updates = []

    def update(self, html_content):
        self.updates.append(html_content)


def test_download_without_show_progress_never_touches_progress_browser(monkeypatch):
    def fail_if_called():
        raise AssertionError("progress_browser should not be used when show_progress=False")

    monkeypatch.setattr(progress_browser, "get_browser_view", fail_if_called)
    monkeypatch.setattr(dd, "plugins", {"FakePlugin": FakePlugin()})

    result = dd.download(DOI, show_progress=False, enable_benchmark=False)

    assert result is None


def test_download_with_show_progress_records_and_refreshes_the_view(monkeypatch):
    fake_view = FakeBrowserView()
    monkeypatch.setattr(progress_browser, "get_browser_view", lambda: fake_view)
    monkeypatch.setattr(dd, "plugins", {"FakePlugin": FakePlugin(urls=[])})
    monkeypatch.setattr(progress, "_recorder", None)

    result = dd.download(DOI, show_progress=True, enable_benchmark=False)

    assert result is None
    assert fake_view.updates
    last_update = fake_view.updates[-1]
    assert DOI in last_update
    assert "FakePlugin" in last_update
    assert progress.STATUS_NOT_FOUND in last_update  # disk status: file was never downloaded


def test_download_show_progress_skips_plugins_when_file_already_exists(monkeypatch):
    fake_view = FakeBrowserView()
    monkeypatch.setattr(progress_browser, "get_browser_view", lambda: fake_view)
    monkeypatch.setattr(dd, "plugins", {"FakePlugin": FakePlugin()})
    monkeypatch.setattr(progress, "_recorder", None)

    safe_filename = dd.sanitize_doi(DOI) + ".pdf"
    with open(safe_filename, "wb") as f:
        f.write(b"%PDF-1.4 fake content")

    result = dd.download(DOI, output_dir=".", show_progress=True, enable_benchmark=False)

    assert result == os.path.join(".", safe_filename)
    assert fake_view.updates
    last_update = fake_view.updates[-1]
    assert progress.STATUS_SKIPPED in last_update
