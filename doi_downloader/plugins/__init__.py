from enum import Enum

from dotenv import load_dotenv
from requests.exceptions import ConnectionError, HTTPError, ReadTimeout, TooManyRedirects

from doi_downloader import progress
from doi_downloader.article_dataobject import ArticleDataObject
from doi_downloader.benchmark import BenchmarkLogger
from doi_downloader.cache_duckdb import Cache
from doi_downloader.lib import get_page_with_requests

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

    def make_url(self, doi):
        """
        Return the URL to fetch metadata from for doi. Must be implemented by
        subclasses. May raise (e.g. for a missing API key/email) -- the
        exception propagates out of fetch_metadata uncaught, before any
        request is attempted.
        """
        raise NotImplementedError("Plugin subclasses must implement the `make_url` method")

    def request_headers(self, doi):
        """Optional HTTP headers to use instead of the default browser-like headers."""
        return

    def request_params(self, doi):
        """Optional query string parameters to include in the request."""
        return

    def process_webpage(self, response, doi, data_object):
        """
        Parse a successful response (title, authors, pdf links, ...) into
        data_object. Must be implemented by subclasses. May raise ValueError
        if the response content can't be parsed; request-level exceptions
        (HTTP errors, timeouts, ...) are already handled by fetch_metadata.
        """
        raise NotImplementedError("Plugin subclasses must implement the `process_webpage` method")

    def fetch_metadata(self, doi):
        """
        Resolve doi to a url via make_url(), fetch it, and hand a successful
        response to process_webpage() to extract metadata and pdf links.

        Always returns a data_object, whether or not the fetch succeeded, so
        the attempted url stays available for post-processing analysis (see
        ArticleDataObject.mark_fetch_pending). Subclasses with a fundamentally
        different shape (e.g. more than one request) can override this instead
        of make_url/process_webpage.
        """
        data_object = ArticleDataObject(None)
        data_object.set_doi(doi)
        url = self.make_url(doi)
        data_object.mark_fetch_pending(url)

        request_kwargs = {"plugin_name": self.plugin_name}
        headers = self.request_headers(doi)
        if headers is not None:
            request_kwargs["headers"] = headers
        params = self.request_params(doi)
        if params is not None:
            request_kwargs["params"] = params

        try:
            response = get_page_with_requests(url, **request_kwargs)
            response.raise_for_status()
            data_object.mark_fetch_reachable(response.url, pending_url=url)
            self.process_webpage(response, doi, data_object)
        except HTTPError:
            print(f"[{self.plugin_name}] access error while fetching data")
            data_object.mark_fetch_pending(response.url, replacing_url=url)
        except ConnectionError:
            print(f"[{self.plugin_name}] connection error while fetching data")
        except ReadTimeout:
            print(f"[{self.plugin_name}] timeout while fetching data")
        except TooManyRedirects:
            print(f"[{self.plugin_name}] too many redirects while fetching data")
        except ValueError:
            print(f"[{self.plugin_name}] error processing response data")
        return data_object

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
            except Exception as e:
                progress.record_cache(f"{progress.STATUS_ACCESS_ERROR}: {e}", [])
                cached_data = None
            else:
                if cached_data is None:
                    progress.record_cache(progress.STATUS_NOT_FOUND, [])
                else:
                    try:
                        data_object = ArticleDataObject.from_json(cached_data)
                        data_object.validate()
                        # get_pdf_links() flattens pdf_links across all fetch urls and
                        # skips any url mapped to None (inaccessible) or [] (checked,
                        # empty) -- so this is empty both when there are no fetch urls
                        # at all, and when every fetch url yielded nothing usable.
                        pdf_urls = data_object.get_pdf_links()
                    except Exception:
                        print(f"[{self.plugin_name}] error reading from cache")
                        progress.record_cache(f"{progress.STATUS_ACCESS_ERROR}: invalid cached data", [])
                    else:
                        if pdf_urls:
                            print(f"[{self.plugin_name}] using cached data for {doi}.")
                            progress.record_cache(progress.STATUS_SUCCESS, pdf_urls)
                            progress.record_pdf_url_map(data_object.get_pdf_links_by_fetch_url())
                            return(pdf_urls)
                        # A cached entry with no usable pdf urls (e.g. a previous
                        # attempt failed entirely) is treated as a cache miss, so
                        # CACHE_FIRST retries the fetch instead of getting stuck
                        # returning the same empty result forever.
                        print(f"[{self.plugin_name}] cached data for {doi} has no pdf urls, treating as a miss")
                        progress.record_cache(progress.STATUS_NOT_FOUND, [])
            if cache_mode is CacheMode.CACHE_ONLY:
                return []
        else:
            progress.record_cache(progress.STATUS_SKIPPED, [])

        with progress.fetch_scope():
            try:
                metadata = self.fetch_metadata(doi)
            except Exception as e:
                progress.record_fetch(f"{progress.STATUS_ACCESS_ERROR}: {e}", None)
                raise

        if metadata:
            self.cache.set_cache(doi, metadata.to_json())
            progress.record_pdf_url_map(metadata.get_pdf_links_by_fetch_url())
            return metadata.get_pdf_links()
        else:
            return []

