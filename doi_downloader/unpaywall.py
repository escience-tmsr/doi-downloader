import requests
from .cache_duckdb import Cache
from . import article_dataobject as ado # import ArticleDataObject

# Read API keys and other sensitive data from environment variables
UNPAYWALL_EMAIL = None
UNPAYWALL_API_URL = "https://api.unpaywall.org/v2/{doi}?email={email}"
cache = Cache("database.db", "unpaywall")

# Function to set the email for the Unpaywall API
def set_email(email):
    global UNPAYWALL_EMAIL
    UNPAYWALL_EMAIL = email

def get_number_of_cached():
    return cache.get_count_all()

def fetch_metadata(doi):
    if not UNPAYWALL_EMAIL:
        raise EnvironmentError("Please make sure email is set using set_email().")
    url = UNPAYWALL_API_URL.format(doi=doi, email=UNPAYWALL_EMAIL)
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        data = response.json()
        # print(data)
        dataObj = ado.ArticleDataObject.from_unpaywall_json(data)
        return dataObj
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

# Function to get the URL of the PDF from the DOI
def get_pdf_url(doi, use_cache=True, ttl=0):
    if use_cache:
        # Check the cache first
        cached_data = cache.get_cache(doi, ttl=ttl)
        if cached_data:
            # print(f"Using cached data for {doi}.")
            data_object = ado.ArticleDataObject.from_json(cached_data)
            data_object.validate()
            return data_object.get_pdf_link()
            # return _extract_url(cached_data)

    metadata = fetch_metadata(doi)
    if metadata: 
        if use_cache:
            cache.set_cache(doi, metadata.to_json())
            # print(f"Data cached for {doi}.")
        return metadata.get_pdf_link()
    else:
        return None

