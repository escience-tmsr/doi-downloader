import asyncio
import os
import regex
import requests
from doi_downloader.plugins import Plugin
from doi_downloader.cache_duckdb import Cache
from doi_downloader import article_dataobject as ado
from doi_downloader.benchmark import BenchmarkLogger
from playwright.async_api import async_playwright

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
SERPAPI_SEARCH_URL = "https://serpapi.com/search.json"

class GoogleScholarSerpAPIPlugin(Plugin):
    def __new__(self):
        instance = super(Plugin, self).__new__(self)
        self.cache = Cache("database.db", "googlescholar_serpapi")

        # Plugin-specific logger
        self.benchmark_logger = BenchmarkLogger("benchmark/logs/serpapi_benchmark.jsonl")

        self.params = { "engine": "google_scholar", "api_key": SERPAPI_KEY }
        return instance


    def test(self):
        return SERPAPI_KEY is not None


    def verify_links_by_url(self, target_doi, link, pdf_link):
        """Compare returned links with target DOI"""
        target_doi_suffix = "/".join(target_doi.split("/")[1:])
        if regex.search(target_doi_suffix, str(pdf_link)):
            print(f"PDF link {pdf_link} matches DOI {target_doi}")
            return True
        if regex.search(target_doi_suffix, str(link)):
            print(f"PDF link {pdf_link} matches DOI {target_doi}")
            return True
        print(f"Failed matching DOI {target_doi} to either {link} or {pdf_link}")
        return False


    async def get_page_with_playwright(self, url):
        async with async_playwright() as p:
            browser = await p.firefox.launch()
            page = await browser.new_page()
            history = []
            page.on("response", lambda r: history.append((r.status, r.url)))
            response = await page.goto(url)
            content = await page.content()
            await browser.close()
            return response, content, history


    async def verify_links_by_contents(self, target_doi, link, pdf_link):
        """Compare content of returned links with target DOI"""
        try:
            response, content, history = await self.get_page_with_playwright(link)
            print(response.status)
            if regex.search(target_doi, content, regex.IGNORECASE):
                print(f"Found DOI {target_doi} in contents of link {link}")
                return True
        except Exception:
            pass
        print(f"DOI {target_doi} not found in contents of link {link}")
        return False

         
    async def make_data_object(self, data, doi):
        """Convert data object returned by Google Scholar to plugin format"""
        top_result = data["organic_results"][0]
        title = top_result.get("title", "no_title")
        link = top_result.get("link", ("no_link"))
        pdf_link = top_result.get("resources", [{}])[0].get("link", "no_pdf_link")
        if not self.verify_links_by_url(doi, link, pdf_link):
            await self.verify_links_by_contents(doi, link, pdf_link)

        data_object = ado.ArticleDataObject(None)
        data_object.set_title(title)
        data_object.set_doi(doi)
        data_object.add_link(link)
        data_object.add_pdf_link(pdf_link)

        return data_object


    async def fetch_metadata(self, doi):
        if not SERPAPI_KEY:
            raise EnvironmentError("Please set SERPAPI_KEY environment variable.")

        self.params["q"] = f"doi:{doi}"
        try:
            response = requests.get(SERPAPI_SEARCH_URL, params=self.params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if not data.get("organic_results"):
                print(f"No Google Scholar results for DOI {doi}")
                return None

            return await self.make_data_object(data, doi)
        except requests.exceptions.RequestException as e:
            print(f"SerpAPI request failed: {e}")
            return None


    # Function to get the URL of the PDF from the DOI
    async def get_pdf_url(self, doi, use_cache=True, ttl=0):
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
                return data_object.get_pdf_link()

        metadata = await self.fetch_metadata(doi)
        print("metadata", metadata.get_link() if metadata else None)
        if metadata:
            url = metadata.get_pdf_link()
            if use_cache:
                self.cache.set_cache(doi, metadata.to_json())
            return url
        else:
            return None
