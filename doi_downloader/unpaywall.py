import requests
import os

# Read API keys and other sensitive data from environment variables
UNPAYWALL_EMAIL = None
UNPAYWALL_API_URL = "https://api.unpaywall.org/v2/{doi}?email={email}"
headers = {
    'User-Agent': "Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/81.0"
}

# Function to set the email for the Unpaywall API
def set_email(email):
    global UNPAYWALL_EMAIL
    UNPAYWALL_EMAIL = email

# Function to get the URL of the PDF from the DOI
def get_url(doi):
    if not UNPAYWALL_EMAIL:
        raise EnvironmentError("Please make sure email is set using set_email().")

    # Make the request to the Unpaywall API
    unpaywall_api_url = UNPAYWALL_API_URL.format(doi=doi, email=UNPAYWALL_EMAIL)
    print(f"Checking {unpaywall_api_url}...")
    response = requests.get(unpaywall_api_url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if "best_oa_location" in data and data["best_oa_location"]:
            pdf_url = data["best_oa_location"]["url_for_pdf"]
            return pdf_url
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
        return download_pdf(pdf_url, f"{doi.replace('/', '_')}.pdf")
    return False

def download_from_dois(dois):
    urls = get_urls(dois)
    files = {}
    for doi, pdf_url in urls.items():
        if pdf_url:
            file_path = download_pdf(pdf_url, f"{doi.replace('/', '_')}.pdf")
            if file_path:
                files[doi] = { "doi": doi, "url": pdf_url, "file_path": file_path }
            else:
                files[doi] = False
    return files
        

# Function to download PDF
def download_pdf(pdf_url, filename, directory="."):
    response = requests.get(pdf_url, headers=headers)
    if response.status_code == 200:
        full_path = os.path.join(directory, filename)
        with open(full_path, "wb") as f:
            f.write(response.content)
        return full_path
    return False

