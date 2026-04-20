import regex
import requests
from doi_downloader.plugins import Plugin
from doi_downloader.cache_duckdb import Cache
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
from urllib.parse import urlsplit


DOIORG_URL = "https://doi.org/{doi}"


class DoiorgPlugin(Plugin):
    def __new__(self):
        """Create new instance of class"""
        instance = super(Plugin, self).__new__(self)
        self.cache = Cache("database.db", "doiorg")
        return instance


    def robot_access_allowed(self, url):
        """Check if website allows access to url by robots"""
        url_splitted = urlsplit(url)
        robots_txt_url = (url_splitted.scheme + "://" + 
                          url_splitted.netloc + "/robots.txt")
        try:
            response = requests.get(robots_txt_url)
        except requests.RequestException as e:
            print(f"[doi.org] website access problem for robots.txt: {e}")
            return True
        if response.status_code != 200:
            print(f"[doi.org] webpage access problem for robots.txt: "
                  f"{response.status_code}")
            return True
        robot_parsed = RobotFileParser()
        robot_parsed.set_url(robots_txt_url)
        robot_parsed.parse(response.text.splitlines())
        return robot_parsed.can_fetch("*", url)
  

    def get_web_page(self, doi):
        url = DOIORG_URL.format(doi=doi)
        headers = {
            "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/120.0.0.0 Safari/537.36"),
        }
        return requests.get(url, headers=headers, timeout=10)

 
    def get_pdf_url_from_meta(self, soup):
        """Get url pointing to PDF related to DOI from publisher metadata in web page"""
        meta = soup.find("meta", attrs={"name": "citation_pdf_url"})
        if meta and meta["content"]:
            return meta["content"]
        else:
            return None


    def get_pdf_url_from_links(self, soup):
        """Get url pointing to PDF related to DOI from links in web page"""
        links = soup.find_all("a", 
                              string=lambda text: text and 
                                                  regex.search("download|pdf", 
                                                               text, 
                                                               flags=regex.IGNORECASE))
        for link in links:
            if link["href"]:
                return link["href"]
        return None



    def fetch_metadata(self, doi):
        """Get url pointing to PDF related to DOI from the web"""
        try:
            response = self.get_web_page(doi)
            # Raise an HTTPError for bad responses (4xx and 5xx)
            response.raise_for_status()
            if not self.robot_access_allowed(response.url):
                print(f"[doi.org] robots.txt blocked acccess to {response.url}")
                return None
            soup = BeautifulSoup(response.text, "html.parser")
            if (pdf_url := self.get_pdf_url_from_meta(soup)):
                return pdf_url
            if (pdf_url := self.get_pdf_url_from_links(soup)):
                return pdf_url
            return None
        except requests.exceptions.RequestException as e:
            print(f"[doi.org] An error occurred: {e}")
            return None


    def get_pdf_url(self, doi, use_cache=True, ttl=0):
        """Get url pointing to PDF related to DOI, from cache or from the web"""
        if use_cache and (cached_data := self.cache.get_cache(doi, ttl=ttl)):
            print(f"[doi.org] Using cached data for {doi}.")
            return cached_data
        metadata = self.fetch_metadata(doi)
        if use_cache and meta_data:
            self.cache.set_cache(doi, metadata)
            print(f"[doi.org] Data cached for {doi}.")
        return metadata
