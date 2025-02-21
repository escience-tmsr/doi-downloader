import requests
from doi_downloader.plugins import Plugin
from doi_downloader.cache_duckdb import Cache
from doi_downloader import article_dataobject as ado # import ArticleDataObject


# Read API keys and other sensitive data from environment variables
CROSSREF_API_URL = "https://api.crossref.org/works/{doi}"

class CrossrefPlugin(Plugin):
    def __new__(self):
        instance = super(Plugin, self).__new__(self)
        self.cache = Cache("database.db", "crossref")
        return instance

    def test(self):
        return True

    def fetch_metadata(self, doi):
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


    def get_pdf_url(self, doi, use_cache=True, ttl=0):
        if use_cache:
            # Check the cache first
            cached_data = self.cache.get_cache(doi, ttl=ttl)
            if cached_data:
                # print(f"Using cached data for {doi}.")
                data_object = ado.ArticleDataObject.from_json(cached_data)
                data_object.validate()
                return data_object.get_pdf_link()

        metadata = self.fetch_metadata(doi)
        if metadata: 
            if use_cache:
                self.cache.set_cache(doi, metadata.to_json())
                # print(f"Data cached for {doi}.")
            return metadata.get_pdf_link()
        else:
            return None

