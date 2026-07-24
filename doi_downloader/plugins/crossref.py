from doi_downloader.plugins import Plugin
from doi_downloader.cache_duckdb import Cache
from doi_downloader import article_dataobject as ado # import ArticleDataObject
from doi_downloader.benchmark import BenchmarkLogger
from doi_downloader.lib import get_page_with_requests
from requests.exceptions import ConnectionError, HTTPError, ReadTimeout, TooManyRedirects

# Read API keys and other sensitive data from environment variables
CROSSREF_API_URL = "https://api.crossref.org/works/{doi}"

class CrossrefPlugin(Plugin):
    def __new__(self):
        instance = super(Plugin, self).__new__(self)
        self.cache = Cache("database.db", "crossref")

        # Plugin-specific logger
        self.benchmark_logger = BenchmarkLogger("benchmark/logs/crossref_benchmark.jsonl")

        return instance

    def test(self):
        return True

    def fetch_metadata(self, doi, plugin_name=""):
        url = CROSSREF_API_URL.format(doi=doi)
        try:
            response = get_page_with_requests(url, params={}, plugin_name="crossref")
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
            data = response.json()
            if "message" not in data:
                # print(f"No metadata found for DOI: {doi}")
                return None

            dataObj = ado.ArticleDataObject.from_crossref_json(data)
            dataObj.validate()
            return dataObj

        except HTTPError:
            print(f"[{plugin_name}] access error while fetching data")
        except ConnectionError:
            print(f"[{plugin_name}] connection error while fetching data")
        except ReadTimeout:
            print(f"[{plugin_name}] timeout while fetching data")
        except TooManyRedirects:
            print(f"[{plugin_name}] too many redirects while fetching data")
        return None
