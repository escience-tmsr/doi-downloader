from dotenv import load_dotenv

from doi_downloader import article_dataobject as ado
from doi_downloader.benchmark import BenchmarkLogger
from doi_downloader.cache_duckdb import Cache

load_dotenv()


class Plugin:
    """Base class for plugins. All plugins must inherit from this class."""

    plugin_name = None

    def __init__(self):
        self.cache = Cache("database.db", self.plugin_name)
        self.benchmark_logger = BenchmarkLogger(f"benchmark/logs/{self.plugin_name}_benchmark.jsonl")

    def test(self):
        raise NotImplementedError("Plugin subclasses must implement the `test` method")

    def fetch_metadata(self, doi, plugin_name):
        raise NotImplementedError("Plugin subclasses must implement the `fetch_metadata` method")

    def get_pdf_urls(self, doi, read_from_cache=True, ttl=0, plugin_name=None):
        """
        Args:
            doi: DOI identifier
            read_from_cache: whether to read the results from the cache
            ttl: Cache time-to-live in seconds
            
        Returns:
            PDF URLs: list, could be empty
        """
        plugin_name = plugin_name if plugin_name else self.plugin_name
        if read_from_cache:
            print(f"[{plugin_name}] using cached data for {doi}.")
            try:
                cached_data = self.cache.get_cache(doi, ttl=ttl)
                data_object = ado.ArticleDataObject.from_json(cached_data)
                data_object.validate()
                return data_object.get_pdf_links()
            except Exception:
                print(f"[{plugin_name}] error reading from cache")
            return []

        metadata = self.fetch_metadata(doi, plugin_name)
        if metadata:
            self.cache.set_cache(doi, metadata.to_json())
            return metadata.get_pdf_links()
        else:
            return []

