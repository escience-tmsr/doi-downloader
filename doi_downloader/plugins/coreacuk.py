import os
from doi_downloader.plugins import Plugin
from doi_downloader.cache_duckdb import Cache
from doi_downloader import article_dataobject as ado
from dotenv import load_dotenv
from doi_downloader.lib import get_page_with_requests
from requests.exceptions import ConnectionError, HTTPError, ReadTimeout, TooManyRedirects


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

    def fetch_metadata(self, doi, plugin_name=""):
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

        full_url = f"{base_url}/{doi}"

        try:
            retries = 1
            for i in range(retries):
                response = get_page_with_requests(full_url, headers=headers, plugin_name="coreacuk")
                response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)

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

                    print(f"[{plugin_name}] Title: {title} has download url: {download_link} and full text sources: {full_text_sources}")
                    return data_object

                if response.status_code == 429:
                    print(f"[{plugin_name}] Rate limit exceeded for doi {doi}.")
                    return None
                if response.status_code == 404:
                    print(f"[{plugin_name}] Paper with DOI {doi} not found.")
                    return None
                if response.status_code == 403:
                    print(f"[{plugin_name}] Forbidden access. Check your API key.")
                    return None
                if response.status_code == 401:
                    print(f"[{plugin_name}] Unauthorized access. Check your API key.")
                    return None
                if response.status_code >= 500:
                    print(f"[{plugin_name}] Server error for doi {doi}.")
                    return None

        except HTTPError:
            print(f"[{plugin_name}] access error while fethcing data, authorization problem?")
        except ReadTimeout:
            print(f"[{plugin_name}] timeout while fetching data")
        except ConnectionError:
            print(f"[{plugin_name}] connection error while fetching data")
        except TooManyRedirects:
            print(f"[{plugin_name}] too many redirects while fetching data")
        return None
