from doi_downloader.plugins import Plugin
from doi_downloader.cache_duckdb import Cache
from doi_downloader.lib import get_pdf_url_from_web_page


DOIORG_URL = "https://doi.org/{doi}"


class DoiorgPlugin(Plugin):
    def __new__(self):
        """Create new instance of class"""
        instance = super(Plugin, self).__new__(self)
        self.cache = Cache("database.db", "doiorg")
        return instance


    def fetch_metadata(self, doi):
        """Get url pointing to PDF related to DOI from the web"""
        url = DOIORG_URL.format(doi=doi)
        return get_pdf_url_from_web_page(url, plugin_name="doi.org")


    def get_pdf_url(self, doi, use_cache=True, ttl=0):
        """Get url pointing to PDF related to DOI, from cache or from the web"""
        if use_cache and (cached_data := self.cache.get_cache(doi, ttl=ttl)):
            print(f"[doi.org] Using cached data for {doi}.")
            return cached_data
        metadata = self.fetch_metadata(doi)
        if use_cache and metadata:
            self.cache.set_cache(doi, metadata)
            print(f"[doi.org] Data cached for {doi}.")
        return metadata
