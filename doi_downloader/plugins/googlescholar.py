import os
import regex
from doi_downloader import article_dataobject as ado
from doi_downloader.cache_duckdb import Cache
from doi_downloader.benchmark import BenchmarkLogger
from doi_downloader.lib import get_pdf_url_from_web_page, get_page_with_playwright, get_page_with_requests, robot_access_allowed
from doi_downloader.plugins import Plugin


SERPAPI_KEY = os.getenv("SERPAPI_KEY")
SERPAPI_SEARCH_URL = "https://serpapi.com/search.json"
PARAMS_BASE =  { "engine": "google_scholar", "api_key": SERPAPI_KEY }


class GoogleScholarSerpAPIPlugin(Plugin):
    def __new__(self):
        instance = super(Plugin, self).__new__(self)
        self.cache = Cache("database.db", "googlescholar_serpapi")

        # Plugin-specific logger
        self.benchmark_logger = BenchmarkLogger("benchmark/logs/serpapi_benchmark.jsonl")
        return instance


    def test(self):
        return SERPAPI_KEY is not None


    def verify_links_by_url(self, target_doi, link, pdf_links):
        """Compare returned links with target DOI"""
        for pdf_link in pdf_links:
            if pdf_link and regex.search(target_doi, str(pdf_link)):
                print(f"[serpapi] ✅ PDF link matches DOI {target_doi}")
                return True
        if link and regex.search(target_doi, str(link)):
            print(f"[serpapi] ✅ link matches DOI {target_doi}")
            return True
        return False


    async def verify_link_by_metadata(self, target_doi, link):
        """Compare content of returned links (metadata) with target DOI"""
        try:
            _, content, _ = await get_page_with_playwright(link)
            if (nbr_of_matches := len(regex.findall(target_doi, content, regex.IGNORECASE))) > 0:
                print(f"[serpapi] ✅ Found DOI {target_doi} in metadata ({nbr_of_matches} times)")
                return True
        except Exception as e:
            # link verification by metadata failed
            pass
        return False


    def make_data_object(self, top_result, doi, publisher_link, pdf_links, links_verified):
        """Store paper data in data object"""
        data_object = ado.ArticleDataObject(None)
        data_object.set_title(top_result.get("title", "no_title"))
        data_object.set_doi(doi)
        data_object.add_link(publisher_link)
        for pdf_link in pdf_links:
            data_object.add_pdf_link(pdf_link)
        data_object.set_links_verified(links_verified)
        return data_object


    async def get_data_object(self, results, doi):
        """Convert data object returned by Google Scholar to plugin format.
           Serpapi returns one result (list data["organic_results"][0])
           with links to the publisher (data["organic_results"][0]["link"])
           and the PDFs (data["organic_results"][0]["resources"][*]["link"]).
           Returns: publisher PDF link plus all PDF links from the first result
        """
        top_result = results[0]
        publisher_link = top_result.get("link", ("no_link"))
        pdf_links = [record["link"] for record in top_result.get("resources", [])]
        links_verified = self.verify_links_by_url(doi, publisher_link, pdf_links)
        if not links_verified and publisher_link:
            links_verified = await self.verify_link_by_metadata(doi, publisher_link)

        if robot_access_allowed(publisher_link):
            publisher_pdf_link = get_pdf_url_from_web_page(publisher_link, plugin_name="serpapi")
            if publisher_pdf_link and publisher_pdf_link not in pdf_links and not links_verified:
                links_verified = self.verify_links_by_url(doi, publisher_link, [publisher_pdf_link])

        return self.make_data_object(top_result, doi, publisher_link, pdf_links, links_verified)


    async def fetch_metadata(self, doi):
        """Fetch metadata for doi from Serpapi API"""
        if not SERPAPI_KEY:
            raise EnvironmentError("[serpapi] Please set SERPAPI_KEY environment variable.")

        try:
            response = get_page_with_requests(SERPAPI_SEARCH_URL,
                                              params=PARAMS_BASE | {"q": f"doi:{doi}"},
                                              timeout=10)
            response.raise_for_status()
            results = response.json().get("organic_results")

            if not results or not isinstance(results, list):
                print(f"[serpapi] search results for DOI {doi}")
                return None

            return await self.get_data_object(results, doi)
        except Exception as e:
            print(f"[serpapi] SerpAPI request failed: {e}")
            return None


    async def get_pdf_urls(self, doi, read_from_cache=True, save_to_cache=True, ttl=0):
        """
        Get PDF URL from Google Scholar API

        Args:
            doi: DOI identifier
            read_from_cache: Whether to use cached results
            save_to_cache: Whether to save results in the cache
            ttl: Cache time-to-live in seconds

        Returns:
            PDF URL or None if not found
        """
        if read_from_cache:
            cached_data = self.cache.get_cache(doi, ttl=ttl)
            if cached_data:
                print(f"[serpapi] using cached data for {doi}.")
                data_object = ado.ArticleDataObject.from_json(cached_data)
                data_object.validate()
                return data_object.get_pdf_links()

        metadata = await self.fetch_metadata(doi)
        if save_to_cache:
            self.cache.set_cache(doi, metadata.to_json() if metadata else None)
        if metadata:
            urls = metadata.get_pdf_links()
            return urls
        return None
