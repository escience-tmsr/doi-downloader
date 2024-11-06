import requests

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
    response = requests.get(UNPAYWALL_API_URL.format(doi=doi, email=UNPAYWALL_EMAIL), headers=headers)

    if response.status_code == 200:
        data = response.json()
        if "best_oa_location" in data and data["best_oa_location"]:
            pdf_url = data["best_oa_location"]["url_for_pdf"]
            return pdf_url
    return False

def download_from_doi(doi):
    pdf_url = get_url(doi)
    if pdf_url:
        return download_pdf(pdf_url, f"{doi.replace('/', '_')}.pdf")
    return False

# Function to download PDF
def download_pdf(pdf_url, filename):
    response = requests.get(pdf_url, headers=headers)
    if response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(response.content)
        return True
    return False

