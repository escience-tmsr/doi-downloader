from doi_downloader.plugins import Plugin
from doi_downloader.cache_duckdb import Cache
from doi_downloader.lib import get_pdf_url_from_html_text, get_page_with_requests
from requests.exceptions import ConnectionError, HTTPError, TooManyRedirects


DOIORG_URL = "https://doi.org/{doi}"


class DoiorgPlugin(Plugin):
    def __new__(self):
        """Create new instance of class"""
        instance = super(Plugin, self).__new__(self)
        self.cache = Cache("database.db", "doiorg")
        return instance


    def fetch_metadata(self, doi):
        """Get publisher web page related to DOI from doi.org and extract url pointing to PDF from page"""
        try:
            url = DOIORG_URL.format(doi=doi)
            response = get_page_with_requests(url, plugin_name="doi.org")
            response.raise_for_status()
            return get_pdf_url_from_html_text(response.text, plugin_name="doi.org", base_url=response.url)
        except (ConnectionError, HTTPError, TooManyRedirects) as e:
            print(f"[doi.org] fetching data failed: {e}")
            return None


    def get_pdf_urls(self, doi, read_from_cache=True, save_to_cache=True, ttl=0):
        """Get url pointing to PDF related to DOI, from cache or from website doi.org"""
        if read_from_cache and (cached_data := self.cache.get_cache(doi, ttl=ttl)):
            print(f"[doi.org] Using cached data for {doi}.")
            return [cached_data]
        metadata = self.fetch_metadata(doi)
        if save_to_cache and metadata:
            self.cache.set_cache(doi, metadata)
            print(f"[doi.org] Data cached for {doi}.")
        return [metadata] if metadata else []
