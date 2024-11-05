import requests


# Read API keys and other sensitive data from environment variables
UNPAYWALL_EMAIL = None
UNPAYWALL_API_URL = "https://api.unpaywall.org/v2/{doi}?email={email}"

# Check if necessary variables are loaded
# if not UNPAYWALL_EMAIL:
#     raise EnvironmentError("Please make sure UNPAYWALL_EMAIL are set in the .env file.")

def set_email(email):
    global UNPAYWALL_EMAIL
    UNPAYWALL_EMAIL = email


def get_url(doi):
    if not UNPAYWALL_EMAIL:
        raise EnvironmentError("Please make sure email is set using set_email().")

    # Make the request to the Unpaywall API
    response = requests.get(UNPAYWALL_API_URL.format(doi=doi, email=UNPAYWALL_EMAIL))

    if response.status_code == 200:
        data = response.json()
        if "best_oa_location" in data and data["best_oa_location"]:
            pdf_url = data["best_oa_location"]["url_for_pdf"]
            # print(f"Open access PDF for {doi}: {pdf_url}")
            return pdf_url
    return False

def download_from_doi(doi):
    pdf_url = get_url(doi)
    if pdf_url:
        return download_pdf(pdf_url, f"{doi.replace('/', '_')}.pdf")
    return False

# Function to download PDF
def download_pdf(pdf_url, filename):
    response = requests.get(pdf_url)
    if response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(response.content)
        # print(f"Downloaded PDF: {filename}")
        return True
    return False

