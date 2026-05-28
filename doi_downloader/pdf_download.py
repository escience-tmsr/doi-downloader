import os
import pypdf
import requests
from requests.exceptions import ConnectTimeout, ConnectionError
from . import config

# Function to check if file is a PDF file
def is_valid_pdf(filename):
    try:
        with open(filename, 'rb') as f:
            header = f.read(4)
            return header == b'%PDF'
    except Exception:
        return False


def search_pdf_for_doi(filename, target_doi):
    """search_pdf: find search_string in PDF file stored on disk, Claude code"""
    with open(filename, "rb") as infile:
        reader = pypdf.PdfReader(infile)
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if target_doi.lower() in text.lower():
                print(f"✅ Found DOI in PDF on page {page_num + 1}")
                return True
    print("Remark: DOI not found in PDF")
    return False


# Function to download PDF
def download_pdf(pdf_url, filename, directory=".", plugin_name="unknown", doi="not_a_doi_value"):
    try:
        response = requests.get(pdf_url, headers=config.headers, timeout=30)
    except (ConnectTimeout, ConnectionError) as e:
        print(f"Request failed for {plugin_name}: {e}")
        response = None
    if response and response.status_code == 200:
        full_path = os.path.join(directory, filename)
        with open(full_path, "wb") as f:
            f.write(response.content)

        # Check if the downloaded file is a valid PDF
        if is_valid_pdf(full_path):
            search_pdf_for_doi(full_path, doi)
            return full_path
        else:
            os.remove(full_path)
            return False

    return False

