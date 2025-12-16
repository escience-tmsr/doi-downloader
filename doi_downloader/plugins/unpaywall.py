import requests
import os
from doi_downloader.plugins import Plugin
from doi_downloader.cache_duckdb import Cache
from doi_downloader import article_dataobject as ado # import ArticleDataObject
from doi_downloader.benchmark import BenchmarkLogger

# Read API keys and other sensitive data from environment variables
# UNPAYWALL_EMAIL = None
UNPAYWALL_API_URL = "https://api.unpaywall.org/v2/{doi}?email={email}"
UNPAYWALL_EMAIL = os.getenv("UNPAYWALL_EMAIL")

class UnpaywallPlugin(Plugin):
    def __new__(self):
        instance = super(Plugin, self).__new__(self)
        self.cache = Cache("database.db", "unpaywall")

        # Plugin-specific logger
        self.benchmark_logger = BenchmarkLogger("benchmark/logs/unpaywall_benchmark.jsonl")
        return instance

    def test(self):
        return True

    def fetch_metadata(self, doi):
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
    def get_pdf_url(self, doi, use_cache=True, ttl=0):
        """
        Get PDF URL from CORE API
        
        Args:
            doi: DOI identifier
            use_cache: Whether to use cached results
            ttl: Cache time-to-live in seconds
            
        Returns:
            PDF URL or None if not found
        """
        if use_cache:
            cached_data = self.cache.get_cache(doi, ttl=ttl)
            if cached_data:
                print(f"[unpaywall] using cached data for {doi}.")
                data_object = ado.ArticleDataObject.from_json(cached_data)
                data_object.validate()
                return data_object.get_pdf_link()

        metadata = self.fetch_metadata(doi)
        if metadata:
            url = metadata.get_pdf_link()
            if use_cache:
                self.cache.set_cache(doi, metadata.to_json())
            return url
        else:
            return None

