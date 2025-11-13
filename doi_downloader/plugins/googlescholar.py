import os
import requests
from doi_downloader.plugins import Plugin
from doi_downloader.cache_duckdb import Cache
from doi_downloader import article_dataobject as ado
from doi_downloader.benchmark import BenchmarkLogger

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
SERPAPI_SEARCH_URL = "https://serpapi.com/search.json"

class GoogleScholarSerpAPIPlugin(Plugin):
    def __new__(self):
        instance = super(Plugin, self).__new__(self)
        self.cache = Cache("database.db", "googlescholar_serpapi")

        # Plugin-specific logger
        self.benchmark_logger = BenchmarkLogger("benchmark/logs/serpapi_benchmark.jsonl")
        return instance

    def test(self):
        return SERPAPI_KEY is not None

    def fetch_metadata(self, doi):
        if not SERPAPI_KEY:
            raise EnvironmentError("Please set SERPAPI_KEY environment variable.")

        params = {
            "engine": "google_scholar",
            "q": f"doi:{doi}",
            "api_key": SERPAPI_KEY
        }

        try:
            response = requests.get(SERPAPI_SEARCH_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if not data.get("organic_results"):
                print(f"No Google Scholar results for DOI {doi}")
                return None

            top_result = data["organic_results"][0]
            title = top_result.get("title", "N/A")
            download_link = top_result.get("link", f"https://doi.org/{doi}")  # fallback to DOI URL

            # Optional PDF link, if available:
            pdf_link = top_result.get("resources", [{}])[0].get("link", download_link)

            data_object = ado.ArticleDataObject(None)
            data_object.set_title(title)
            data_object.set_doi(doi)
            data_object.add_pdf_link(pdf_link)

            return data_object

        except requests.exceptions.RequestException as e:
            print(f"SerpAPI request failed: {e}")
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
                print(f"[serpapi] using cached data for {doi}.")
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

