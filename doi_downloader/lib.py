import logging
import regex
import requests
import responses
import time
from functools import cache
from urllib.parse import urljoin
from playwright.async_api import async_playwright
from urllib.robotparser import RobotFileParser
from urllib.parse import urlsplit
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)


HTTP_HEADERS = {
   "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
   "AppleWebKit/537.36 (KHTML, like Gecko) "
   "Chrome/120.0.0.0 Safari/537.36"),
}


@cache
def get_robots_txt(robots_txt_url):
    """Retrieve robots.txt file of a website"""
    return requests.get(robots_txt_url, timeout=10)


def robot_access_allowed(url, plugin_name=""):
    """Check if website allows access to url by robots"""
    split_url = urlsplit(url)
    robots_txt_url = f"{split_url.scheme}://{split_url.netloc}/robots.txt"
    try:
        response = get_robots_txt(robots_txt_url)
    except requests.RequestException as e:
        # website access problem for robots.txt
        return True
    if response.status_code != 200:
        # webpage access problem for robots.txt: "
        return True
    robot_parsed = RobotFileParser()
    robot_parsed.set_url(robots_txt_url)
    robot_parsed.parse(response.text.splitlines())
    if not robot_parsed.can_fetch("*", url):
        return False
    else:
        return True


BROWSER_PARAMS = { "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                                  "Chrome/120.0.0.0 Safari/537.36") }

def get_page_with_requests(url, params=BROWSER_PARAMS, timeout=10, plugin_name=""):
    """Get web page with requests library; check return statr=us and robots.txt"""
    session = requests.Session()
    session.headers.update(params)
    max_hops = 10
    for hop in range(max_hops):
        response = session.get(url, params=params, timeout=timeout, allow_redirects=False)
        time.sleep(1)
        if response.status_code not in [301, 302, 303]:
            return response
        else:
            url = urljoin(response.url, response.headers.get("Location"))
            if robot_access_allowed(url):
                continue
            else:
                print(f"[{plugin_name}] robots.txt blocks {url}")
                return response
    raise Exception(f"[{plugin_name}] get_page_with_requests: too many hops: {max_hops}")


async def get_page_with_playwright(url):
    """Get web page with playwright library"""
    async with async_playwright() as p:
        browser = await p.firefox.launch()
        page = await browser.new_page()
        history = []
        page.on("response", lambda r: history.append((r.status, r.url)))
        response = await page.goto(url)
        content = await page.content()
        await browser.close()
        return response, content, history


def get_pdf_url_from_meta(soup):
    """Get url pointing to PDF related to DOI from publisher metadata in web page"""
    meta = soup.find("meta", attrs={"name": "citation_pdf_url"})
    if meta and "content" in meta.attrs:
        return meta["content"]
    else:
        return None


def get_pdf_url_from_links(soup, base_url):
    """Get url pointing to PDF related to DOI from links in web page"""
    link = soup.find("a", href=lambda h: h and 
                                         regex.search("download|pdf",
                                                      h,
                                                      flags=regex.IGNORECASE))
    return urljoin(base_url, link["href"]) if link and base_url else None


def get_pdf_url_from_html_text(html_text, plugin_name="", base_url=None):
    """Extract pdf url from html text, returns link to PDF"""
    soup = BeautifulSoup(html_text, "html.parser")
    if (pdf_url := get_pdf_url_from_meta(soup)):
        return pdf_url
    if (pdf_url := get_pdf_url_from_links(soup, base_url=base_url)):
        return pdf_url
    return None
