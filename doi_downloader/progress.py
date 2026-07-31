"""Collects per-(doi, plugin) download progress and renders it as an HTML table.

Recording is opt-in and cheap when inactive: the free functions below are no-ops
unless `active_row` has been entered around the current call stack (done by
`doi_downloader.download()` when `show_progress=True`), so calling plugins or
`pdf_download` directly (as tests and the benchmark harness do) is unaffected.
"""

import contextvars
import html
from dataclasses import dataclass, field

STATUS_SUCCESS = "SUCCESS"
STATUS_NOT_FOUND = "NOT_FOUND"
STATUS_ACCESS_ERROR = "ACCESS_ERROR"
STATUS_SKIPPED = "SKIPPED"

_COLUMNS = [
    "DOI", "plugin",
    "disk status", "disk result",
    "cache status", "cache result",
    "fetch status", "fetch result",
    "pdf access status", "pdf access urls", "pdf access files",
]


@dataclass
class _RowData:
    doi: str
    plugin_name: str
    disk_status: str = STATUS_SKIPPED
    disk_result: list = field(default_factory=list)
    cache_status: str = STATUS_SKIPPED
    cache_result: list = field(default_factory=list)
    fetch_status: list = field(default_factory=list)
    fetch_result: list = field(default_factory=list)
    pdf_access_status: list = field(default_factory=list)
    pdf_access_urls: list = field(default_factory=list)
    pdf_access_files: list = field(default_factory=list)


class ProgressRecorder:
    """Collects progress events keyed by (doi, plugin_name) and renders them as an HTML table."""

    def __init__(self):
        self._rows = {}

    def _row(self, doi, plugin_name):
        key = (doi, plugin_name)
        if key not in self._rows:
            self._rows[key] = _RowData(doi=doi, plugin_name=plugin_name)
        return self._rows[key]

    def record_disk(self, doi, plugin_name, status, result):
        row = self._row(doi, plugin_name)
        row.disk_status = status
        row.disk_result = [result] if result else []

    def record_cache(self, doi, plugin_name, status, result):
        row = self._row(doi, plugin_name)
        row.cache_status = status
        row.cache_result = list(result) if result else []

    def record_fetch(self, doi, plugin_name, status, url):
        row = self._row(doi, plugin_name)
        row.fetch_status.append(status)
        row.fetch_result.append(url or "")

    def record_pdf_access(self, doi, plugin_name, status, url):
        row = self._row(doi, plugin_name)
        row.pdf_access_status.append(status)
        row.pdf_access_urls.append(url or "")

    def record_pdf_file(self, doi, plugin_name, filepath):
        row = self._row(doi, plugin_name)
        row.pdf_access_files.append(filepath)

    def to_html(self):
        header = "".join(f"<th>{html.escape(c)}</th>" for c in _COLUMNS)
        rows_html = "".join(self._row_html(row) for row in self._rows.values())
        return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>doi_downloader progress</title>
<style>
body {{ font-family: sans-serif; font-size: 13px; margin: 0; }}
.table-wrap {{ overflow-x: auto; width: 100%; box-sizing: border-box; }}
table {{ border-collapse: collapse; min-width: 100%; }}
th, td {{
    border: 1px solid #ccc; padding: 4px 8px; vertical-align: top; text-align: left;
    max-width: 260px; overflow-wrap: anywhere;
}}
th {{ background: #f0f0f0; position: sticky; top: 0; white-space: nowrap; }}
ul {{ margin: 0; padding-left: 16px; }}
</style></head>
<body><div class="table-wrap"><table>
<thead><tr>{header}</tr></thead><tbody>{rows_html}</tbody>
</table></div></body></html>"""

    def _row_html(self, row):
        cells = "".join([
            self._cell(row.doi), self._cell(row.plugin_name),
            self._cell(row.disk_status), self._cell(row.disk_result),
            self._cell(row.cache_status), self._cell(row.cache_result),
            self._cell(row.fetch_status), self._cell(row.fetch_result),
            self._cell(row.pdf_access_status), self._cell(row.pdf_access_urls), self._cell(row.pdf_access_files),
        ])
        return f"<tr>{cells}</tr>"

    @staticmethod
    def _cell(value):
        if isinstance(value, list):
            if not value:
                return "<td></td>"
            items = "".join(f"<li>{html.escape(str(v))}</li>" for v in value)
            return f"<td><ul>{items}</ul></td>"
        return f"<td>{html.escape(str(value)) if value else ''}</td>"


_recorder = None


def get_recorder():
    """Return the process-wide singleton recorder, creating it on first use."""
    global _recorder
    if _recorder is None:
        _recorder = ProgressRecorder()
    return _recorder


_row_var = contextvars.ContextVar("doi_downloader_progress_row", default=None)
_fetch_stage_var = contextvars.ContextVar("doi_downloader_progress_fetch_stage", default=False)


class active_row:
    """Marks (recorder, doi, plugin_name) as the target for record_* calls made in this scope.

    A no-op context manager when `recorder` is None, so it's safe to wrap every
    plugin call in this even when progress reporting is disabled.
    """

    def __init__(self, recorder, doi, plugin_name):
        self._active = recorder is not None
        self._value = (recorder, doi, plugin_name)
        self._token = None

    def __enter__(self):
        if self._active:
            self._token = _row_var.set(self._value)
        return self

    def __exit__(self, *exc_info):
        if self._active:
            _row_var.reset(self._token)


class fetch_scope:
    """Marks calls to lib.get_page_with_requests/robot_access_allowed as fetch-stage events.

    Needed because both the metadata fetch and the PDF download go through the
    same shared request helpers in lib.py; only calls made while a fetch_scope
    is active are recorded via record_fetch.
    """

    def __enter__(self):
        self._token = _fetch_stage_var.set(True)
        return self

    def __exit__(self, *exc_info):
        _fetch_stage_var.reset(self._token)


def record_cache(status, result):
    row = _row_var.get()
    if row is None:
        return
    recorder, doi, plugin_name = row
    recorder.record_cache(doi, plugin_name, status, result)


def record_fetch(status, url):
    if not _fetch_stage_var.get():
        return
    row = _row_var.get()
    if row is None:
        return
    recorder, doi, plugin_name = row
    recorder.record_fetch(doi, plugin_name, status, url)


def record_pdf_access(status, url):
    row = _row_var.get()
    if row is None:
        return
    recorder, doi, plugin_name = row
    recorder.record_pdf_access(doi, plugin_name, status, url)


def record_pdf_file(filepath):
    row = _row_var.get()
    if row is None:
        return
    recorder, doi, plugin_name = row
    recorder.record_pdf_file(doi, plugin_name, filepath)
