import json
import jsonschema
from jsonschema import validate

schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://example.com/crossref-schema",
    "title": "Crossref Metadata Schema",
    "type": "object",
    "required": ["title", "DOI", "source", "pdf_links" ],
    "properties": {
                "title": {"type": "string" },
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
                    "type": "array",
                    "items": {
                        "type": "string",
                        "format": "uri"
                    }
                }
            }
        }

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
            "title": [],
            "source": "",
            "author": [],
            "DOI": "",
            "published_date": "",
            "pdf_links": []

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
        self.data["title"] = [title]

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

    def add_pdf_link(self, url):
        """
        Add a link to the Article data object.

        :param url: The URL of the link.
        :param content_type: The content type of the link.
        """
        self.data["pdf_links"].append(url)

    def get_pdf_link(self):
        """
        Get the PDF link from the Article data object.

        :return: The PDF link if available, otherwise None.
        """
        return self.data["pdf_links"][0] if self.data["pdf_links"] else None

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
    def from_unpaywall_json(cls, unpaywall_data):
        """
        Create a ArticleDataObject instance from an Unpaywall JSON response.

        :param unpaywall_data: An Unpaywall JSON response representing the data.
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
            if "best_oa_location" in data and data["best_oa_location"]:
                return data["best_oa_location"]["url_for_pdf"]
            return None

        authors = extract_authors(unpaywall_data)
        data = {
            "title": unpaywall_data.get("title", ""),
            "source": "unpaywall",
            "authors": list(authors),
            "DOI": unpaywall_data.get("doi", ""),
            "publisher": unpaywall_data.get("publisher", ""),
            "published_date": unpaywall_data.get("published_date", ""),
            "pdf_links": [extract_pdf_link(unpaywall_data)] if extract_pdf_link(unpaywall_data) else []
        }
        return cls(data)

    @classmethod
    def from_crossref_json(cls, crossref_json):
        """
        Create a ArticleDataObject instance from a Crossref JSON response.

        :param crossref_json: A Crossref JSON response representing the data.
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
                return f'{published_date["date-parts"][0][0]}-{published_date["date-parts"][0][1]}'
            return ""
        def extract_pdf_link(data):
            """
            Get the PDF link from the Article data object.

            :return: The PDF link if available, otherwise None.
            """
            for link in data["link"]:
                if link.get("content-type") == "application/pdf":
                    return link.get("URL")
            return None

        data = {
            "title": crossref_data.get("title", [])[0],
            "source": "crossref",
            "authors": extract_authors(crossref_data),
            "DOI": crossref_data.get("DOI", ""),
            "publisher": crossref_data.get("publisher", ""),
            "published_date": convert_published_date(crossref_data.get("published", {})),
            "pdf_links": [extract_pdf_link(crossref_data)] if extract_pdf_link(crossref_data) else []
        }

        return cls(data)

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

