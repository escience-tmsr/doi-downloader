from doi_downloader import loader as ld
from doi_downloader import pdf_download as pdf_dl
import os

plugins = ld.plugins

def download(doi, output_dir=".", force_download=False):
    if not doi:
        raise ValueError("DOI cannot be empty.")
    os.makedirs(output_dir, exist_ok=True)
    if not force_download and os.path.exists(os.path.join(output_dir, f"{doi}.pdf")):
        print(f"File already exists: {os.path.join(output_dir, f'{doi}.pdf')}")
        return os.path.join(output_dir, f"{doi}.pdf")

    downloaded_file = None

    for name, plugin in plugins.items():
        url = plugin.get_pdf_url(doi)
        if url:
            # Sanitize DOI for filename
            safe_filename = doi.replace("/", "_").replace(".", "_") + ".pdf"
            print(f"Plugin: {name},  doi:{doi},  url: {url}")
            downloaded_file = pdf_dl.download_pdf(url, safe_filename, output_dir)
            continue

    return downloaded_file
