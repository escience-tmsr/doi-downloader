import os
import requests
from . import config

# Function to check if file is a PDF file
def is_valid_pdf(filename):
    try:
        with open(filename, 'rb') as f:
            header = f.read(4)
            return header == b'%PDF'
    except Exception:
        return False

# Function to download PDF
def download_pdf(pdf_url, filename, directory="."):
    response = requests.get(pdf_url, headers=config.headers)
    if response.status_code == 200:
        full_path = os.path.join(directory, filename)
        with open(full_path, "wb") as f:
            f.write(response.content)

        # Check if the downloaded file is a valid PDF
        if is_valid_pdf(full_path):
            return full_path
        else:
            os.remove(full_path)
            return False

    return False

