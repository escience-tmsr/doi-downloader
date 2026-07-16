import os
import pypdf
from doi_downloader import config
from doi_downloader.lib import robot_access_allowed, get_page_with_requests
from requests.exceptions import ConnectionError, HTTPError, TooManyRedirects

# Function to check if file is a PDF file
def is_valid_pdf(filename):
    try:
        with open(filename, 'rb') as f:
            header = f.read(4)
            return header == b'%PDF'
    except Exception:
        return False



def verify_pdf(filename, target_doi, plugin_name=None):
    """verify_pdf: find search_string in PDF file stored on disk, Claude code"""
    with open(filename, "rb") as infile:
        reader = pypdf.PdfReader(infile)
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if target_doi.lower() in text.lower():
                print(f"[{plugin_name}] ✅ Found DOI in PDF on page {page_num + 1}")
                return True
    if False:
        print(f"[{plugin_name}] Remark: DOI not found in PDF")
    return False


# Function to download PDF
def download_pdf(pdf_url, filename, directory=".", plugin_name=None, doi="not_a_doi_value"):
    if not pdf_url:
        return False, False
    if not robot_access_allowed(pdf_url, plugin_name=plugin_name):
        print(f"[{plugin_name}] robots.txt denied download access to {pdf_url}")
        return False, False
    try:
        response = get_page_with_requests(pdf_url, params=config.headers, plugin_name=plugin_name, timeout=30)
        response.raise_for_status()
    except (ConnectionError, HTTPError, TooManyRedirects) as e:
        print(f"[{plugin_name}] Request failed for {plugin_name}: {e}")
        response = None
    if response and response.status_code == 200:
        full_path = os.path.join(directory, filename)
        with open(full_path, "wb") as f:
            f.write(response.content)

        # Check if the downloaded file is a valid PDF
        if is_valid_pdf(full_path):
            pdf_has_doi = verify_pdf(full_path, doi, plugin_name)
            return full_path, pdf_has_doi
        else:
            os.remove(full_path)
            return False, False

    return False, False

