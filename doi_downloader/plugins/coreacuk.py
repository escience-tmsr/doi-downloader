import requests
import os
import time
from doi_downloader.plugins import Plugin
from doi_downloader.cache_duckdb import Cache
from doi_downloader import article_dataobject as ado # import ArticleDataObject
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

        :param doi: The DOI of the research paper
        :param api_key: CORE API key
        :return: Metadata dictionary or an error message
        """
        base_url = CORE_API_URL
        api_key = CORE_API_KEY
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # Prepare the query using the DOI
        # params = {
        #     "q": f"doi:{doi}"
        # }

        params = {}
        full_url = f"{base_url}/{doi}"

        try:
            backoff = 0
            retries = 5
            for i in range(retries):
                # Make the request to the CORE API
                response = requests.get(full_url, headers=headers, params=params)

                if response.status_code == 200:
                    paper = response.json()
                    title = paper.get("title", "N/A")
                    download_link = paper.get("downloadUrl", "N/A")
                    full_text_sources = paper.get("sourceFulltextUrls", [])
                    data_object = ado.ArticleDataObject(None)
                    data_object.set_title(title)
                    data_object.set_doi(doi)
                    # data_object.set_published_date(paper.get("publishedDate", "N/A"))
                    if download_link:
                        data_object.add_pdf_link(download_link)
                    for source in full_text_sources:
                        if "pdf" in source:
                            data_object.add_pdf_link(source) 

                    print(f"Title: {title} has download url: {download_link} and full text sources: {full_text_sources}")
                    return data_object

                if response.status_code == 429:
                    backoff += 5
                    print(f"Rate limit exceeded. Retrying in {backoff} seconds.")
                    time.sleep(backoff)
                    continue
                if response.status_code == 404:
                    print(f"Paper with DOI {doi} not found.")
                    return None
                if response.status_code == 403:
                    print("Forbidden access. Check your API key.")
                    return None
                if response.status_code == 401:
                    print("Unauthorized access. Check your API key.")
                    return None
                if response.status_code >= 500:
                    print(f"Server error. Retrying in {backoff} seconds.")
                    backoff += 5
                    time.sleep(backoff)
                    continue
    
            return None

        except requests.exceptions.RequestException as e:
                print(f"An error occurred: {e}")
                return None

    # Function to get the URL of the PDF from the DOI
    def get_pdf_url(self, doi, use_cache=True, ttl=0):
        if use_cache:
            # Check the cache first
            cached_data = self.cache.get_cache(doi, ttl=ttl)
            if cached_data:
                print(f"[coreacuk] using cached data for {doi}.")
                data_object = ado.ArticleDataObject.from_json(cached_data)
                data_object.validate()
                return data_object.get_pdf_link()
                # return _extract_url(cached_data)

        metadata = self.fetch_metadata(doi)
        if metadata: 
            if use_cache:
                self.cache.set_cache(doi, metadata.to_json())
                # print(f"Data cached for {doi}.")
            return metadata.get_pdf_link()
        else:
            return None

