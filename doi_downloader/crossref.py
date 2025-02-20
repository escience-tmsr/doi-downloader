import requests
from .cache_duckdb import Cache
from . import article_dataobject as ado # import ArticleDataObject

# Read API keys and other sensitive data from environment variables
CROSSREF_API_URL = "https://api.crossref.org/works/{doi}"
cache = Cache("database.db", "crossref")

def fetch_metadata(doi):
    url = CROSSREF_API_URL.format(doi=doi)
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        data = response.json()
        if "message" not in data:
            # print(f"No metadata found for DOI: {doi}")
            return None

        dataObj = ado.ArticleDataObject.from_crossref_json(data)
        dataObj.validate()
        return dataObj

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def get_pdf_url(doi, use_cache=True, ttl=0):
    if use_cache:
        # Check the cache first
        cached_data = cache.get_cache(doi, ttl=ttl)
        if cached_data:
            # print(f"Using cached data for {doi}.")
            data_object = ado.ArticleDataObject.from_json(cached_data)
            data_object.validate()
            return data_object.get_pdf_link()

    metadata = fetch_metadata(doi)
    if metadata: 
        if use_cache:
            cache.set_cache(doi, metadata.to_json())
            # print(f"Data cached for {doi}.")
        return metadata.get_pdf_link()
    else:
        return None

