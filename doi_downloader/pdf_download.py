import os

from requests.exceptions import ConnectionError, ConnectTimeout, HTTPError, TooManyRedirects

from doi_downloader import config
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
        return False
    try:
        response = get_page_with_requests(pdf_url, headers=config.headers, plugin_name=plugin_name, timeout=30)
        response.raise_for_status()
    except ConnectTimeout:
        print(f"[{plugin_name}] connection timeout for pdf download")
        response = None
    except HTTPError:
        print(f"[{plugin_name}] access error for pdf download")
        response = None
    except (ConnectionError, TooManyRedirects) as e:
        print(f"[{plugin_name}] pdf download failed for {plugin_name}: {e}")
        response = None
    if not response or response.status_code != 200:
        return False

    full_path = os.path.join(directory, filename)
    with open(full_path, "wb") as f:
        f.write(response.content)

    # Check if the downloaded file is a valid PDF
    if not is_valid_pdf(full_path):
        os.remove(full_path)
        return False

    return full_path
