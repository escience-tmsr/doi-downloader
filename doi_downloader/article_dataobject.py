import json

import jsonschema
from jsonschema import validate

schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://example.com/crossref-schema",
    "title": "Crossref Metadata Schema",
    "type": "object",
    "required": ["version", "title", "DOI", "source", "pdf_links" ],
    "properties": {
                "title": {"type": "string" },
                "version": {"type": "string"},
                "source": {"type": "string"},
                "authors": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["given", "family"],
                        "properties": {
                            "given": {"type": "string"},
                            "family": {"type": "string"}
                        }
                    }
                },
                "DOI": {
                    "type": "string",
                    "pattern": "^10\\.\\d{4,9}/[-._;()/:a-zA-Z0-9]+$"
                },
                "published_date": {"type": "string"},
                "pdf_links": {
                    "type": "object",
                    "additionalProperties": {
                        "type": ["array", "null"],
                        "items": {
                            "type": "string",
                            "format": "uri"
                        }
                    }
                }
            }
        }

VERSION = "0.1.0"

class ArticleDataObject:
    """
    A class for handling Article data objects and validating them against a Article schema.
    """

    def __init__(self, data, schema = schema):
        """
        Initialize the ArticleDataObject with data and schema.

        :param data: The Article data object (dictionary).
        :param schema: The Article schema for validation (dictionary).
        """
        self.data = data or {
            "title": "",
            "version": VERSION,
            "source": "",
            "author": [],
            "DOI": "",
            "published_date": "",
            "pdf_links": {},
            "links_verified": False

        }
        self.schema = schema

    def set_source(self, source):
        """
        Set the source of the Article data object.

        :param source: The source of the Article.
        """
        self.data["source"] = source

    def set_title(self, title):
        """
        Set the title of the Article data object.

        :param title: The title of the Article.
        """
        self.data["title"] = title

    def add_author(self, given_name, family_name):
        """
        Add an author to the Article data object.

        :param given_name: The given name of the author.
        :param family_name: The family name of the author.
        """
        self.data["author"].append({"given": given_name, "family": family_name})

    def set_doi(self, doi):
        """
        Set the DOI of the Article data object.

        :param doi: The DOI of the Article.
        """
        self.data["DOI"] = doi


    def set_published_date(self, year, month, day):
        """
        Set the issued date of the Article data object.

        :param year: The year of publication.
        :param month: The month of publication.
        :param day: The day of publication.
        """
        self.data["published_date"] = f"{year}-{month}-{day}"

    def set_links_verified(self, links_verified):
        """
        Set the links_verified flag

        :param links_verified: flag indicating if PDF links could be verified for the target DOI
        """
        self.data["links_verified"] = links_verified

    def add_pdf_link(self, fetch_url, url):
        """
        Add a pdf_link to the Article data object, tied to the webpage it was found on.

        :param fetch_url: The URL of the webpage the pdf_link was found on.
        :param url: The URL of the pdf link.
        """
        self.data["pdf_links"].setdefault(fetch_url, []).append(url)

    def mark_fetch_pending(self, fetch_url, replacing_url=None):
        """
        Record that fetch_url is about to be processed, before its outcome is
        known. Stays None (inaccessible) unless mark_fetch_reachable later
        upgrades it to an empty list once its contents are actually checked.

        This makes the url available for post-processing analysis even when
        it turns out to be unreachable, instead of vanishing entirely.

        :param fetch_url: The URL about to be requested.
        :param replacing_url: An url previously marked pending that this one
            supersedes (e.g. once the outcome revealed a more precise url,
            such as requests appending query parameters) -- its now-stale
            entry is removed in favor of fetch_url.
        """
        if replacing_url and replacing_url != fetch_url:
            self.data["pdf_links"].pop(replacing_url, None)
        self.data["pdf_links"][fetch_url] = None

    def mark_fetch_reachable(self, fetch_url, pending_url=None):
        """
        Record that fetch_url's contents were fetched and are being searched
        for pdf links now (even if none end up being found): upgrades its
        entry from None (pending/inaccessible) to an empty list.

        :param fetch_url: The URL that was actually reached (after redirects).
        :param pending_url: The url originally marked pending via
            mark_fetch_pending, if it differs from fetch_url -- its now-stale
            pending entry is removed in favor of fetch_url's.
        """
        if pending_url and pending_url != fetch_url:
            self.data["pdf_links"].pop(pending_url, None)
        self.data["pdf_links"][fetch_url] = []

    def get_pdf_links(self):
        """
        Get all PDF links from the Article data object, flattened across fetch URLs.

        :return: All PDF links, as a flat list
        """
        return [url for urls in self.data["pdf_links"].values() if urls for url in urls]

    def get_pdf_links_by_fetch_url(self):
        """
        Get all PDF links from the Article data object, grouped by the webpage
        (fetch URL) each one was found on.

        :return: dict mapping fetch URL to the list of pdf_links found there
        """
        return self.data["pdf_links"]

    def validate(self):
        """
        Validate the Article data against the provided schema.

        :raises jsonschema.exceptions.ValidationError: If the data does not match the schema.
        :raises jsonschema.exceptions.SchemaError: If the schema itself is invalid.
        :return: True if validation succeeds.
        """
        try:
            validate(instance=self.data, schema=self.schema)
            return True
        except jsonschema.exceptions.ValidationError as e:
            print(f"Validation error: {e.message}")
            raise
        except jsonschema.exceptions.SchemaError as e:
            print(f"Schema error: {e.message}")
            raise

    def to_json(self):
        """
        Convert the Article data object to a Article string.

        :return: A Article string representation of the data.
        """
        return json.dumps(self.data, indent=4)

    @classmethod
    def from_unpaywall_json(cls, unpaywall_data, fetch_url=None):
        """
        Create a ArticleDataObject instance from an Unpaywall JSON response.

        :param unpaywall_data: An Unpaywall JSON response representing the data.
        :param fetch_url: The URL the response was fetched from, used to key pdf_links.
        :return: An instance of ArticleDataObject.
        """
        def extract_authors(data):
            def filter_author(author):
                if author.get("given") and author.get("family"):
                    return {
                        "given": author.get("given"),
                        "family": author.get("family")
                    }
                return None

            return [
                author for author in map(filter_author, data.get("z_authors", [])) 
                if author is not None
        ]
        def extract_pdf_link(data):
            if data.get("best_oa_location"):
                return data["best_oa_location"]["url_for_pdf"]
            return None

        authors = extract_authors(unpaywall_data)
        data = {
            "title": unpaywall_data.get("title", ""),
            "version": VERSION,
            "source": "unpaywall",
            "authors": list(authors),
            "DOI": unpaywall_data.get("doi", ""),
            "publisher": unpaywall_data.get("publisher", ""),
            "published_date": unpaywall_data.get("published_date", ""),
            "pdf_links": {}
        }
        obj = cls(data)
        if fetch_url:
            obj.mark_fetch_reachable(fetch_url)
            pdf_link = extract_pdf_link(unpaywall_data)
            if pdf_link:
                obj.add_pdf_link(fetch_url, pdf_link)
        return obj

    @classmethod
    def from_crossref_json(cls, crossref_json, fetch_url=None):
        """
        Create a ArticleDataObject instance from a Crossref JSON response.

        :param crossref_json: A Crossref JSON response representing the data.
        :param fetch_url: The URL the response was fetched from, used to key pdf_links.
        :return: An instance of ArticleDataObject.
        """
        crossref_data = crossref_json.get("message", {})
        def extract_authors(data):
            def filter_author(author):
                if author.get("given") and author.get("family"):
                    return {
                        "given": author.get("given"),
                        "family": author.get("family")
                    }
                return None

            return [
                author for author in map(filter_author, data.get("author", [])) 
                if author is not None
        ]
        def convert_published_date(published_date):
            if published_date.get("date-parts"):
                try:
                    return f'{published_date["date-parts"][0][0]}-{published_date["date-parts"][0][1]}'
                except IndexError:
                    pass
            return ""
        def extract_pdf_link(data):
            """
            Get the PDF link from the Article data object.

            Accepts a link if Crossref reports it as content-type "application/pdf",
            or if "pdf" (case-insensitive) appears anywhere in the URL -- some
            publishers (e.g. MDPI) deposit PDF links with content-type "unspecified".

            :return: The PDF link if available, otherwise None.
            """
            for link in data["link"]:
                url = link.get("URL") or ""
                if link.get("content-type") == "application/pdf" or "pdf" in url.lower():
                    return url
            return None

        data = {
            "title": crossref_data.get("title", [])[0],
            "version": VERSION,
            "source": "crossref",
            "authors": extract_authors(crossref_data),
            "DOI": crossref_data.get("DOI", ""),
            "publisher": crossref_data.get("publisher", ""),
            "published_date": convert_published_date(crossref_data.get("published", {})),
            "pdf_links": {}
        }
        obj = cls(data)
        if fetch_url:
            obj.mark_fetch_reachable(fetch_url)
            pdf_link = extract_pdf_link(crossref_data)
            if pdf_link:
                obj.add_pdf_link(fetch_url, pdf_link)
        return obj

    @classmethod
    def from_json(cls, json_string, schema = schema):
        """
        Create a ArticleDataObject instance from a Article string.

        :param json_string: A Article string representing the data.
        :param schema: The Article schema for validation.
        :return: An instance of ArticleDataObject.
        """
        data = json.loads(json_string)
        return cls(data, schema)

