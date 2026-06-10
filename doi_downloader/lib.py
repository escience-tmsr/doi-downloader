import regex
import requests
from urllib.robotparser import RobotFileParser
from urllib.parse import urlsplit
from bs4 import BeautifulSoup


HTTP_HEADERS = {
   "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
   "AppleWebKit/537.36 (KHTML, like Gecko) "
   "Chrome/120.0.0.0 Safari/537.36"),
}


def robot_access_allowed(url, plugin_name=""):
    """Check if website allows access to url by robots"""
    split_url = urlsplit(url)
    robots_txt_url = f"{split_url.scheme}://{split_url.netloc}/robots.txt"
    try:
        response = requests.get(robots_txt_url)
    except requests.RequestException as e:
        print(f"[{plugin_name}] website access problem for robots.txt: {e}")
        return True
    if response.status_code != 200:
        print(f"[{plugin_name}] webpage access problem for robots.txt: "
              f"{response.status_code}")
        return True
    robot_parsed = RobotFileParser()
    robot_parsed.set_url(robots_txt_url)
    robot_parsed.parse(response.text.splitlines())
    return robot_parsed.can_fetch("*", url)


def get_web_page_contents(url):
    return requests.get(url, headers=HTTP_HEADERS, timeout=10)


def get_pdf_url_from_meta(soup):
    """Get url pointing to PDF related to DOI from publisher metadata in web page"""
    meta = soup.find("meta", attrs={"name": "citation_pdf_url"})
    if meta and "content" in meta.attrs:
        return meta["content"]
    else:
        return None


def get_pdf_url_from_links(soup):
    """Get url pointing to PDF related to DOI from links in web page"""
    return soup.find("a",
                     string=lambda href: href and
                                         regex.search("download|pdf",
                                                      href,
                                                      flags=regex.IGNORECASE))


def get_pdf_url_from_web_page(url, plugin_name=""):
    """Extract pdf url from html page, returns link to PDF"""
    try:
        response = get_web_page_contents(url)
        response.raise_for_status()
    except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as e:
        print(f"[{plugin_name}] An error occurred: {e}")
        return None

    if not robot_access_allowed(response.url):
        print(f"[{plugin_name}] robots.txt blocked acccess to {response.url}")
        return None
    soup = BeautifulSoup(response.text, "html.parser")
    if (pdf_url := get_pdf_url_from_meta(soup)):
        return pdf_url
    if (pdf_url := get_pdf_url_from_links(soup)):
        return pdf_url
    return None
