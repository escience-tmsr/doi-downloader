import os

from dotenv import load_dotenv
from requests.exceptions import ConnectionError, HTTPError, ReadTimeout, TooManyRedirects

from doi_downloader.article_dataobject import ArticleDataObject
from doi_downloader.lib import get_page_with_requests
from doi_downloader.plugins import Plugin

# Load environment variables from .env file
load_dotenv()

# Read API keys and other sensitive data from environment variables
CORE_API_URL = "https://api.core.ac.uk/v3/works"
CORE_API_KEY = os.getenv("CORE_API_KEY")

class CoreacukPlugin(Plugin):
    plugin_name = "coreacuk"

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

        full_url = f"{base_url}/{doi}"

        try:
            response = get_page_with_requests(full_url, headers=headers, plugin_name=self.plugin_name)
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)

            paper = response.json()
            title = paper.get("title", "N/A")
            download_link = paper.get("downloadUrl", "N/A")
            full_text_sources = paper.get("sourceFulltextUrls", [])
            data_object = ArticleDataObject(None)
            data_object.set_title(title)
            data_object.set_doi(doi)

            if download_link:
                data_object.add_pdf_link(download_link)
            for source in full_text_sources:
                if "pdf" in source:
                    data_object.add_pdf_link(source)

            print(
                f"[{self.plugin_name}] Title: {title} has download url:"
                f" {download_link} and full text sources: {full_text_sources}"
            )
            return data_object

        except HTTPError:
            print(f"[{self.plugin_name}] access error while fetching data, authorization problem?")
        except ReadTimeout:
            print(f"[{self.plugin_name}] timeout while fetching data")
        except ConnectionError:
            print(f"[{self.plugin_name}] connection error while fetching data")
        except TooManyRedirects:
            print(f"[{self.plugin_name}] too many redirects while fetching data")
        except ValueError:
            print(f"[{self.plugin_name}] error processing JSON data")
        return None
