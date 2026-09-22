import asyncio

import pytest

from doi_downloader import progress_browser


class FakePage:
    def __init__(self):
        self.contents = []

    async def set_content(self, html_content):
        self.contents.append(html_content)


class FakeBrowser:
    def __init__(self):
        self.page = FakePage()
        self.closed = False

    async def new_page(self, no_viewport=None):
        self.new_page_kwargs = {"no_viewport": no_viewport}
        return self.page

    async def close(self):
        self.closed = True


class FakeChromium:
    def __init__(self, browser):
        self._browser = browser
        self.launch_kwargs = None

    async def launch(self, headless=None):
        self.launch_kwargs = {"headless": headless}
        return self._browser


class FakePlaywright:
    def __init__(self, browser):
        self.chromium = FakeChromium(browser)
        self.stopped = False

    async def stop(self):
        self.stopped = True


class FakePlaywrightContextManager:
    def __init__(self, playwright):
        self._playwright = playwright

    async def start(self):
        return self._playwright


@pytest.fixture
def browser_view(monkeypatch):
    """A BrowserView wired to fakes instead of a real Playwright/Chromium instance."""
    browser = FakeBrowser()
    playwright = FakePlaywright(browser)
    monkeypatch.setattr(progress_browser, "async_playwright", lambda: FakePlaywrightContextManager(playwright))
    view = progress_browser.BrowserView()
    yield view, browser, playwright
    view.close()


def test_update_starts_browser_headful_and_sets_content(browser_view):
    view, browser, playwright = browser_view
    view.update("<html>one</html>")
    assert browser.page.contents == ["<html>one</html>"]
    assert playwright.chromium.launch_kwargs == {"headless": False}
    assert browser.new_page_kwargs == {"no_viewport": True}


def test_update_reuses_the_same_browser_and_thread_across_calls(browser_view):
    view, browser, playwright = browser_view
    view.update("<html>one</html>")
    thread_after_first_call = view._thread
    view.update("<html>two</html>")
    assert browser.page.contents == ["<html>one</html>", "<html>two</html>"]
    assert view._thread is thread_after_first_call
    # the browser/page should only ever be launched once
    assert playwright.chromium.launch_kwargs == {"headless": False}


def test_close_stops_browser_and_playwright_and_resets_state(browser_view):
    view, browser, playwright = browser_view
    view.update("<html>x</html>")
    view.close()
    assert browser.closed
    assert playwright.stopped
    assert view._loop is None
    assert view._thread is None
    assert view._browser is None
    assert view._page is None
    assert view._playwright is None


def test_close_before_any_update_is_a_noop():
    view = progress_browser.BrowserView()
    view.close()  # must not raise even though the background thread never started
    assert view._loop is None


def test_shutdown_tolerates_browser_and_playwright_never_having_started():
    # _shutdown guards each step with `is not None` so a partially-initialized
    # view (e.g. _start() failed before setting _browser/_playwright) can
    # still be torn down without raising.
    view = progress_browser.BrowserView()
    asyncio.run(view._shutdown())


def test_get_browser_view_returns_a_process_wide_singleton(monkeypatch):
    monkeypatch.setattr(progress_browser, "_view", None)
    first = progress_browser.get_browser_view()
    second = progress_browser.get_browser_view()
    assert first is second
    assert isinstance(first, progress_browser.BrowserView)
