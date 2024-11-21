import requests
import json
from . import config
from . import pdf_download as pdf
from .cache import Cache

# Read API keys and other sensitive data from environment variables
UNPAYWALL_EMAIL = None
UNPAYWALL_API_URL = "https://api.unpaywall.org/v2/{doi}?email={email}"
cache = Cache("unpaywall_cache.db")

# Function to set the email for the Unpaywall API
def set_email(email):
    global UNPAYWALL_EMAIL
    UNPAYWALL_EMAIL = email

def check_cache(doi):
    return cache.get_cache(doi)

def get_number_of_cached_404():
    return cache.get_count_of_value({'code': 404})

def get_list_with_no_urls():
    records = cache.get_all_cache()
    return [record for record in records if not _extract_url(json.loads(record[1]))]

def get_number_of_cached():
    return cache.get_count_all()

def _extract_url(data):
    if "best_oa_location" in data and data["best_oa_location"]:
        return data["best_oa_location"]["url_for_pdf"]
    return False

# Function to get the URL of the PDF from the DOI
def get_url(doi, use_cache=True):
    if not UNPAYWALL_EMAIL:
        raise EnvironmentError("Please make sure email is set using set_email().")
    if use_cache:
        # Check the cache first
        cached_data = check_cache(doi)
        if cached_data:
            # print(f"Using cached data for {doi}.")
            return _extract_url(cached_data)

    # Make the request to the Unpaywall API
    unpaywall_api_url = UNPAYWALL_API_URL.format(doi=doi, email=UNPAYWALL_EMAIL)
    print(f"Checking {unpaywall_api_url}...")
    response = requests.get(unpaywall_api_url, headers=config.headers)

    if response.status_code == 200:
        data = response.json()
        if use_cache:
            cache.set_cache(doi, data)
            print(f"Data cached for {doi}.")

        return _extract_url(data)
    if response.status_code == 404:
        if use_cache:
            cache.set_cache(doi, {'code': 404})

        print(f"No data found for {doi}.")
        return False
        # if "best_oa_location" in data and data["best_oa_location"]:
        #     pdf_url = data["best_oa_location"]["url_for_pdf"]
        #     return pdf_url
    if response.status_code == 429:
        raise ValueError("Rate limit.")

    return False

def get_urls(dois):
    if not UNPAYWALL_EMAIL:
        raise EnvironmentError("Please make sure email is set using set_email().")

    urls = {}
    for doi in dois:
        urls[doi] = get_url(doi)
    return urls

def download_from_doi(doi):
    pdf_url = get_url(doi)
    if pdf_url:
        return pdf.download_pdf(pdf_url, f"{doi.replace('/', '_')}.pdf")
    return False

def download_from_dois(dois):
    urls = get_urls(dois)
    files = {}
    for doi, pdf_url in urls.items():
        if pdf_url:
            file_path = pdf.download_pdf(pdf_url, f"{doi.replace('/', '_')}.pdf")
            if file_path:
                files[doi] = { "doi": doi, "url": pdf_url, "file_path": file_path }
            else:
                files[doi] = False
    return files

