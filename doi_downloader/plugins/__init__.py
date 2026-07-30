from enum import Enum

from dotenv import load_dotenv

from doi_downloader.article_dataobject import ArticleDataObject
from doi_downloader.benchmark import BenchmarkLogger
from doi_downloader.cache_duckdb import Cache

load_dotenv()



class CacheMode(Enum):
    REFRESH = "refresh"
    """Skip the cache, call `fetch_metadata`, and store the result."""
    CACHE_ONLY = "cache_only"
    """Read from the cache only; return an empty list if there is no cached data."""
    CACHE_FIRST = "cache_first"
    """Try the cache first, falling back to `REFRESH` behavior if there is no cached data."""


class Plugin:
    """Base class for plugins. All plugins must inherit from this class."""

    plugin_name = None

    def __init__(self):
        self.cache = Cache("database.db", self.plugin_name)
        self.benchmark_logger = BenchmarkLogger(f"benchmark/logs/{self.plugin_name}_benchmark.jsonl")

    def test(self):
        raise NotImplementedError("Plugin subclasses must implement the `test` method")

    def fetch_metadata(self, doi):
        raise NotImplementedError("Plugin subclasses must implement the `fetch_metadata` method")

    def get_pdf_urls(self, doi, cache_mode=CacheMode.CACHE_FIRST, ttl=10):
        """
        Args:
            doi: DOI of the article
            cache_mode: how the cache and its contents should be used
            ttl: Cache time-to-live in seconds
            
        Returns:
            PDF URLs: list, could be empty
        """
        if cache_mode in (CacheMode.CACHE_ONLY, CacheMode.CACHE_FIRST):
            try:
                cached_data = self.cache.get_cache(doi, ttl=ttl)
                data_object = ArticleDataObject.from_json(cached_data)
                data_object.validate()
                pdf_urls = data_object.get_pdf_links()
                print(f"[{self.plugin_name}] using cached data for {doi}.")
                return(pdf_urls)
            except Exception:
                print(f"[{self.plugin_name}] error reading from cache")
            if cache_mode is CacheMode.CACHE_ONLY:
                return []

        metadata = self.fetch_metadata(doi)
        if metadata:
            self.cache.set_cache(doi, metadata.to_json())
            return metadata.get_pdf_links()
        else:
            return []

