from doi_downloader.plugins import Plugin
from doi_downloader.article_dataobject import ArticleDataObject
from doi_downloader.lib import get_page_with_requests
from requests.exceptions import ConnectionError, HTTPError, ReadTimeout, TooManyRedirects

# Read API keys and other sensitive data from environment variables
CROSSREF_API_URL = "https://api.crossref.org/works/{doi}"

class CrossrefPlugin(Plugin):
    plugin_name = "crossref"

    def test(self):
        return True

    def fetch_metadata(self, doi):
        url = CROSSREF_API_URL.format(doi=doi)
        try:
            response = get_page_with_requests(url, params={}, plugin_name=self.plugin_name)
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
            data = response.json()
            if "message" not in data:
                raise ValueError
            dataObj = ArticleDataObject.from_crossref_json(data)
            dataObj.validate()
            return dataObj

        except HTTPError:
            print(f"[{self.plugin_name}] access error while fetching data")
        except ConnectionError:
            print(f"[{self.plugin_name}] connection error while fetching data")
        except ReadTimeout:
            print(f"[{self.plugin_name}] timeout while fetching data")
        except TooManyRedirects:
            print(f"[{self.plugin_name}] too many redirects while fetching data")
        except ValueError:
            print(f"[{self.plugin_name}] error processing JSON data")
        return None
