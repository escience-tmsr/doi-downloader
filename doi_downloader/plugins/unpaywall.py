import os
from doi_downloader.plugins import Plugin
from doi_downloader.article_dataobject import ArticleDataObject
from doi_downloader.lib import get_page_with_requests
from requests.exceptions import ConnectionError, ConnectTimeout, HTTPError, ReadTimeout, TooManyRedirects


# Read API keys and other sensitive data from environment variables
# UNPAYWALL_EMAIL = None
UNPAYWALL_API_URL = "https://api.unpaywall.org/v2/{doi}?email={email}"
UNPAYWALL_EMAIL = os.getenv("UNPAYWALL_EMAIL")

class UnpaywallPlugin(Plugin):
    plugin_name = "unpaywall"

    def test(self):
        return True

    def fetch_metadata(self, doi):
        if not UNPAYWALL_EMAIL:
            raise EnvironmentError("Please make sure email is set using set_email().")
        url = UNPAYWALL_API_URL.format(doi=doi, email=UNPAYWALL_EMAIL)
        try:
            response = get_page_with_requests(url, params={}, plugin_name=self.plugin_name)
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
            data = response.json()
            dataObj = ArticleDataObject.from_unpaywall_json(data)
            return dataObj
        except HTTPError:
            print(f"[{self.plugin_name}] access error while fetching data")
        except (ConnectTimeout, ReadTimeout):
            print(f"[{self.plugin_name}] timeout while fetching data")
        except ConnectionError:
            print(f"[{self.plugin_name}] connection error while fetching data")
        except TooManyRedirects:
            print(f"[{self.plugin_name}] too many redirects while fetching data")
        except ValueError:
            print(f"[{self.plugin_name}] error processing JSON data")
        return None
