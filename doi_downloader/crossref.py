import requests
import json
from . import config
from . import pdf_download as pdf
from .cache import Cache

# Read API keys and other sensitive data from environment variables
CROSSREF_API_URL = "https://api.crossref.org/works/{doi}"


def fetch_metadata(doi):
    url = CROSSREF_API_URL.format(doi=doi)
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        data = response.json()
        if "message" in data:
            metadata = data["message"]
            pdf_link = None
            if "link" in metadata:
                for link in metadata["link"]:
                    if link.get("content-type") == "application/pdf":
                        pdf_link = link.get("URL")
                        break

            return {
                "title": metadata.get("title", ["Unknown"])[0],
                "authors": [
                    f"{author.get('given', '')} {author.get('family', '')}"
                    for author in metadata.get("author", [])
                ],
                "publisher": metadata.get("publisher", "Unknown"),
                "published_date": metadata.get("published-print", {}).get("date-parts", [["Unknown"]])[0],
                "journal": metadata.get("container-title", ["Unknown"])[0],
                "doi": metadata.get("DOI", "Unknown"),
                "pdf_link": pdf_link or "No PDF link available"
            }
        else:
            return {"error": "No metadata found for the given DOI."}
    except requests.exceptions.RequestException as e:
        return {"error": f"An error occurred: {e}"}


