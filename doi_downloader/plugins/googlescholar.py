import os

from requests.exceptions import ConnectionError, HTTPError, ReadTimeout, TooManyRedirects

from doi_downloader import article_dataobject as ado
from doi_downloader.lib import get_pdf_url_from_html_text, get_page_with_requests, robot_access_allowed
from doi_downloader.plugins import Plugin

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
SERPAPI_SEARCH_URL = "https://serpapi.com/search.json"
PARAMS_BASE =  { "engine": "google_scholar", "api_key": SERPAPI_KEY }


class GoogleScholarSerpAPIPlugin(Plugin):
    plugin_name = "serpapi"

    def test(self):
        return SERPAPI_KEY is not None

    def verify_links_by_url(self, target_doi, publisher_link, pdf_links):
        """Compare returned links with target DOI"""
        for pdf_link in pdf_links:
            if pdf_link and target_doi.lower() in str(pdf_link).lower():
                print(f"[{self.plugin_name}] ✅ PDF link matches DOI {target_doi}")
                return True
        if publisher_link and target_doi.lower() in str(publisher_link).lower():
            print(f"[{self.plugin_name}] ✅ publisher link matches DOI {target_doi}")
            return True
        return False

    def verify_link_by_html(self, target_doi, text):
        """Compare content of returned links (html) with target DOI"""
        if target_doi.lower() in str(text).lower():
            print(f"[{self.plugin_name}] ✅ Found DOI {target_doi} in html")
            return True
        return False

    def make_data_object(self, top_result, doi, publisher_link, pdf_links, links_verified):
        """Store paper data in data object"""
        data_object = ado.ArticleDataObject(None)
        data_object.set_title(top_result.get("title"))
        data_object.set_doi(doi)
        data_object.add_link(publisher_link)
        for pdf_link in pdf_links:
            data_object.add_pdf_link(pdf_link)
        data_object.set_links_verified(links_verified)
        return data_object

    def get_data_object(self, results, doi):
        """Convert data object returned by Google Scholar to plugin format.
           Serpapi returns one result (list data["organic_results"][0])
           with links to the publisher (data["organic_results"][0]["link"])
           and the PDFs (data["organic_results"][0]["resources"][*]["link"]).
           Returns: publisher PDF link plus all PDF links from the first result
        """
        top_result = results[0]
        publisher_link = top_result.get("link")
        pdf_links = [record["link"] for record in top_result.get("resources", []) if record.get("link")]
        links_verified = self.verify_links_by_url(doi, publisher_link, pdf_links)

        if robot_access_allowed(publisher_link):
            try:
                response = get_page_with_requests(publisher_link, plugin_name=self.plugin_name)
                response.raise_for_status()
            except HTTPError:
                print(f"[{self.plugin_name}] access error for publisher page")
            except ConnectionError:
                print(f"[{self.plugin_name}] connection error for publisher page")
            except ReadTimeout:
                print(f"[{self.plugin_name}] timeout accessing publisher page")
            except TooManyRedirects:
                print(f"[{self.plugin_name}] too many redirects acccessing publisher page")
            else:
                publisher_pdf_link = get_pdf_url_from_html_text(response.text, plugin_name=self.plugin_name)
                if not links_verified and publisher_link:
                    links_verified = self.verify_link_by_html(doi, response.text)
                if publisher_pdf_link and publisher_pdf_link not in pdf_links and not links_verified:
                    links_verified = self.verify_links_by_url(doi, publisher_link, [publisher_pdf_link])

        return self.make_data_object(top_result, doi, publisher_link, pdf_links, links_verified)

    def fetch_metadata(self, doi):
        """Fetch metadata for doi from Serpapi API"""
        if not SERPAPI_KEY:
            raise EnvironmentError("[self.plugin_name] Please set SERPAPI_KEY environment variable.")

        empty_data_object = self.make_data_object({}, doi, None, [], False)
        try:
            response = get_page_with_requests(SERPAPI_SEARCH_URL,
                                              params=PARAMS_BASE | {"q": f"doi:{doi}"},
                                              timeout=10,
                                              plugin_name=self.plugin_name)
            response.raise_for_status()
            results = response.json().get("organic_results")
        except HTTPError:
            print(f"[{self.plugin_name}] access error while fetching data")
        except ConnectionError:
            print(f"[{self.plugin_name}] connection error while fetching data")
        except ReadTimeout:
            print(f"[{self.plugin_name}] timeout while fetching data")
        except TooManyRedirects:
            print(f"[{self.plugin_name}] too many redirects while fetching data")
        except ValueError:
            print(f"[{self.plugin_name}] error reading json data")
        else:
            if results and isinstance(results, list):
                return self.get_data_object(results, doi)
            print(f"[{self.plugin_name}] no search results for DOI {doi}")

        return empty_data_object
