import regex
import requests
from playwright.async_api import async_playwright
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
        response = requests.get(robots_txt_url, timeout=10)
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
        print(f"[{plugin_name}] robots.txt blocked access to {url}")
        return False
    else:
        return True


def get_page_with_requests(url, params={}, timeout=10):
    """Get web page with requests library"""
    return requests.get(url, params=params, timeout=timeout)


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


def get_web_page_contents(url):
    """Get web page with requests library"""
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

    soup = BeautifulSoup(response.text, "html.parser")
    if (pdf_url := get_pdf_url_from_meta(soup)):
        return pdf_url
    if (pdf_url := get_pdf_url_from_links(soup)):
        return pdf_url
    return None
