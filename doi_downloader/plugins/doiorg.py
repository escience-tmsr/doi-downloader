from requests.exceptions import ConnectionError, HTTPError, ReadTimeout, TooManyRedirects

from doi_downloader.plugins import Plugin
from doi_downloader.cache_duckdb import Cache
from doi_downloader.lib import get_pdf_url_from_html_text, get_page_with_requests
from doi_downloader import article_dataobject as ado

DOIORG_URL = "https://doi.org/{doi}"


class DoiorgPlugin(Plugin):
    """Fetch PDF url via website doi.org"""

    def __new__(self):
        """Create new instance of class"""
        instance = super(Plugin, self).__new__(self)
        self.cache = Cache("database.db", "doiorg")
        return instance

    def fetch_metadata(self, doi, plugin_name=""):
        """Get publisher web page related to DOI from doi.org and extract url pointing to PDF from page"""
        try:
            url = DOIORG_URL.format(doi=doi)
            response = get_page_with_requests(url, plugin_name="doi.org")
            response.raise_for_status()
            pdf_url = get_pdf_url_from_html_text(response.text, plugin_name="doi.org", base_url=response.url)
            data_object = ado.ArticleDataObject(None)
            data_object.set_doi(doi)
            if pdf_url:
                data_object.add_pdf_link(pdf_url)
                return data_object
        except HTTPError:
            print(f"[{plugin_name}] access error while fetching data")
        except ConnectionError:
            print(f"[{plugin_name}] connection error while fetching data")
        except ReadTimeout:
            print(f"[{plugin_name}] timeout while fetching data")
        except TooManyRedirects:
            print(f"[{plugin_name}] too many redirects while fetching data")
        return None
