import os
from doi_downloader.plugins import Plugin
from doi_downloader.cache_duckdb import Cache
from doi_downloader import article_dataobject as ado # import ArticleDataObject
from doi_downloader.benchmark import BenchmarkLogger
from doi_downloader.lib import get_page_with_requests
from requests.exceptions import ConnectionError, ConnectTimeout, HTTPError, ReadTimeout, TooManyRedirects


# Read API keys and other sensitive data from environment variables
# UNPAYWALL_EMAIL = None
UNPAYWALL_API_URL = "https://api.unpaywall.org/v2/{doi}?email={email}"
UNPAYWALL_EMAIL = os.getenv("UNPAYWALL_EMAIL")

class UnpaywallPlugin(Plugin):
    def __new__(self):
        instance = super(Plugin, self).__new__(self)
        self.cache = Cache("database.db", "unpaywall")

        # Plugin-specific logger
        self.benchmark_logger = BenchmarkLogger("benchmark/logs/unpaywall_benchmark.jsonl")
        return instance

    def test(self):
        return True

    def fetch_metadata(self, doi, plugin_name=""):
        if not UNPAYWALL_EMAIL:
            raise EnvironmentError("Please make sure email is set using set_email().")
        url = UNPAYWALL_API_URL.format(doi=doi, email=UNPAYWALL_EMAIL)
        try:
            response = get_page_with_requests(url, params={}, plugin_name="unpaywall")
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
            data = response.json()
            dataObj = ado.ArticleDataObject.from_unpaywall_json(data)
            return dataObj
        except HTTPError:
            print(f"[{plugin_name}] access error while fetching data")
        except (ConnectTimeout, ReadTimeout):
            print(f"[{plugin_name}] timeout while fetching data")
        except ConnectionError:
            print(f"[{plugin_name}] connection error while fetching data")
        except TooManyRedirects:
            print(f"[{plugin_name}] too many redirects while fetching data")
        return None
