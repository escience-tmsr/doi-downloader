import os

from requests.exceptions import ConnectionError, ConnectTimeout, HTTPError, TooManyRedirects

from doi_downloader import config, progress
from doi_downloader.lib import get_page_with_requests, robot_access_allowed


# Function to check if file is a PDF file
def is_valid_pdf(filename):
    try:
        with open(filename, 'rb') as f:
            header = f.read(4)
            return header == b'%PDF'
    except Exception:
        return False


# Function to download PDF
def download_pdf(pdf_url, filename, directory=".", plugin_name=None):
    """
    Download PDF file from url to filename.
    Returns: file_path: path to the downloaded file (or False if download failed).
    """

    if not pdf_url:
        return False
    if not robot_access_allowed(pdf_url, plugin_name=plugin_name):
        print(f"[{plugin_name}] robots.txt denied download access to {pdf_url}")
        progress.record_pdf_access(f"{progress.STATUS_ACCESS_ERROR}: blocked by robots.txt", pdf_url)
        return False
    try:
        response = get_page_with_requests(pdf_url, headers=config.headers, plugin_name=plugin_name, timeout=30)
        response.raise_for_status()
    except ConnectTimeout:
        print(f"[{plugin_name}] connection timeout for pdf download")
        progress.record_pdf_access(f"{progress.STATUS_ACCESS_ERROR}: connection timeout", pdf_url)
        return False
    except HTTPError:
        print(f"[{plugin_name}] access error for pdf download")
        status = progress.STATUS_NOT_FOUND if response.status_code == 404 else \
            f"{progress.STATUS_ACCESS_ERROR}: HTTP error {response.status_code}"
        progress.record_pdf_access(status, pdf_url)
        return False
    except (ConnectionError, TooManyRedirects) as e:
        print(f"[{plugin_name}] pdf download failed for {plugin_name}: {e}")
        progress.record_pdf_access(f"{progress.STATUS_ACCESS_ERROR}: {e}", pdf_url)
        return False
    if not response or response.status_code != 200:
        progress.record_pdf_access(f"{progress.STATUS_ACCESS_ERROR}: unexpected response", pdf_url)
        return False

    full_path = os.path.join(directory, filename)
    with open(full_path, "wb") as f:
        f.write(response.content)

    # Check if the downloaded file is a valid PDF
    if not is_valid_pdf(full_path):
        os.remove(full_path)
        progress.record_pdf_access(f"{progress.STATUS_ACCESS_ERROR}: downloaded content is not a valid PDF", pdf_url)
        return False

    progress.record_pdf_access(progress.STATUS_SUCCESS, pdf_url)
    progress.record_pdf_file(os.path.abspath(full_path))
    return full_path


def download_first_available_pdf(pdf_urls, filename, directory=".", plugin_name=None):
    """
    Try each candidate PDF url in order until one succeeds.
    Returns: file_path: path to the downloaded file (or False if none succeeded).
    """
    downloaded_file = None
    for pdf_url in pdf_urls:
        if downloaded_file:
            progress.record_pdf_access(progress.STATUS_SKIPPED, pdf_url)
            continue
        downloaded_file = download_pdf(pdf_url, filename, directory=directory, plugin_name=plugin_name)
    return downloaded_file
