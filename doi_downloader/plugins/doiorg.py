from doi_downloader.lib import get_pdf_url_from_html_text
from doi_downloader.plugins import Plugin

DOIORG_URL = "https://doi.org/{doi}"


class DoiorgPlugin(Plugin):
    """Fetch PDF url via website doi.org"""

    plugin_name = "doiorg"

    def make_url(self, doi):
        return DOIORG_URL.format(doi=doi)

    def process_webpage(self, response, doi, data_object):
        """Extract url pointing to PDF from the publisher page doi.org redirected to"""
        pdf_url = get_pdf_url_from_html_text(response.text, plugin_name=self.plugin_name, base_url=response.url)
        if pdf_url:
            data_object.add_pdf_link(response.url, pdf_url)
