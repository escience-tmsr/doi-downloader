import requests
import os
from doi_downloader.plugins import Plugin
from doi_downloader.cache_duckdb import Cache
from doi_downloader import article_dataobject as ado
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Read API keys and other sensitive data from environment variables
CORE_API_URL = "https://api.core.ac.uk/v3/works"
CORE_API_KEY = os.getenv("CORE_API_KEY")

class CoreacukPlugin(Plugin):
    def __new__(self):
        instance = super(Plugin, self).__new__(self)
        self.cache = Cache("database.db", "coreacuk")
        return instance

    def test(self):
        return True

    def fetch_metadata(self, doi):
        """
        Retrieve metadata for a paper using its DOI from CORE API.

        Args:
            doi: The DOI of the research paper
        
        Returns:
            Metadata dictionary or an error message
        """
        base_url = CORE_API_URL
        api_key = CORE_API_KEY
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        params = {}
        full_url = f"{base_url}/{doi}"

        try:
            retries = 1
            for i in range(retries):
                response = requests.get(full_url, headers=headers, params=params)

                if response.status_code == 200:
                    paper = response.json()
                    title = paper.get("title", "N/A")
                    download_link = paper.get("downloadUrl", "N/A")
                    full_text_sources = paper.get("sourceFulltextUrls", [])
                    data_object = ado.ArticleDataObject(None)
                    data_object.set_title(title)
                    data_object.set_doi(doi)
                    
                    if download_link:
                        data_object.add_pdf_link(download_link)
                    for source in full_text_sources:
                        if "pdf" in source:
                            data_object.add_pdf_link(source) 

                    print(f"[coreacuk] Title: {title} has download url: {download_link} and full text sources: {full_text_sources}")
                    return data_object

                if response.status_code == 429:
                    print(f"[coreacuk] Rate limit exceeded for doi {doi}.")
                    return None
                if response.status_code == 404:
                    print(f"[coreacuk] Paper with DOI {doi} not found.")
                    return None
                if response.status_code == 403:
                    print("[coreacuk] Forbidden access. Check your API key.")
                    return None
                if response.status_code == 401:
                    print("[coreacuk] Unauthorized access. Check your API key.")
                    return None
                if response.status_code >= 500:
                    print(f"[coreacuk] Server error for doi {doi}.")
                    return None
            return None

        except requests.exceptions.RequestException as e:
            print(f"[coreacuk] An error occurred: {e}")
            return None

    # Original function signature restored - no ctx parameter
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
                print(f"[coreacuk] using cached data for {doi}.")
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