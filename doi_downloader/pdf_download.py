import os
import requests
from . import config


# Function to download PDF
def download_pdf(pdf_url, filename, directory="."):
    response = requests.get(pdf_url, headers=config.headers)
    if response.status_code == 200:
        full_path = os.path.join(directory, filename)
        with open(full_path, "wb") as f:
            f.write(response.content)
        return full_path
    return False

