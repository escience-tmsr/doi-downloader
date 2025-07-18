import os
import requests
from doi_downloader.plugins import Plugin
from doi_downloader.cache_duckdb import Cache
from doi_downloader import article_dataobject as ado

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
SERPAPI_SEARCH_URL = "https://serpapi.com/search.json"

class GoogleScholarSerpAPIPlugin(Plugin):
    def __new__(self):
        instance = super(Plugin, self).__new__(self)
        self.cache = Cache("database.db", "googlescholar_serpapi")
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

    def get_pdf_url(self, doi, use_cache=True, ttl=0):
        if use_cache:
            cached_data = self.cache.get_cache(doi, ttl=ttl)
            if cached_data:
                data_object = ado.ArticleDataObject.from_json(cached_data)
                data_object.validate()
                return data_object.get_pdf_link()

        metadata = self.fetch_metadata(doi)
        if metadata:
            if use_cache:
                self.cache.set_cache(doi, metadata.to_json())
            return metadata.get_pdf_link()
        else:
            return None

