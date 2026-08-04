import os

from dotenv import load_dotenv

from doi_downloader.plugins import Plugin

# Load environment variables from .env file
load_dotenv()

# Read API keys and other sensitive data from environment variables
CORE_API_URL = "https://api.core.ac.uk/v3/works"
CORE_API_KEY = os.getenv("CORE_API_KEY")


class CoreacukPlugin(Plugin):
    plugin_name = "coreacuk"

    def make_url(self, doi):
        return f"{CORE_API_URL}/{doi}"

    def request_headers(self, doi):
        return {
            "Authorization": f"Bearer {CORE_API_KEY}",
            "Content-Type": "application/json"
        }

    def process_webpage(self, response, doi, data_object):
        paper = response.json()
        title = paper.get("title", "N/A")
        download_link = paper.get("downloadUrl", "N/A")
        full_text_sources = paper.get("sourceFulltextUrls", [])
        data_object.set_title(title)

        if download_link:
            data_object.add_pdf_link(response.url, download_link)
        for source in full_text_sources:
            if "pdf" in source:
                data_object.add_pdf_link(response.url, source)

        print(
            f"[{self.plugin_name}] Title: {title} has download url:"
            f" {download_link} and full text sources: {full_text_sources}"
        )
