from doi_downloader.plugins import Plugin

# Read API keys and other sensitive data from environment variables
CROSSREF_API_URL = "https://api.crossref.org/works/{doi}"


class CrossrefPlugin(Plugin):
    plugin_name = "crossref"

    def make_url(self, doi):
        return CROSSREF_API_URL.format(doi=doi)

    def process_webpage(self, response, doi, data_object):
        data = response.json()
        if "message" not in data:
            raise ValueError
        crossref_data = data["message"]

        title = crossref_data.get("title", [])
        data_object.set_title(title[0] if title else "")
        for author in crossref_data.get("author", []):
            if author.get("given") and author.get("family"):
                data_object.add_author(author["given"], author["family"])
        data_object.data["publisher"] = crossref_data.get("publisher", "")
        data_object.data["published_date"] = self._convert_published_date(crossref_data.get("published", {}))

        pdf_link = self._extract_pdf_link(crossref_data)
        if pdf_link:
            data_object.add_pdf_link(response.url, pdf_link)

    @staticmethod
    def _convert_published_date(published_date):
        if published_date.get("date-parts"):
            try:
                return f'{published_date["date-parts"][0][0]}-{published_date["date-parts"][0][1]}'
            except IndexError:
                pass
        return ""

    @staticmethod
    def _extract_pdf_link(data):
        """
        Get the PDF link from Crossref metadata.

        Accepts a link if Crossref reports it as content-type "application/pdf",
        or if "pdf" (case-insensitive) appears anywhere in the URL -- some
        publishers (e.g. MDPI) deposit PDF links with content-type "unspecified".
        """
        for link in data.get("link", []):
            url = link.get("URL") or ""
            if link.get("content-type") == "application/pdf" or "pdf" in url.lower():
                return url
        return None
