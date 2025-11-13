import requests
from doi_downloader.plugins import Plugin
from doi_downloader.cache_duckdb import Cache
from doi_downloader import article_dataobject as ado # import ArticleDataObject
from doi_downloader.benchmark import BenchmarkLogger

# Read API keys and other sensitive data from environment variables
CROSSREF_API_URL = "https://api.crossref.org/works/{doi}"

class CrossrefPlugin(Plugin):
    def __new__(self):
        instance = super(Plugin, self).__new__(self)
        self.cache = Cache("database.db", "crossref")

        # Plugin-specific logger
        self.benchmark_logger = BenchmarkLogger("benchmark/logs/crossref_benchmark.jsonl")

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


    # Function to get the URL of the PDF from the DOI
    def get_pdf_url(self, doi, ctx, use_cache=True, ttl=0, enable_benchmark=False):
            """
            Get PDF URL with optional benchmarking
            
            Args:
                enable_benchmark: If True, log detailed plugin-level metrics
            """
            # Plugin-level benchmarking (optional, for detailed analysis)
            if enable_benchmark:
                return self._get_pdf_url_impl(doi, ctx, use_cache, ttl)
            else:
                return self._get_pdf_url_impl(doi, None, use_cache, ttl)
    
    def _get_pdf_url_impl(self, doi, ctx, use_cache, ttl):
        """Internal implementation with context support"""
        if use_cache:
            cached_data = self.cache.get_cache(doi, ttl=ttl)
            if cached_data:
                print(f"[crossref] using cached data for {doi}.")
                data_object = ado.ArticleDataObject.from_json(cached_data)
                data_object.validate()
                url = data_object.get_pdf_link()
                if ctx and url:
                    ctx.mark_url_resolved(url)
                return url

        metadata = self.fetch_metadata(doi)
        if metadata:
            url = metadata.get_pdf_link()
            if ctx and url:
                ctx.mark_url_resolved(url)
            if use_cache:
                self.cache.set_cache(doi, metadata.to_json())
            return url
        else:
            return None

