"""A single persistent Playwright browser tab that live-renders the progress table.

Imported lazily by doi_downloader.download() only when show_progress=True, so
importing doi_downloader never requires a Playwright browser to be installed.

Runs the browser in its own background thread with its own event loop, using
Playwright's async API there. This keeps it independent of whatever asyncio
loop (if any) is running in the caller's thread -- Playwright's sync API
refuses to start when the calling thread already has a running event loop,
which is exactly the situation in Jupyter notebooks.
"""

import asyncio
import atexit
import threading

from playwright.async_api import async_playwright


class BrowserView:
    def __init__(self):
        self._loop = None
        self._thread = None
        self._playwright = None
        self._browser = None
        self._page = None
        self._ready = threading.Event()

    def _ensure_started(self):
        if self._thread is not None:
            return
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        self._ready.wait()
        atexit.register(self.close)

    def _run_loop(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._start())
        self._ready.set()
        self._loop.run_forever()

    async def _start(self):
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=False)
        self._page = await self._browser.new_page()

    def update(self, html_content):
        self._ensure_started()
        future = asyncio.run_coroutine_threadsafe(self._page.set_content(html_content), self._loop)
        future.result()

    def close(self):
        if self._loop is None:
            return
        future = asyncio.run_coroutine_threadsafe(self._shutdown(), self._loop)
        future.result()
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join(timeout=5)
        self._loop = self._thread = self._browser = self._page = self._playwright = None

    async def _shutdown(self):
        if self._browser is not None:
            await self._browser.close()
        if self._playwright is not None:
            await self._playwright.stop()


_view = None


def get_browser_view():
    """Return the process-wide singleton browser view, launching it on first use."""
    global _view
    if _view is None:
        _view = BrowserView()
    return _view
