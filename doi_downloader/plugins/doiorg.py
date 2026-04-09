import regex
import requests
from doi_downloader.plugins import Plugin
from doi_downloader.cache_duckdb import Cache
from doi_downloader import article_dataobject as ado # import ArticleDataObject
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
from urllib.parse import urlsplit


# Read API keys and other sensitive data from environment variables
DOIORG_URL = "https://doi.org/{doi}"

class AAADoiorgPlugin(Plugin):
    def __new__(self):
        instance = super(Plugin, self).__new__(self)
        self.cache = Cache("database.db", "doiorg")
        return instance

    def test(self):
        return True

    def robots_check(self, url):
        url_splitted = urlsplit(url)
        robots_txt_url = url_splitted.scheme + "://" + url_splitted.netloc + "/robots.txt"
        try:
            response = requests.get(robots_txt_url)
        except requests.RequestException as e:
            print(f"website access problem: {e}")
            return True
        if response.status_code != 200:
            print(f"webpage access problem: {response.status_code}")
            return True
        robot_parsed = RobotFileParser()
        robot_parsed.set_url(robots_txt_url)
        robot_parsed.parse(response.text.splitlines())
        return robot_parsed.can_fetch("*", url)
        
    def fetch_metadata(self, doi):
        url = DOIORG_URL.format(doi=doi)
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
            if not self.robots_check(response.url):
                print(f"[doi.org] robots.txt blocked acccess to {response.url}")
                return None
            soup = BeautifulSoup(response.text, "html.parser")
            meta = soup.find("meta", attrs={"name": "citation_pdf_url"})
            if meta and meta["content"]:
                return meta["content"]
            links = soup.find_all("a", string=lambda text: text and regex.search("download|pdf", text, flags=regex.IGNORECASE))
            for link in links:
                if link["href"]:
                    return link["href"]
            return None

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None


    def get_pdf_url(self, doi, use_cache=True, ttl=0):
        if use_cache:
            # Check the cache first
            cached_data = self.cache.get_cache(doi, ttl=ttl)
            if cached_data:
                print(f"[doiorg] Using cached data for {doi}.")
                return cached_data

        metadata = self.fetch_metadata(doi)
        if metadata: 
            if use_cache:
                self.cache.set_cache(doi, metadata)
                print(f"Data cached for {doi}.")
            return metadata
        else:
            return None

