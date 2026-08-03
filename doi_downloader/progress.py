"""Collects per-(doi, plugin) download progress and renders it as an HTML table.

The table shows one row per distinct (doi, plugin, fetch result) triple, since
fetch_metadata may visit more than one webpage while searching for PDF links;
a (doi, plugin) pair with no fetch result yet gets a single row with empty
fetch cells instead.

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
    disk_status: str = None  # None: not recorded yet, distinct from an explicit SKIPPED
    disk_result: str = None  # single file path, or None: at most one disk file is ever checked
    cache_status: str = None  # None: not recorded yet, distinct from an explicit SKIPPED
    cache_result: list = field(default_factory=list)
    fetch_status: list = field(default_factory=list)
    fetch_result: list = field(default_factory=list)
    # pdf_url_fetch_map: fetch url -> [pdf urls found on that page], from ArticleDataObject.
    # pdf_access_*: fetch url -> [values], one entry per pdf url tried that came from that fetch.
    pdf_url_fetch_map: dict = field(default_factory=dict)
    pdf_access_status: dict = field(default_factory=dict)
    pdf_access_urls: dict = field(default_factory=dict)
    pdf_access_files: dict = field(default_factory=dict)


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
        row.disk_result = result

    def record_cache(self, doi, plugin_name, status, result):
        row = self._row(doi, plugin_name)
        row.cache_status = status
        row.cache_result = list(result) if result else []

    def record_fetch(self, doi, plugin_name, status, url):
        row = self._row(doi, plugin_name)
        row.fetch_status.append(status)
        row.fetch_result.append(url or "")

    def record_pdf_url_map(self, doi, plugin_name, mapping):
        row = self._row(doi, plugin_name)
        row.pdf_url_fetch_map = mapping

    @staticmethod
    def _fetch_url_for(row, pdf_url):
        """Which fetch url a pdf_url was found on, per the plugin's ArticleDataObject.

        pdf_urls is None for a fetch url that was inaccessible (no pdf links were
        ever possible to find there), so it's skipped rather than iterated.
        """
        for fetch_url, pdf_urls in row.pdf_url_fetch_map.items():
            if pdf_urls and pdf_url in pdf_urls:
                return fetch_url
        return None

    def record_pdf_access(self, doi, plugin_name, status, url):
        row = self._row(doi, plugin_name)
        fetch_url = self._fetch_url_for(row, url)
        row.pdf_access_status.setdefault(fetch_url, []).append(status)
        row.pdf_access_urls.setdefault(fetch_url, []).append(url or "")

    def record_pdf_file(self, doi, plugin_name, url, filepath):
        row = self._row(doi, plugin_name)
        fetch_url = self._fetch_url_for(row, url)
        row.pdf_access_files.setdefault(fetch_url, []).append(filepath)

    def to_html(self):
        header = "".join(f"<th>{html.escape(c)}</th>" for c in _COLUMNS)
        rows_html = "".join(self._rows_html(row) for row in self._rows.values())
        return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>doi_downloader progress</title>
<style>
body {{ font-family: sans-serif; font-size: 13px; margin: 0; }}
.table-wrap {{ overflow-x: auto; width: 100%; box-sizing: border-box; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{
    border: 1px solid #ccc; vertical-align: top; text-align: left;
    min-width: 160px; overflow-wrap: anywhere;
}}
th {{ padding: 4px 8px; background: #f0f0f0; position: sticky; top: 0; white-space: nowrap; }}
td {{ padding: 4px 8px; }}
td.multi {{ padding: 0; }}
td.multi span {{ display: block; padding: 4px 8px; }}
.status-success {{ background: #e6f4ea; }}
.status-failed {{ background: #fdecea; }}
.status-skipped {{ background: #eeeeee; }}
</style></head>
<body><div class="table-wrap"><table>
<thead><tr>{header}</tr></thead><tbody>{rows_html}</tbody>
</table></div></body></html>"""

    def _rows_html(self, row):
        """One <tr> per distinct (fetch_status, fetch_result) pair seen for this (doi, plugin),
        or a single row with empty fetch cells if fetch_metadata hasn't produced a result yet."""
        seen = set()
        fetch_events = []
        for status, url in zip(row.fetch_status, row.fetch_result):
            event = (status, url)
            if event not in seen:
                seen.add(event)
                fetch_events.append(event)
        if not fetch_events:
            fetch_events = [(None, None)]
        return "".join(self._row_html(row, fetch_status, fetch_url) for fetch_status, fetch_url in fetch_events)

    def _row_html(self, row, fetch_status, fetch_result):
        # Each row is one specific fetch (fetch_result = that page's url), and
        # pdf_access_* is keyed by the same fetch url, so this is an exact match:
        # a failed fetch never appears as a key (it produced no pdf urls to try),
        # and coreacuk-style pages that yield several pdf urls from one fetch
        # naturally keep those urls together on that fetch's single row.
        if fetch_result is None:
            # No fetch happened this run (cache hit, or CACHE_ONLY): there's no
            # specific fetch to attribute pdf-access data to, so show all of it.
            pdf_access_status = [s for statuses in row.pdf_access_status.values() for s in statuses]
            pdf_access_urls = [u for urls in row.pdf_access_urls.values() for u in urls]
            pdf_access_files = [f for files in row.pdf_access_files.values() for f in files]
            files_value = pdf_access_files
            files_status = STATUS_SUCCESS if pdf_access_files else None
        elif fetch_result not in row.pdf_url_fetch_map:
            # This page was never searched for pdf links at all (e.g. the plugin
            # doesn't track this url), so nothing was ever attempted: SKIPPED.
            pdf_access_status = STATUS_SKIPPED
            pdf_access_urls = []
            files_value = None
            files_status = STATUS_SKIPPED
        elif row.pdf_url_fetch_map[fetch_result] is None:
            # This page could not be accessed at all (blocked, network/HTTP
            # error, ...), so no pdf-link search was even possible there. Leave
            # blank rather than repeating the failure fetch_status already shows.
            pdf_access_status = None
            pdf_access_urls = []
            files_value = None
            files_status = None
        elif not row.pdf_url_fetch_map[fetch_result]:
            # This page was fetched and searched for pdf links, but had none:
            # distinct from both cases above, since a check genuinely happened.
            pdf_access_status = STATUS_NOT_FOUND
            pdf_access_urls = []
            files_value = None
            files_status = STATUS_NOT_FOUND
        else:
            pdf_access_status = row.pdf_access_status.get(fetch_result, [])
            pdf_access_urls = row.pdf_access_urls.get(fetch_result, [])
            pdf_access_files = row.pdf_access_files.get(fetch_result, [])
            if pdf_access_files:
                files_value, files_status = pdf_access_files, STATUS_SUCCESS
            else:
                # candidate pdf urls existed and were tried, but none was downloadable:
                # leave blank rather than repeating the failure pdf access status shows.
                files_value, files_status = None, None

        cells = "".join([
            self._cell(row.doi), self._cell(row.plugin_name),
            self._status_cell(row.disk_status), self._result_cell(row.disk_result, row.disk_status),
            self._status_cell(row.cache_status), self._result_cell(row.cache_result, row.cache_status),
            self._status_cell(fetch_status), self._result_cell(fetch_result, fetch_status),
            self._status_cell(pdf_access_status), self._result_cell(pdf_access_urls, pdf_access_status),
            self._result_cell(files_value, files_status, as_list=False),
        ])
        return f"<tr>{cells}</tr>"

    @staticmethod
    def _status_class(status):
        """Classify a finished status for coloring; None/empty (not recorded yet)
        stays uncolored, so an unprocessed cell is visually distinct from a
        finished one -- including one that was explicitly skipped."""
        if not status:
            return None
        if status.startswith(STATUS_SUCCESS):
            return "status-success"
        failed_prefixes = (STATUS_NOT_FOUND, STATUS_ACCESS_ERROR)
        if status.startswith(failed_prefixes):
            return "status-failed"
        if status.startswith(STATUS_SKIPPED):
            return "status-skipped"
        return None

    @classmethod
    def _span(cls, value, status):
        css = cls._status_class(status)
        css_attr = f' class="{css}"' if css else ""
        return f"<span{css_attr}>{html.escape(str(value))}</span>"

    @staticmethod
    def _cell(value):
        if isinstance(value, list):
            if not value:
                return "<td></td>"
            text = " ".join(html.escape(str(v)) for v in value)
            return f"<td>{text}</td>"
        return f"<td>{html.escape(str(value)) if value else ''}</td>"

    @classmethod
    def _status_cell(cls, status):
        """Render a status cell, colored by its own value(s)."""
        if isinstance(status, list):
            if not status:
                return "<td></td>"
            spans = " ".join(cls._span(s, s) for s in status)
            return f'<td class="multi">{spans}</td>'
        css = cls._status_class(status)
        css_attr = f' class="{css}"' if css else ""
        text = html.escape(str(status)) if status else ""
        return f"<td{css_attr}>{text}</td>"

    @classmethod
    def _result_cell(cls, value, statuses, as_list=True):
        """Render a result cell, colored using the paired status(es) rather than its own text.

        as_list=False renders a list value as a single plain cell (joining entries
        with ", " in the rare case there's more than one), for columns that in
        practice never hold more than one item.
        """
        if isinstance(value, list) and not as_list:
            value = ", ".join(str(v) for v in value) if value else None
        if isinstance(value, list):
            if not value:
                # A single paired status (e.g. cache_status) still applies even
                # when there's nothing to list, so NOT_FOUND/ACCESS_ERROR/etc.
                # colors an empty result cell the same way a scalar one would.
                css = cls._status_class(statuses) if not isinstance(statuses, list) else None
                css_attr = f' class="{css}"' if css else ""
                return f"<td{css_attr}></td>"
            spans = []
            for i, v in enumerate(value):
                status = statuses[i] if isinstance(statuses, list) and i < len(statuses) else statuses
                spans.append(cls._span(v, status))
            return f'<td class="multi">{" ".join(spans)}</td>'
        css = cls._status_class(statuses)
        css_attr = f' class="{css}"' if css else ""
        text = html.escape(str(value)) if value else ""
        return f"<td{css_attr}>{text}</td>"


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


def record_pdf_url_map(mapping):
    row = _row_var.get()
    if row is None:
        return
    recorder, doi, plugin_name = row
    recorder.record_pdf_url_map(doi, plugin_name, mapping)


def record_pdf_access(status, url):
    row = _row_var.get()
    if row is None:
        return
    recorder, doi, plugin_name = row
    recorder.record_pdf_access(doi, plugin_name, status, url)


def record_pdf_file(url, filepath):
    row = _row_var.get()
    if row is None:
        return
    recorder, doi, plugin_name = row
    recorder.record_pdf_file(doi, plugin_name, url, filepath)
