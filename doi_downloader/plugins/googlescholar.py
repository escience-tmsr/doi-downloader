import os

from requests.exceptions import ConnectionError, HTTPError, ReadTimeout, TooManyRedirects

from doi_downloader.lib import get_page_with_requests, get_pdf_url_from_html_text, robot_access_allowed
from doi_downloader.plugins import Plugin

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
SERPAPI_SEARCH_URL = "https://serpapi.com/search.json"
PARAMS_BASE =  { "engine": "google_scholar", "api_key": SERPAPI_KEY }


class GoogleScholarSerpAPIPlugin(Plugin):
    """Fetch metadata from SerpAPI's Google Scholar search, then additionally
       fetch the publisher page it points to for link verification and its own
       pdf link (if any). The second fetch has its own url/failure modes, so
       it's handled directly in process_webpage rather than via make_url --
       only the primary SerpAPI request goes through the base Plugin template.
    """

    plugin_name = "serpapi"

    def make_url(self, doi):
        if not SERPAPI_KEY:
            raise OSError("[self.plugin_name] Please set SERPAPI_KEY environment variable.")
        return SERPAPI_SEARCH_URL

    def request_params(self, doi):
        return PARAMS_BASE | {"q": f"doi:{doi}"}

    def process_webpage(self, response, doi, data_object):
        results = response.json().get("organic_results")
        if results and isinstance(results, list):
            self.add_serpapi_results(data_object, results, doi, response.url)
        else:
            print(f"[{self.plugin_name}] no search results for DOI {doi}")

    def verify_links_by_url(self, target_doi, links):
        """Compare returned links with target DOI"""
        for pdf_link in links:
            if pdf_link and target_doi.lower() in str(pdf_link).lower():
                print(f"[{self.plugin_name}] PDF link matches DOI {target_doi}")
                return True
        return False

    def verify_link_by_html(self, target_doi, text):
        """Compare content of returned links (html) with target DOI"""
        if target_doi.lower() in str(text).lower():
            print(f"[{self.plugin_name}] Found DOI {target_doi} in html")
            return True
        return False

    def add_publisher_page(self, data_object, doi, publisher_link, links_verified, existing_pdf_links):
        """Fetch the publisher page for additional link verification and its own
           pdf link (if any), recorded under its own url -- separate from the
           SerpAPI-derived pdf_links already added to data_object.

           :return: the (possibly updated) links_verified flag
        """
        data_object.mark_fetch_pending(publisher_link)
        if not robot_access_allowed(publisher_link):
            return links_verified

        response = None
        try:
            response = get_page_with_requests(publisher_link, plugin_name=self.plugin_name)
            response.raise_for_status()
        except HTTPError:
            print(f"[{self.plugin_name}] access error for publisher page")
            data_object.mark_fetch_pending(response.url, replacing_url=publisher_link)
        except ConnectionError:
            print(f"[{self.plugin_name}] connection error for publisher page")
        except ReadTimeout:
            print(f"[{self.plugin_name}] timeout accessing publisher page")
        except TooManyRedirects:
            print(f"[{self.plugin_name}] too many redirects acccessing publisher page")
        else:
            data_object.mark_fetch_reachable(response.url, pending_url=publisher_link)
            if not links_verified and publisher_link:
                links_verified = self.verify_link_by_html(doi, response.text)
            publisher_pdf_link = get_pdf_url_from_html_text(response.text, plugin_name=self.plugin_name)
            if publisher_pdf_link:
                data_object.add_pdf_link(response.url, publisher_pdf_link)
                if not links_verified and publisher_pdf_link not in existing_pdf_links:
                    links_verified = self.verify_links_by_url(doi, [publisher_pdf_link, publisher_link])
        return links_verified

    def add_serpapi_results(self, data_object, results, doi, fetch_url):
        """Populate data_object from a successful SerpAPI response's first result.
           Serpapi returns one result (list data["organic_results"][0]) with
           links to the publisher (data["organic_results"][0]["link"]) and the
           PDFs (data["organic_results"][0]["resources"][*]["link"]).

           Note: most pdf_links come from the SerpAPI search result (fetch_url).
           The publisher page fetched below is used for link verification, and
           its own pdf link (if any) is recorded separately under its own url.
        """
        top_result = results[0]
        data_object.set_title(top_result.get("title"))
        publisher_link = top_result.get("link")
        pdf_links = [record["link"] for record in top_result.get("resources", []) if record.get("link")]
        links_verified = self.verify_links_by_url(doi, [*pdf_links, publisher_link])
        for pdf_link in pdf_links:
            data_object.add_pdf_link(fetch_url, pdf_link)

        links_verified = self.add_publisher_page(data_object, doi, publisher_link, links_verified, pdf_links)
        data_object.set_links_verified(links_verified)
