import os
import regex
import requests
import urllib.robotparser
import urllib.parse
from doi_downloader import loader as ld
from doi_downloader.plugins import Plugin
from doi_downloader.cache_duckdb import Cache
from doi_downloader import article_dataobject as ado
from doi_downloader.benchmark import BenchmarkLogger
from playwright.async_api import async_playwright


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
        target_doi_suffix = "/".join(target_doi.split("/")[1:])
        for pdf_link in pdf_links:
            if pdf_link and regex.search(target_doi_suffix, str(pdf_link)):
                print(f"[serpapi] ✅ PDF link matches DOI {target_doi}")
                return True
        if link and regex.search(target_doi_suffix, str(link)):
            print(f"[serpapi] ✅ link matches DOI {target_doi}")
            return True
        if False:
            print(f"[serpapi] Remark: failed matching DOI {target_doi} to either link or pdf link")
        return False


    def may_fetch(url, user_agent="*"):
        """Check robots.txt file for robot access permission, Claude code"""
        print("may_fetch 1", url)
        parts = urllib.parse.urlparse(url)
        print("may_fetch 2")
        robots_url = f"{parts.scheme}://{parts.netloc}/robots.txt"
        print("may_fetch 3")
        rp = urllib.robotparser.RobotFileParser()
        print("may_fetch 4")
        rp.set_url(robots_url)
        print("may_fetch 5")
        try:
            print("may_fetch 6")
            rp.read()
        except Exception:
            print("robots.txt access error")
            return True
        print("may_fetch 7")
        return rp.can_fetch(user_agent, url)


    async def get_page_with_playwright(self, url):
        async with async_playwright() as p:
            if not self.may_fetch(url):
                print("robot access refused")
                return None, "", []
            else:
                browser = await p.firefox.launch()
                page = await browser.new_page()
                history = []
                page.on("response", lambda r: history.append((r.status, r.url)))
                response = await page.goto(url)
                content = await page.content()
                await browser.close()
                return response, content, history


    async def verify_link_by_metadata(self, target_doi, link):
        """Compare content of returned links (metadata) with target DOI"""
        try:
            response, content, history = await self.get_page_with_playwright(link)
            print(f"response.status: {response.status} {len(content)} history: len: {len(history)}, contents: {history}")
            if (nbr_of_matches := len(regex.findall(target_doi, content, regex.IGNORECASE))) > 0:
                print(f"[serpapi] ✅ Found DOI {target_doi} in metadata of link ({nbr_of_matches} times)")
                return True
        except Exception as e:
            print(f"verification failed: {e}")
            #pass
        if False:
            print(f"[serpapi] Remark: DOI {target_doi} not found in metadata of link {link}")
        return False


    async def make_data_object(self, results, doi):
        """Convert data object returned by Google Scholar to plugin format.
           Serpapi returns one result (list data["organic_results"][0]) 
           with a link to the publisher (data["organic_results"][0]["link"])
           and the PDFs (data["organic_results"][0]["resources"][*]["link"]).
           Returns: publisher PDF link plus all PDF links from the first result
        """
        top_result = results[0]
        title = top_result.get("title", "no_title")
        link = top_result.get("link", ("no_link"))
        pdf_links = [record["link"] for record in top_result.get("resources", [])]
        pdf_url_link = ld.plugins["DoiorgPlugin"].get_pdf_url_from_url(link)
        if pdf_url_link and pdf_url_link not in pdf_links:
            pdf_links.append(pdf_url_link)
        links_verified = self.verify_links_by_url(doi, link, pdf_links)
        if not links_verified and link:
            await self.verify_link_by_metadata(doi, link)

        data_object = ado.ArticleDataObject(None)
        data_object.set_title(title)
        data_object.set_doi(doi)
        data_object.add_link(link)
        for pdf_link in pdf_links:
            data_object.add_pdf_link(pdf_link)

        return data_object


    async def fetch_metadata(self, doi):
        """Fetch metadata for doi from Serpapi API"""
        if not SERPAPI_KEY:
            raise EnvironmentError("Please set SERPAPI_KEY environment variable.")

        try:
            response = requests.get(SERPAPI_SEARCH_URL, 
                                    params=PARAMS_BASE | {"q": f"doi:{doi}"},
                                    timeout=10)
            response.raise_for_status()
            results = response.json().get("organic_results")

            if not results or not isinstance(results, list): 
                print(f"No Google Scholar results for DOI {doi}")
                return None

            return await self.make_data_object(results, doi)
        except requests.exceptions.RequestException as e:
            print(f"SerpAPI request failed: {e}")
            return None


    async def get_pdf_urls(self, doi, use_cache=True, ttl=0):
        """
        Get PDF URL from Google Scholar API
        
        Args:
            doi: DOI identifier
            use_cache: Whether to use cached results
            ttl: Cache time-to-live in seconds
            
        Returns:
            PDF URL or None if not found
        """
        if use_cache:
            cached_data = self.cache.get_cache(doi, ttl=ttl)
            if cached_data:
                print(f"[serpapi] using cached data for {doi}.")
                data_object = ado.ArticleDataObject.from_json(cached_data)
                data_object.validate()
                return data_object.get_pdf_links()

        metadata = await self.fetch_metadata(doi)
        if metadata:
            urls = metadata.get_pdf_links()
            if use_cache:
                self.cache.set_cache(doi, metadata.to_json())
            return urls
        else:
            return None
