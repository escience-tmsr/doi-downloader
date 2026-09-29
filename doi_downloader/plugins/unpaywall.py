import os

from doi_downloader.plugins import Plugin

# Read API keys and other sensitive data from environment variables
# UNPAYWALL_EMAIL = None
UNPAYWALL_API_URL = "https://api.unpaywall.org/v2/{doi}?email={email}"
UNPAYWALL_EMAIL = os.getenv("UNPAYWALL_EMAIL")


class UnpaywallPlugin(Plugin):
    plugin_name = "unpaywall"

    def make_url(self, doi):
        if not UNPAYWALL_EMAIL:
            raise OSError("Please make sure email is set using set_email().")
        return UNPAYWALL_API_URL.format(doi=doi, email=UNPAYWALL_EMAIL)

    def process_webpage(self, response, doi, data_object):
        data = response.json()
        data_object.set_title(data.get("title", ""))
        data_object.data["publisher"] = data.get("publisher", "")
        data_object.data["published_date"] = data.get("published_date", "")
        for author in data.get("z_authors") or []:
            if author.get("given") and author.get("family"):
                data_object.add_author(author["given"], author["family"])

        pdf_link = None
        if data.get("best_oa_location"):
            pdf_link = data["best_oa_location"].get("url_for_pdf")
        if pdf_link:
            data_object.add_pdf_link(response.url, pdf_link)
