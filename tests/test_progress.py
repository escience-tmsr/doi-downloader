import pytest

from doi_downloader import progress
from doi_downloader.progress import (
    STATUS_ACCESS_ERROR,
    STATUS_NOT_FOUND,
    STATUS_SKIPPED,
    STATUS_SUCCESS,
    ProgressRecorder,
    active_row,
    fetch_scope,
    get_recorder,
    record_cache,
    record_fetch,
    record_pdf_access,
    record_pdf_file,
    record_pdf_url_map,
)

DOI = "10.1000/example"
PLUGIN = "ExamplePlugin"


@pytest.fixture(autouse=True)
def reset_singleton_recorder():
    # get_recorder() is a process-wide singleton; isolate tests from each other.
    progress._recorder = None
    yield
    progress._recorder = None


# --- get_recorder singleton ---


def test_get_recorder_returns_singleton():
    first = get_recorder()
    second = get_recorder()
    assert first is second
    assert isinstance(first, ProgressRecorder)


# --- free functions are no-ops without an active row ---


def test_record_functions_do_nothing_without_active_row():
    record_cache(STATUS_SUCCESS, ["http://example.com/a.pdf"])
    record_fetch(STATUS_SUCCESS, "http://example.com")
    record_pdf_url_map({"http://example.com": ["http://example.com/a.pdf"]})
    record_pdf_access(STATUS_SUCCESS, "http://example.com/a.pdf")
    record_pdf_file("http://example.com/a.pdf", "/tmp/a.pdf")
    # nothing to assert: absence of an exception, and no recorder was ever created
    assert progress._recorder is None


def test_active_row_with_none_recorder_is_a_noop():
    with active_row(None, DOI, PLUGIN), fetch_scope():
        record_fetch(STATUS_SUCCESS, "http://example.com")
    assert progress._recorder is None


# --- active_row / fetch_scope context management ---


def test_record_fetch_is_ignored_outside_fetch_scope():
    recorder = ProgressRecorder()
    with active_row(recorder, DOI, PLUGIN):
        record_fetch(STATUS_SUCCESS, "http://example.com")  # no fetch_scope active
    row = recorder._row(DOI, PLUGIN)
    assert row.fetch_status == []
    assert row.fetch_result == []


def test_record_fetch_is_recorded_inside_fetch_scope():
    recorder = ProgressRecorder()
    with active_row(recorder, DOI, PLUGIN), fetch_scope():
        record_fetch(STATUS_SUCCESS, "http://example.com")
    row = recorder._row(DOI, PLUGIN)
    assert row.fetch_status == [STATUS_SUCCESS]
    assert row.fetch_result == ["http://example.com"]


def test_nested_active_row_restores_outer_context_on_exit():
    outer_recorder = ProgressRecorder()
    inner_recorder = ProgressRecorder()
    with active_row(outer_recorder, "doi-outer", "plugin-outer"):
        with active_row(inner_recorder, "doi-inner", "plugin-inner"), fetch_scope():
            record_fetch(STATUS_SUCCESS, "http://inner")
        with fetch_scope():
            record_fetch(STATUS_SUCCESS, "http://outer")

    inner_row = inner_recorder._row("doi-inner", "plugin-inner")
    outer_row = outer_recorder._row("doi-outer", "plugin-outer")
    assert inner_row.fetch_result == ["http://inner"]
    assert outer_row.fetch_result == ["http://outer"]


def test_fetch_scope_reset_stops_recording_afterwards():
    recorder = ProgressRecorder()
    with active_row(recorder, DOI, PLUGIN):
        with fetch_scope():
            record_fetch(STATUS_SUCCESS, "http://during-scope")
        record_fetch(STATUS_SUCCESS, "http://after-scope")
    row = recorder._row(DOI, PLUGIN)
    assert row.fetch_result == ["http://during-scope"]


# --- individual record_* free functions route to the active row ---


def test_record_cache_pdf_url_map_access_and_file():
    recorder = ProgressRecorder()
    with active_row(recorder, DOI, PLUGIN):
        record_cache(STATUS_SUCCESS, ["http://pdf1"])
        record_pdf_url_map({"http://fetch1": ["http://pdf1"]})
        record_pdf_access(STATUS_SUCCESS, "http://pdf1")
        record_pdf_file("http://pdf1", "/abs/path.pdf")

    row = recorder._row(DOI, PLUGIN)
    assert row.cache_status == STATUS_SUCCESS
    assert row.cache_result == ["http://pdf1"]
    assert row.pdf_url_fetch_map == {"http://fetch1": ["http://pdf1"]}
    assert row.pdf_access_status == {"http://fetch1": [STATUS_SUCCESS]}
    assert row.pdf_access_urls == {"http://fetch1": ["http://pdf1"]}
    assert row.pdf_access_files == {"http://fetch1": ["/abs/path.pdf"]}


def test_fetch_url_for_skips_non_matching_entries_before_finding_the_match():
    recorder = ProgressRecorder()
    with active_row(recorder, DOI, PLUGIN):
        record_pdf_url_map(
            {
                "http://page-without-it": ["http://other.pdf"],
                "http://page-with-it": ["http://pdf1"],
            }
        )
        record_pdf_access(STATUS_SUCCESS, "http://pdf1")
    row = recorder._row(DOI, PLUGIN)
    assert row.pdf_access_status == {"http://page-with-it": [STATUS_SUCCESS]}


def test_record_cache_defaults_none_result_to_empty_list():
    recorder = ProgressRecorder()
    recorder.record_cache(DOI, PLUGIN, STATUS_NOT_FOUND, None)
    row = recorder._row(DOI, PLUGIN)
    assert row.cache_result == []


# --- ProgressRecorder._row reuses an existing entry per (doi, plugin) ---


def test_row_is_reused_for_same_doi_and_plugin():
    recorder = ProgressRecorder()
    recorder.record_disk(DOI, PLUGIN, STATUS_NOT_FOUND, None)
    recorder.record_cache(DOI, PLUGIN, STATUS_NOT_FOUND, [])
    assert len(recorder._rows) == 1


def test_different_plugins_for_same_doi_get_separate_rows():
    recorder = ProgressRecorder()
    recorder.record_disk(DOI, "PluginA", STATUS_NOT_FOUND, None)
    recorder.record_disk(DOI, "PluginB", STATUS_NOT_FOUND, None)
    assert len(recorder._rows) == 2


# --- _status_class classification ---


@pytest.mark.parametrize(
    ("status", "expected_class"),
    [
        (None, None),
        ("", None),
        (STATUS_SUCCESS, "status-success"),
        (f"{STATUS_SUCCESS}: cached", "status-success"),
        (STATUS_NOT_FOUND, "status-failed"),
        (f"{STATUS_ACCESS_ERROR}: blocked by robots.txt", "status-failed"),
        (STATUS_SKIPPED, "status-skipped"),
        ("SOME_OTHER_STATUS", None),
    ],
)
def test_status_class_classification(status, expected_class):
    assert ProgressRecorder._status_class(status) == expected_class


# --- to_html rendering ---


def test_to_html_contains_header_row_and_recorded_values():
    recorder = ProgressRecorder()
    recorder.record_disk(DOI, PLUGIN, STATUS_NOT_FOUND, None)
    html_out = recorder.to_html()
    assert "<th>DOI</th>" in html_out
    assert "<th>plugin</th>" in html_out
    assert DOI in html_out
    assert PLUGIN in html_out


def test_to_html_escapes_values():
    recorder = ProgressRecorder()
    recorder.record_disk("<script>doi</script>", PLUGIN, STATUS_SUCCESS, "/tmp/a&b.pdf")
    html_out = recorder.to_html()
    assert "<script>doi</script>" not in html_out
    assert "&lt;script&gt;doi&lt;/script&gt;" in html_out
    assert "a&amp;b.pdf" in html_out


def test_to_html_with_no_rows_still_renders_table():
    recorder = ProgressRecorder()
    html_out = recorder.to_html()
    assert "<table>" in html_out
    assert "<tbody></tbody>" in html_out


def test_row_with_no_fetch_events_renders_a_single_row():
    recorder = ProgressRecorder()
    recorder.record_disk(DOI, PLUGIN, STATUS_NOT_FOUND, None)
    html_out = recorder.to_html()
    assert html_out.count("<tr>") == 2  # header + one data row


def test_distinct_fetch_events_render_separate_rows():
    recorder = ProgressRecorder()
    recorder.record_fetch(DOI, PLUGIN, STATUS_SUCCESS, "http://a")
    recorder.record_fetch(DOI, PLUGIN, STATUS_SUCCESS, "http://b")
    html_out = recorder.to_html()
    assert html_out.count("<tr>") == 3  # header + two distinct fetch rows


def test_duplicate_fetch_events_are_deduplicated_into_one_row():
    recorder = ProgressRecorder()
    recorder.record_fetch(DOI, PLUGIN, STATUS_SUCCESS, "http://a")
    recorder.record_fetch(DOI, PLUGIN, STATUS_SUCCESS, "http://a")
    html_out = recorder.to_html()
    assert html_out.count("<tr>") == 2  # header + one deduplicated row


# --- pdf-access branches in _row_html, exercised via record_* + to_html ---


def test_pdf_access_when_no_fetch_happened_aggregates_across_fetch_urls():
    # Cache hit: no record_fetch call at all, so fetch_result is None and
    # every recorded pdf_access entry (regardless of which fetch url it maps
    # to) should be shown together.
    recorder = ProgressRecorder()
    recorder.record_cache(DOI, PLUGIN, STATUS_SUCCESS, ["http://pdf1"])
    recorder.record_pdf_access(DOI, PLUGIN, STATUS_SUCCESS, "http://pdf1")
    recorder.record_pdf_file(DOI, PLUGIN, "http://pdf1", "/abs/pdf1.pdf")
    html_out = recorder.to_html()
    assert "http://pdf1" in html_out
    assert "/abs/pdf1.pdf" in html_out
    assert html_out.count("<tr>") == 2


def test_pdf_access_skipped_when_fetch_url_was_never_checked_for_links():
    recorder = ProgressRecorder()
    recorder.record_fetch(DOI, PLUGIN, STATUS_SUCCESS, "http://page1")
    # no record_pdf_url_map call for http://page1 at all
    html_out = recorder.to_html()
    assert STATUS_SKIPPED in html_out


def test_pdf_access_blank_when_fetch_url_was_inaccessible():
    recorder = ProgressRecorder()
    recorder.record_fetch(DOI, PLUGIN, f"{STATUS_ACCESS_ERROR}: HTTP error 500", "http://page2")
    recorder.record_pdf_url_map(DOI, PLUGIN, {"http://page2": None})
    html_out = recorder.to_html()
    # the fetch failure is shown once (in the fetch column) but not repeated
    # as a pdf-access status
    assert html_out.count(f"{STATUS_ACCESS_ERROR}: HTTP error 500") == 1


def test_pdf_access_not_found_when_page_had_no_pdf_links():
    recorder = ProgressRecorder()
    recorder.record_fetch(DOI, PLUGIN, STATUS_SUCCESS, "http://page3")
    recorder.record_pdf_url_map(DOI, PLUGIN, {"http://page3": []})
    html_out = recorder.to_html()
    assert STATUS_NOT_FOUND in html_out


def test_pdf_access_shows_tried_urls_and_status_for_matching_fetch():
    recorder = ProgressRecorder()
    recorder.record_fetch(DOI, PLUGIN, STATUS_SUCCESS, "http://page4")
    recorder.record_pdf_url_map(DOI, PLUGIN, {"http://page4": ["http://pdf4"]})
    recorder.record_pdf_access(DOI, PLUGIN, STATUS_NOT_FOUND, "http://pdf4")
    html_out = recorder.to_html()
    assert "http://pdf4" in html_out
    # tried but no file was ever downloaded for it
    assert "/abs/pdf4.pdf" not in html_out


def test_pdf_access_shows_downloaded_file_for_matching_fetch():
    recorder = ProgressRecorder()
    recorder.record_fetch(DOI, PLUGIN, STATUS_SUCCESS, "http://page5")
    recorder.record_pdf_url_map(DOI, PLUGIN, {"http://page5": ["http://pdf5"]})
    recorder.record_pdf_access(DOI, PLUGIN, STATUS_SUCCESS, "http://pdf5")
    recorder.record_pdf_file(DOI, PLUGIN, "http://pdf5", "/abs/pdf5.pdf")
    html_out = recorder.to_html()
    assert "/abs/pdf5.pdf" in html_out


# --- _cell / _status_cell / _result_cell rendering helpers ---


def test_cell_renders_empty_list_and_falsy_scalar_as_blank():
    assert ProgressRecorder._cell([]) == "<td></td>"
    assert ProgressRecorder._cell(None) == "<td></td>"
    assert ProgressRecorder._cell("") == "<td></td>"


def test_cell_renders_nonempty_list_joined():
    assert ProgressRecorder._cell(["a", "b"]) == "<td>a b</td>"


def test_status_cell_renders_empty_list_as_blank():
    assert ProgressRecorder._status_cell([]) == "<td></td>"


def test_status_cell_renders_list_of_statuses_as_multi():
    out = ProgressRecorder._status_cell([STATUS_SUCCESS, STATUS_NOT_FOUND])
    assert 'class="multi"' in out
    assert "status-success" in out
    assert "status-failed" in out


def test_result_cell_as_list_false_joins_multiple_values():
    out = ProgressRecorder._result_cell(["/a.pdf", "/b.pdf"], STATUS_SUCCESS, as_list=False)
    assert "/a.pdf, /b.pdf" in out
    assert "status-success" in out


def test_result_cell_empty_list_still_colors_using_scalar_status():
    out = ProgressRecorder._result_cell([], STATUS_NOT_FOUND)
    assert "status-failed" in out
