import os
import time
from operator import itemgetter
from pathlib import Path

from doi_downloader import loader as ld
from doi_downloader import pdf_download as pdf_dl
from doi_downloader import progress
from doi_downloader.benchmark import BenchmarkLogger

plugins = ld.plugins

# Initialize benchmark logger
benchmark_logger = BenchmarkLogger("benchmark/logs/benchmark_log.jsonl")


def sanitize_doi(doi):
    """Replace slashes and periods in doi by underscores"""
    return doi.replace("/", "_").replace(".", "_")


def _refresh_progress_view(recorder):
    from doi_downloader import progress_browser
    progress_browser.get_browser_view().update(recorder.to_html())


def download(doi, output_dir=".", force_download=False,
             journal_domain=None, enable_benchmark=True, show_progress=False):
    """
    Download PDF with optional benchmarking and live progress reporting

    Args:
        doi: DOI identifier
        output_dir: Output directory for PDF
        force_download: Skip cache check
        journal_domain: Journal/domain name for analytics
        enable_benchmark: Enable performance tracking
        show_progress: Show a live per-plugin progress table in a Playwright browser tab.
            The tab is opened lazily on first use and stays open across calls, so a batch
            of download() calls accumulates one growing table.
    """
    if not doi:
        raise ValueError("DOI cannot be empty.")

    os.makedirs(output_dir, exist_ok=True)

    recorder = progress.get_recorder() if show_progress else None

    safe_filename = sanitize_doi(doi) + ".pdf"
    target_path = os.path.join(output_dir, safe_filename)
    file_exists = os.path.exists(target_path)

    if force_download:
        disk_status, disk_result = progress.STATUS_SKIPPED, None
    elif file_exists:
        disk_status, disk_result = progress.STATUS_SUCCESS, os.path.abspath(target_path)
    else:
        disk_status, disk_result = progress.STATUS_NOT_FOUND, None

    if recorder:
        for plugin_name in sorted(plugins):
            recorder.record_disk(doi, plugin_name, disk_status, disk_result)

    if not force_download and file_exists:
        print(f"File already exists: {target_path}")
        if recorder:
            for plugin_name in sorted(plugins):
                recorder.record_cache(doi, plugin_name, progress.STATUS_SKIPPED, [])
                recorder.record_fetch(doi, plugin_name, progress.STATUS_SKIPPED, None)
                recorder.record_pdf_access(doi, plugin_name, progress.STATUS_SKIPPED, None)
            _refresh_progress_view(recorder)
        return target_path

    downloaded_file = None

    for plugin_name, plugin in sorted(plugins.items(), key=itemgetter(0)):
        # Create attempt record if benchmarking is enabled
        attempt = None
        start_time = None

        if enable_benchmark:
            attempt = benchmark_logger.create_attempt(doi, plugin_name, journal_domain)
            start_time = time.time()

        try:
            with progress.active_row(recorder, doi, plugin_name):
                # Call plugin with original signature (no ctx parameter)
                urls = plugin.get_pdf_urls(doi)

                if urls:
                    # Mark URL resolution success
                    if attempt:
                        attempt.url_resolved = True
                        attempt.resolved_url = urls[0]

                    print(f"Plugin: {plugin_name},  doi:{doi},  url: {urls[0]}")
                    downloaded_file = pdf_dl.download_first_available_pdf(
                        urls, safe_filename, directory=output_dir, plugin_name=plugin_name
                    )

                    if downloaded_file:
                        # Mark download success
                        if attempt:
                            attempt.pdf_downloaded = True
                            if Path(downloaded_file).exists():
                                attempt.file_size_bytes = Path(downloaded_file).stat().st_size

        except Exception as e:
            # Log error if benchmarking
            if attempt:
                attempt.error_message = str(e)

        finally:
            # Log the attempt with duration
            if attempt:
                attempt.duration_ms = round((time.time() - start_time) * 1000, 2)
                benchmark_logger.log_attempt(attempt)
            if recorder:
                _refresh_progress_view(recorder)

        if downloaded_file:
            break

    return downloaded_file
